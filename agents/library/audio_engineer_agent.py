"""Audio Engineer Agent - Processes and enhances podcast audio.

This agent provides audio cleanup, enhancement, and mastering capabilities
integrated with the agent framework for automated audio production.
"""

import os
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

from agents.base_agent import BaseAgent, AgentTool
from agents.robust_tool import RobustTool, ToolResult


class AudioEngineerAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        super().__init__(name, description, implementation=implementation)

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        raise NotImplementedError("Should not be called when implementation is provided")


class AudioEngineerAgent(BaseAgent):
    """Agent for audio processing, enhancement, and mastering."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the audio engineer agent."""
        super().__init__("audio_engineer", config_path)

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize audio engineering tools."""
        return {
            'audio_cleanup': AudioEngineerAgentTool(
                "audio_cleanup",
                "Remove background noise, hum, and unwanted artifacts",
                AudioCleanupTool()
            ),
            'voice_enhancement': AudioEngineerAgentTool(
                "voice_enhancement",
                "Enhance vocal clarity and presence",
                VoiceEnhancementTool()
            ),
            'sponsor_insertion': AudioEngineerAgentTool(
                "sponsor_insertion",
                "Insert sponsor reads at optimal points",
                SponsorInsertionTool()
            ),
            'audio_mastering': AudioEngineerAgentTool(
                "audio_mastering",
                "Master final audio for distribution",
                AudioMasteringTool()
            ),
            'normalize_audio': AudioEngineerAgentTool(
                "normalize_audio",
                "Normalize audio levels to target LUFS",
                AudioNormalizationTool()
            ),
            'extract_audio': AudioEngineerAgentTool(
                "extract_audio",
                "Extract audio track from video file",
                AudioExtractionTool()
            )
        }


class AudioCleanupTool(RobustTool):
    """Tool for cleaning up audio by removing noise and artifacts."""

    def __init__(self):
        super().__init__(
            name="audio_cleanup",
            description="Remove background noise, hum, and unwanted artifacts"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for audio cleanup."""
        return {
            'type': 'object',
            'required': ['input_audio'],
            'properties': {
                'input_audio': {
                    'type': 'string',
                    'description': 'Path to input audio file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output cleaned audio'
                },
                'noise_reduction_level': {
                    'type': 'string',
                    'enum': ['light', 'medium', 'aggressive'],
                    'default': 'medium',
                    'description': 'Level of noise reduction'
                },
                'remove_hum': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Remove electrical hum (50/60Hz)'
                },
                'de_ess': {
                    'type': 'boolean',
                    'default': False,
                    'description': 'Apply de-essing to reduce sibilance'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'reduce_noise_level',
                'condition': lambda e, p, eid: 'noise' in str(e).lower(),
                'action': self._fallback_reduce_noise,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Clean audio using ffmpeg filters."""
        input_audio = parameters['input_audio']
        output_audio = parameters.get('output_audio')
        noise_level = parameters.get('noise_reduction_level', 'medium')
        remove_hum = parameters.get('remove_hum', True)
        de_ess = parameters.get('de_ess', False)

        if not output_audio:
            base_name = Path(input_audio).stem
            output_audio = f"{base_name}_cleaned.wav"

        # Build ffmpeg filter complex based on parameters
        filters = []

        # Noise reduction based on level
        if noise_level == 'light':
            nr_amount = '0.3'
        elif noise_level == 'medium':
            nr_amount = '0.5'
        else:  # aggressive
            nr_amount = '0.8'

        filters.append(f"anlmdn=lr={nr_amount}:lm=0.01:sm=1")

        # Remove hum
        if remove_hum:
            filters.append("ahumeter=level=-40")

        # De-essing
        if de_ess:
            filters.append("deesser=i=1:m=0.3")

        # Apply high-pass filter to remove low-frequency rumble
        filters.append("highpass=f=80")

        # Apply low-pass filter to remove high-frequency hiss
        filters.append("lowpass=f=12000")

        # Join filters
        filter_complex = ','.join(filters) if filters else 'anull'

        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-af', filter_complex,
            '-c:a', 'pcm_s16le',
            '-ar', '48000',
            output_audio
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Audio cleanup failed: {result.stderr}")

        # Get output file info
        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'input_audio': input_audio,
            'output_audio': output_audio,
            'noise_reduction_level': noise_level,
            'remove_hum': remove_hum,
            'de_ess': de_ess,
            'output_size': output_size
        }

    def _fallback_reduce_noise(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to lighter noise reduction."""
        alt_params = parameters.copy()
        alt_params['noise_reduction_level'] = 'light'

        result = self._execute_core(alt_params, execution_id)
        return ToolResult(
            success=True,
            data=result,
            execution_id=execution_id,
            warnings=["Used lighter noise reduction due to processing issues"]
        )


class VoiceEnhancementTool(RobustTool):
    """Tool for enhancing vocal clarity and presence."""

    def __init__(self):
        super().__init__(
            name="voice_enhancement",
            description="Enhance vocal clarity and presence"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for voice enhancement."""
        return {
            'type': 'object',
            'required': ['input_audio'],
            'properties': {
                'input_audio': {
                    'type': 'string',
                    'description': 'Path to input audio file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output enhanced audio'
                },
                'preset': {
                    'type': 'string',
                    'enum': ['podcast', 'interview', 'narration'],
                    'default': 'podcast',
                    'description': 'Voice enhancement preset'
                },
                'boost_presence': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Boost presence frequencies (2-5kHz)'
                },
                'enhance_clarity': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Enhance clarity with dynamic EQ'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Enhance voice using audio processing filters."""
        input_audio = parameters['input_audio']
        output_audio = parameters.get('output_audio')
        preset = parameters.get('preset', 'podcast')
        boost_presence = parameters.get('boost_presence', True)
        enhance_clarity = parameters.get('enhance_clarity', True)

        if not output_audio:
            base_name = Path(input_audio).stem
            output_audio = f"{base_name}_enhanced.wav"

        # Build ffmpeg filter complex based on preset
        filters = []

        # Preset-based EQ settings
        if preset == 'podcast':
            # Boost presence, warm low-mids
            filters.append("equalizer=f=300:g=-2:w=100")  # Warm low-mids
            if boost_presence:
                filters.append("equalizer=f=3000:g=3:w=200")  # Presence boost
            if enhance_clarity:
                filters.append("dynamic_eq=threshold=-20:attack=0.1:release=0.3:ratio=2")  # Clarity
        elif preset == 'interview':
            # Natural sounding, reduce proximity effect
            filters.append("equalizer=f=150:g=-1:w=100")  # Reduce proximity
            if boost_presence:
                filters.append("equalizer=f=4000:g=2:w=150")
        elif preset == 'narration':
            # Clear, authoritative voice
            filters.append("equalizer=f=250:g=-1:w=80")
            if boost_presence:
                filters.append("equalizer=f=2500:g=4:w=100")

        # Add compression for consistent levels
        filters.append("acompressor=threshold=-20:ratio=4:attack=10:release=100")

        # Add slight limiting to prevent clipping
        filters.append("alimiter=level=0.95")

        # Join filters
        filter_complex = ','.join(filters) if filters else 'anull'

        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-af', filter_complex,
            '-c:a', 'pcm_s16le',
            '-ar', '48000',
            output_audio
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Voice enhancement failed: {result.stderr}")

        # Get output file info
        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'input_audio': input_audio,
            'output_audio': output_audio,
            'preset': preset,
            'boost_presence': boost_presence,
            'enhance_clarity': enhance_clarity,
            'output_size': output_size
        }


class SponsorInsertionTool(RobustTool):
    """Tool for inserting sponsor reads into audio."""

    def __init__(self):
        super().__init__(
            name="sponsor_insertion",
            description="Insert sponsor reads at optimal points"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for sponsor insertion."""
        return {
            'type': 'object',
            'required': ['main_audio', 'sponsor_audio'],
            'properties': {
                'main_audio': {
                    'type': 'string',
                    'description': 'Path to main audio file'
                },
                'sponsor_audio': {
                    'type': 'string',
                    'description': 'Path to sponsor read audio file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output combined audio'
                },
                'insertion_point': {
                    'type': 'number',
                    'description': 'Insertion point in seconds (optional, auto-detect if not provided)'
                },
                'transition_style': {
                    'type': 'string',
                    'enum': ['hard_cut', 'fade', 'crossfade'],
                    'default': 'fade',
                    'description': 'Transition style between segments'
                },
                'fade_duration': {
                    'type': 'number',
                    'default': 0.5,
                    'description': 'Fade duration in seconds'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Insert sponsor audio into main audio."""
        main_audio = parameters['main_audio']
        sponsor_audio = parameters['sponsor_audio']
        output_audio = parameters.get('output_audio')
        insertion_point = parameters.get('insertion_point')
        transition_style = parameters.get('transition_style', 'fade')
        fade_duration = parameters.get('fade_duration', 0.5)

        if not output_audio:
            base_name = Path(main_audio).stem
            output_audio = f"{base_name}_with_sponsor.wav"

        # Get sponsor audio duration
        sponsor_duration = self._get_audio_duration(sponsor_audio)

        # If no insertion point provided, use default (midpoint)
        if insertion_point is None:
            main_duration = self._get_audio_duration(main_audio)
            insertion_point = main_duration // 2

        # Build ffmpeg filter complex based on transition style
        if transition_style == 'hard_cut':
            # Simple concatenation
            cmd = [
                'ffmpeg', '-y',
                '-i', main_audio,
                '-i', sponsor_audio,
                '-filter_complex', f"[0:a]atrim=0:{insertion_point}[pre];[pre][1:a]concat=n=2:v=0:a=1[out]",
                '-map', '[out]',
                '-c:a', 'pcm_s16le',
                output_audio
            ]
        elif transition_style == 'fade':
            # Fade out main, fade in sponsor
            cmd = [
                'ffmpeg', '-y',
                '-i', main_audio,
                '-i', sponsor_audio,
                '-filter_complex', f"[0:a]atrim=0:{insertion_point},afade=t=out:d={fade_duration}[pre];[1:a]afade=t=in:d={fade_duration}[sponsor];[pre][sponsor]concat=n=2:v=0:a=1[out]",
                '-map', '[out]',
                '-c:a', 'pcm_s16le',
                output_audio
            ]
        else:  # crossfade
            # Crossfade between segments
            cmd = [
                'ffmpeg', '-y',
                '-i', main_audio,
                '-i', sponsor_audio,
                '-filter_complex', f"[0:a]atrim=0:{insertion_point}[pre];[1:a]atrim=0:{sponsor_duration}[sponsor];[pre][sponsor]acrossfade=d={fade_duration}[out]",
                '-map', '[out]',
                '-c:a', 'pcm_s16le',
                output_audio
            ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Sponsor insertion failed: {result.stderr}")

        # Get output file info
        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'main_audio': main_audio,
            'sponsor_audio': sponsor_audio,
            'output_audio': output_audio,
            'insertion_point': insertion_point,
            'transition_style': transition_style,
            'sponsor_duration': sponsor_duration,
            'output_size': output_size
        }

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return float(result.stdout.strip())
        except:
            return 0.0


class AudioMasteringTool(RobustTool):
    """Tool for mastering audio for distribution."""

    def __init__(self):
        super().__init__(
            name="audio_mastering",
            description="Master final audio for distribution"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for audio mastering."""
        return {
            'type': 'object',
            'required': ['input_audio'],
            'properties': {
                'input_audio': {
                    'type': 'string',
                    'description': 'Path to input audio file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output mastered audio'
                },
                'target_lufs': {
                    'type': 'number',
                    'default': -16,
                    'description': 'Target LUFS integrated loudness'
                },
                'platform': {
                    'type': 'string',
                    'enum': ['spotify', 'apple_podcasts', 'youtube', 'generic'],
                    'default': 'generic',
                    'description': 'Target platform for optimization'
                },
                'true_peak_limit': {
                    'type': 'number',
                    'default': -1.5,
                    'description': 'True peak limit in dBTP'
                },
                'add_loudness_metadata': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Add loudness metadata to file'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'use_generic_mastering',
                'condition': lambda e, p, eid: 'loudnorm' in str(e).lower(),
                'action': self._fallback_generic_mastering,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Master audio using loudness normalization."""
        input_audio = parameters['input_audio']
        output_audio = parameters.get('output_audio')
        target_lufs = parameters.get('target_lufs', -16)
        platform = parameters.get('platform', 'generic')
        true_peak = parameters.get('true_peak_limit', -1.5)
        add_metadata = parameters.get('add_loudness_metadata', True)

        if not output_audio:
            base_name = Path(input_audio).stem
            output_audio = f"{base_name}_mastered.wav"

        # Platform-specific target loudness
        platform_lufs = {
            'spotify': -14,
            'apple_podcasts': -16,
            'youtube': -14,
            'generic': target_lufs
        }

        target = platform_lufs.get(platform, target_lufs)

        # Build ffmpeg loudness normalization filter
        # Using ffmpeg's loudnorm filter (EBU R128)
        loudnorm_filter = (
            f"loudnorm=I={target}:TP={true_peak}:LRA=11:"
            f"print_format=summary"
        )

        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-af', loudnorm_filter,
            '-c:a', 'pcm_s16le',
            '-ar', '48000',
            output_audio
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Audio mastering failed: {result.stderr}")

        # Parse loudnorm output for stats
        loudness_stats = self._parse_loudnorm_stats(result.stderr)

        # Get output file info
        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'input_audio': input_audio,
            'output_audio': output_audio,
            'target_lufs': target,
            'platform': platform,
            'true_peak_limit': true_peak,
            'output_size': output_size,
            'loudness_stats': loudness_stats
        }

    def _fallback_generic_mastering(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to basic normalization without loudnorm."""
        input_audio = parameters['input_audio']
        output_audio = parameters.get('output_audio')

        if not output_audio:
            base_name = Path(input_audio).stem
            output_audio = f"{base_name}_normalized.wav"

        # Use basic volume normalization
        cmd = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-af', 'dynaudnorm=p=0.5',
            '-c:a', 'pcm_s16le',
            '-ar', '48000',
            output_audio
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            return ToolResult(
                success=False,
                error=f"Audio mastering failed: {result.stderr}",
                execution_id=execution_id
            )

        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return ToolResult(
            success=True,
            data={
                'input_audio': input_audio,
                'output_audio': output_audio,
                'target_lufs': -16,
                'platform': 'generic',
                'output_size': output_size,
                'loudness_stats': {'note': 'Basic normalization applied'},
                'warnings': ['Used fallback normalization - loudnorm filter not available']
            },
            execution_id=execution_id
        )

    def _parse_loudnorm_stats(self, stderr: str) -> Dict[str, Any]:
        """Parse loudnorm statistics from ffmpeg output."""
        stats = {}

        # Look for EBU R128 stats in output
        for line in stderr.split('\n'):
            if 'Input Integrated' in line:
                stats['input_loudness'] = line.split(':')[-1].strip()
            elif 'Input True Peak' in line:
                stats['input_peak'] = line.split(':')[-1].strip()
            elif 'Input LRA' in line:
                stats['input_lra'] = line.split(':')[-1].strip()
            elif 'Output Integrated' in line:
                stats['output_loudness'] = line.split(':')[-1].strip()
            elif 'Output True Peak' in line:
                stats['output_peak'] = line.split(':')[-1].strip()
            elif 'Output LRA' in line:
                stats['output_lra'] = line.split(':')[-1].strip()

        return stats


class AudioNormalizationTool(RobustTool):
    """Tool for normalizing audio levels."""

    def __init__(self):
        super().__init__(
            name="normalize_audio",
            description="Normalize audio levels to target LUFS"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for normalization."""
        return {
            'type': 'object',
            'required': ['input_audio'],
            'properties': {
                'input_audio': {
                    'type': 'string',
                    'description': 'Path to input audio file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output normalized audio'
                },
                'target_db': {
                    'type': 'number',
                    'default': -3,
                    'description': 'Target peak level in dB'
                },
                'normalize_to': {
                    'type': 'string',
                    'enum': ['peak', 'rms'],
                    'default': 'peak',
                    'description': 'Normalization type'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Normalize audio levels."""
        input_audio = parameters['input_audio']
        output_audio = parameters.get('output_audio')
        target_db = parameters.get('target_db', -3)
        normalize_to = parameters.get('normalize_to', 'peak')

        if not output_audio:
            base_name = Path(input_audio).stem
            output_audio = f"{base_name}_normalized.wav"

        # Build ffmpeg command
        if normalize_to == 'peak':
            # Peak normalization
            gain_filter = f"volume={target_db}dB"
        else:
            # RMS normalization (using loudnorm for better results)
            gain_filter = f"loudnorm=I={target_db + 14}:TP=-2:LRA=7"

        cmd = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-af', gain_filter,
            '-c:a', 'pcm_s16le',
            '-ar', '48000',
            output_audio
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Audio normalization failed: {result.stderr}")

        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'input_audio': input_audio,
            'output_audio': output_audio,
            'target_db': target_db,
            'normalize_to': normalize_to,
            'output_size': output_size
        }


class AudioExtractionTool(RobustTool):
    """Tool for extracting audio from video files."""

    def __init__(self):
        super().__init__(
            name="extract_audio",
            description="Extract audio track from video file"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for audio extraction."""
        return {
            'type': 'object',
            'required': ['input_video'],
            'properties': {
                'input_video': {
                    'type': 'string',
                    'description': 'Path to input video file'
                },
                'output_audio': {
                    'type': 'string',
                    'description': 'Path for output audio file'
                },
                'format': {
                    'type': 'string',
                    'enum': ['mp3', 'wav', 'aac', 'flac'],
                    'default': 'wav',
                    'description': 'Output audio format'
                },
                'bitrate': {
                    'type': 'string',
                    'default': '320k',
                    'description': 'Audio bitrate (for compressed formats)'
                },
                'sample_rate': {
                    'type': 'integer',
                    'default': 48000,
                    'description': 'Sample rate in Hz'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Extract audio from video."""
        input_video = parameters['input_video']
        output_audio = parameters.get('output_audio')
        format_type = parameters.get('format', 'wav')
        bitrate = parameters.get('bitrate', '320k')
        sample_rate = parameters.get('sample_rate', 48000)

        if not output_audio:
            base_name = Path(input_video).stem
            output_audio = f"{base_name}_audio.{format_type}"

        # Get codec based on format
        codec_map = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac'
        }
        codec = codec_map.get(format_type, 'libmp3lame')

        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-i', input_video,
            '-vn',  # No video
            '-acodec', codec,
            '-ar', str(sample_rate),
            '-ab', bitrate if format_type != 'wav' else None,
            output_audio
        ]

        # Remove None values from command
        cmd = [c for c in cmd if c is not None]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"Audio extraction failed: {result.stderr}")

        output_size = os.path.getsize(output_audio) if os.path.exists(output_audio) else 0

        return {
            'input_video': input_video,
            'output_audio': output_audio,
            'format': format_type,
            'bitrate': bitrate,
            'sample_rate': sample_rate,
            'output_size': output_size
        }
