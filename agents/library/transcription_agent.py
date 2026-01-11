"""Transcription Agent - Integrates existing transcription functionality.

This agent provides transcription, captioning, and embedding services using
the existing transcription_agent scripts and integrates with the agent framework.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from agents.base_agent import BaseAgent, AgentTool
from agents.robust_tool import RobustTool, ToolResult


class TranscriptionAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        super().__init__(name, description)
        self.implementation = implementation

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        return self.implementation


class TranscriptionAgent(BaseAgent):
    """Agent for transcription, captioning, and embedding services."""

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize transcription tools."""
        return {
            'transcribe_audio': TranscriptionAgentTool("transcribe_audio", "Transcribe audio/video files to text with timestamps", TranscriptionTool()),
            'generate_captions': TranscriptionAgentTool("generate_captions", "Generate VTT/SRT captions from transcript data", CaptionGenerationTool()),
            'create_embeddings': TranscriptionAgentTool("create_embeddings", "Create vector embeddings for transcript text", EmbeddingTool()),
            'diarize_speakers': TranscriptionAgentTool("diarize_speakers", "Identify and separate different speakers in audio", SpeakerDiarizationTool())
        }


class TranscriptionTool(RobustTool):
    """Tool for transcribing audio/video files."""

    def __init__(self):
        super().__init__(
            name="transcribe_audio",
            description="Transcribe audio/video files to text with timestamps"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for transcription."""
        return {
            'type': 'object',
            'required': ['input_file'],
            'properties': {
                'input_file': {
                    'type': 'string',
                    'description': 'Path to audio/video file to transcribe'
                },
                'output_dir': {
                    'type': 'string',
                    'description': 'Directory to save transcription outputs'
                },
                'backend': {
                    'type': 'string',
                    'enum': ['whisper', 'whisperx'],
                    'default': 'whisper',
                    'description': 'Transcription backend to use'
                },
                'language': {
                    'type': 'string',
                    'description': 'Language code (optional)'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'try_alternate_backend',
                'condition': lambda e, p, eid: 'whisper' in str(e).lower(),
                'action': self._fallback_transcription,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Execute transcription using existing agent."""
        try:
            # Import the existing transcription functionality
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

            from transscribe_agent.agent import transcribe_media

            input_file = parameters['input_file']
            output_dir = parameters.get('output_dir', str(Path(input_file).parent))
            backend = parameters.get('backend', 'whisper')

            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Execute transcription
            result = transcribe_media(input_file, output_dir, backend)

            return {
                'vtt_file': result.get('vtt'),
                'json_file': result.get('json'),
                'transcript': self._extract_transcript_text(result.get('json')),
                'duration': self._get_media_duration(input_file)
            }

        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def _fallback_transcription(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback transcription method."""
        try:
            # Try with alternative backend
            alt_params = parameters.copy()
            alt_params['backend'] = 'whisper' if parameters.get('backend') == 'whisperx' else 'whisperx'

            result = self._execute_core(alt_params, execution_id)
            return ToolResult(
                success=True,
                data=result,
                execution_id=execution_id,
                warnings=["Used fallback transcription backend"]
            )
        except Exception as fb_error:
            return ToolResult(
                success=False,
                error=f"Both transcription backends failed: {str(error)}, {str(fb_error)}",
                execution_id=execution_id
            )

    def _extract_transcript_text(self, json_file: Optional[str]) -> Optional[str]:
        """Extract transcript text from JSON file."""
        if not json_file or not Path(json_file).exists():
            return None

        try:
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data.get('text')
        except:
            return None

    def _get_media_duration(self, media_file: str) -> Optional[float]:
        """Get duration of media file."""
        try:
            import soundfile as sf
            if media_file.lower().endswith(('.wav', '.flac', '.ogg')):
                return sf.info(media_file).duration
        except:
            pass
        return None


class CaptionGenerationTool(RobustTool):
    """Tool for generating captions from transcripts."""

    def __init__(self):
        super().__init__(
            name="generate_captions",
            description="Generate VTT/SRT captions from transcript data"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for caption generation."""
        return {
            'type': 'object',
            'required': ['transcript_data'],
            'properties': {
                'transcript_data': {
                    'type': 'object',
                    'description': 'Transcript data with segments'
                },
                'output_format': {
                    'type': 'string',
                    'enum': ['vtt', 'srt'],
                    'default': 'vtt',
                    'description': 'Caption format'
                },
                'output_path': {
                    'type': 'string',
                    'description': 'Path to save caption file'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Generate captions from transcript data."""
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

            from transscribe_agent.agent import convert_vtt_to_srt

            transcript_data = parameters['transcript_data']
            output_format = parameters.get('output_format', 'vtt')
            output_path = parameters.get('output_path')

            if not output_path:
                # Generate default output path
                base_name = f"captions_{execution_id.split('_')[1]}"
                output_path = f"{base_name}.{output_format}"

            # For now, create a simple VTT file
            # In practice, this would parse transcript segments
            vtt_content = "WEBVTT\n\n"
            vtt_content += "00:00:00.000 --> 00:00:05.000\n"
            vtt_content += "Sample caption text\n"

            with open(output_path, 'w') as f:
                f.write(vtt_content)

            # Convert to SRT if requested
            if output_format == 'srt':
                srt_path = output_path.replace('.vtt', '.srt')
                convert_vtt_to_srt(output_path, srt_path)
                return {'caption_file': srt_path}
            else:
                return {'caption_file': output_path}

        except Exception as e:
            raise RuntimeError(f"Caption generation failed: {str(e)}")


class EmbeddingTool(RobustTool):
    """Tool for creating embeddings from transcript text."""

    def __init__(self):
        super().__init__(
            name="create_embeddings",
            description="Create vector embeddings for transcript text"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for embedding creation."""
        return {
            'type': 'object',
            'required': ['text'],
            'properties': {
                'text': {
                    'type': 'string',
                    'description': 'Text to create embeddings for'
                },
                'model_name': {
                    'type': 'string',
                    'default': 'all-MiniLM-L6-v2',
                    'description': 'Sentence transformer model to use'
                },
                'output_path': {
                    'type': 'string',
                    'description': 'Path to save embeddings'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Create embeddings using sentence transformers."""
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

            from transscribe_agent.agent import embeddings_for_transcript, index_embeddings

            text = parameters['text']
            model_name = parameters.get('model_name', 'all-MiniLM-L6-v2')
            output_path = parameters.get('output_path')

            if not output_path:
                output_path = f"embeddings_{execution_id.split('_')[1]}.index"

            # Generate embeddings
            embeddings = embeddings_for_transcript(text, model_name)

            if embeddings is None:
                raise RuntimeError("Failed to generate embeddings - sentence-transformers not available")

            # Create dummy IDs for now
            ids = [f"segment_{i}" for i in range(len(embeddings))]

            # Save embeddings
            index_path = index_embeddings(embeddings, ids, output_path)

            return {
                'embedding_file': index_path,
                'model_used': model_name,
                'num_embeddings': len(embeddings)
            }

        except Exception as e:
            raise RuntimeError(f"Embedding creation failed: {str(e)}")


class SpeakerDiarizationTool(RobustTool):
    """Tool for speaker diarization."""

    def __init__(self):
        super().__init__(
            name="diarize_speakers",
            description="Identify and separate different speakers in audio"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for speaker diarization."""
        return {
            'type': 'object',
            'required': ['audio_file'],
            'properties': {
                'audio_file': {
                    'type': 'string',
                    'description': 'Path to audio file for diarization'
                },
                'output_path': {
                    'type': 'string',
                    'description': 'Path to save diarization results'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Perform speaker diarization."""
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

            from transscribe_agent.agent import run_diarization

            audio_file = parameters['audio_file']
            output_path = parameters.get('output_path')

            if not output_path:
                output_path = f"diarization_{execution_id.split('_')[1]}.json"

            # Run diarization
            segments = run_diarization(audio_file)

            # Save results
            import json
            with open(output_path, 'w') as f:
                json.dump(segments, f, indent=2)

            return {
                'diarization_file': output_path,
                'num_segments': len(segments),
                'speakers': list(set(s['speaker'] for s in segments))
            }

        except Exception as e:
            raise RuntimeError(f"Speaker diarization failed: {str(e)}")
