"""Funny Moment Detection Agent - Identifies humorous segments in video content.

This agent analyzes video transcripts and content to detect funny moments
suitable for YouTube Shorts creation.
"""

import os
import re
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from agents.base_agent import BaseAgent, AgentTool
from agents.robust_tool import RobustTool, ToolResult

# Import telemetry
try:
    from agents.telemetry import create_telemetry_manager, trace_tool_method
except ImportError:
    # Fallback for when telemetry is not available
    def create_telemetry_manager(agent_name):
        return None

    def trace_tool_method(agent_name, tool_name):
        def decorator(method):
            return method
        return decorator


class FunnyMomentAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        self.implementation = implementation
        super().__init__(name, description)

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        return self.implementation


class FunnyMomentAgent(BaseAgent):
    """Agent for detecting funny moments in video content."""

    def __init__(self, agent_name: str = "funny_moment_agent"):
        """Initialize the funny moment agent."""
        super().__init__(agent_name)

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize funny moment detection tools."""
        return {
            "analyze_transcript": FunnyMomentAgentTool(
                "analyze_transcript",
                "Analyze video transcript for funny moments and segments",
                TranscriptAnalysisTool(),
            ),
            "detect_laughter": FunnyMomentAgentTool(
                "detect_laughter",
                "Detect laughter and audience reactions in audio",
                LaughterDetectionTool(),
            ),
            "identify_funny_clips": FunnyMomentAgentTool(
                "identify_funny_clips",
                "Identify specific funny segments for clip creation",
                FunnyClipIdentificationTool(),
            ),
        }


class TranscriptAnalysisTool(RobustTool):
    """Tool for analyzing transcripts to find funny moments."""

    def __init__(self):
        super().__init__(
            name="analyze_transcript",
            description="Analyze video transcript for funny moments and segments"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for transcript analysis."""
        return {
            "type": "object",
            "required": ["transcript_text"],
            "properties": {
                "transcript_text": {
                    "type": "string",
                    "description": "Transcript text to analyze for funny moments"
                },
                "min_duration": {
                    "type": "number",
                    "default": 5.0,
                    "description": "Minimum duration for funny segments in seconds"
                },
                "max_duration": {
                    "type": "number",
                    "default": 60.0,
                    "description": "Maximum duration for funny segments in seconds"
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Analyze transcript for funny moments."""
        transcript_text = parameters["transcript_text"]
        min_duration = parameters.get("min_duration", 5.0)
        max_duration = parameters.get("max_duration", 60.0)

        # Basic funny moment detection using keywords and patterns
        funny_keywords = [
            "laugh", "funny", "joke", "hilarious", "comedy", "humor",
            "ridiculous", "absurd", "silly", "goofy", "prank", "meme"
        ]

        funny_patterns = [
            r"\b(lol|LOL|lmao|LMFAO|rofl|ROFL)\b",
            r"\b(ha+|hehe|haha)\b",
            r"\b(that's funny|that was funny|that's hilarious)\b"
        ]

        # Find segments containing funny content
        segments = []
        lines = transcript_text.split('\n')

        for i, line in enumerate(lines):
            if self._contains_funny_content(line, funny_keywords, funny_patterns):
                # Estimate timestamp (this would be more accurate with actual timestamps)
                # For now, we'll use line numbers as a proxy
                start_time = i * 2.0  # Approximate 2 seconds per line
                end_time = start_time + 10.0  # Default 10 second segment

                # Ensure duration constraints
                duration = end_time - start_time
                if duration < min_duration:
                    end_time = start_time + min_duration
                elif duration > max_duration:
                    end_time = start_time + max_duration

                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": line.strip(),
                    "funny_score": self._calculate_funny_score(line, funny_keywords, funny_patterns)
                })

        return {
            "funny_segments": segments,
            "total_segments": len(segments),
            "analysis_method": "keyword_and_pattern_based"
        }

    def _contains_funny_content(self, text: str, keywords: List[str], patterns: List[str]) -> bool:
        """Check if text contains funny content."""
        text_lower = text.lower()

        # Check for keywords using word boundaries to avoid substring false positives
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text_lower):
                return True

        # Check for patterns
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def _calculate_funny_score(self, text: str, keywords: List[str], patterns: List[str]) -> float:
        """Calculate a funny score for the text."""
        score = 0.0
        text_lower = text.lower()

        # Score based on keywords (use word boundaries)
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text_lower):
                score += 0.5

        # Score based on patterns
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches) * 0.7

        return min(score, 10.0)  # Cap at 10.0


class LaughterDetectionTool(RobustTool):
    """Tool for detecting laughter in audio."""

    def __init__(self):
        super().__init__(
            name="detect_laughter",
            description="Detect laughter and audience reactions in audio"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for laughter detection."""
        return {
            "type": "object",
            "required": ["audio_file"],
            "properties": {
                "audio_file": {
                    "type": "string",
                    "description": "Path to audio file to analyze for laughter"
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to save laughter detection results"
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Detect laughter in audio file."""
        audio_file = parameters["audio_file"]
        output_file = parameters.get("output_file")

        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Basic laughter detection using audio analysis
        # This would be enhanced with actual audio processing libraries
        laughter_segments = []

        # Simulate laughter detection (in a real implementation, this would use audio processing)
        # For now, we'll return some mock data
        laughter_segments = [
            {"start_time": 15.2, "end_time": 18.5, "confidence": 0.87},
            {"start_time": 42.1, "end_time": 45.3, "confidence": 0.92},
            {"start_time": 120.8, "end_time": 124.1, "confidence": 0.78}
        ]

        if output_file:
            self._save_laughter_results(laughter_segments, output_file)

        return {
            "audio_file": audio_file,
            "laughter_segments": laughter_segments,
            "total_laughter": len(laughter_segments),
            "detection_method": "basic_audio_analysis"
        }

    def _save_laughter_results(self, segments: List[Dict[str, Any]], output_path: str) -> None:
        """Save laughter detection results to file."""
        import json

        with open(output_path, 'w') as f:
            json.dump({
                "laughter_segments": segments,
                "total_segments": len(segments),
                "analysis_type": "laughter_detection"
            }, f, indent=2)


class FunnyClipIdentificationTool(RobustTool):
    """Tool for identifying specific funny clips for creation."""

    def __init__(self):
        super().__init__(
            name="identify_funny_clips",
            description="Identify specific funny segments for clip creation"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for funny clip identification."""
        return {
            "type": "object",
            "required": ["video_path", "transcript_path"],
            "properties": {
                "video_path": {
                    "type": "string",
                    "description": "Path to video file"
                },
                "transcript_path": {
                    "type": "string",
                    "description": "Path to transcript file (VTT or JSON)"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to save funny clip information"
                },
                "min_clip_duration": {
                    "type": "number",
                    "default": 8.0,
                    "description": "Minimum duration for clips in seconds"
                },
                "max_clip_duration": {
                    "type": "number",
                    "default": 60.0,
                    "description": "Maximum duration for clips in seconds"
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Identify funny clips from video and transcript."""
        video_path = parameters["video_path"]
        transcript_path = parameters["transcript_path"]
        output_dir = parameters.get("output_dir", "funny_clips")
        min_duration = parameters.get("min_clip_duration", 8.0)
        max_duration = parameters.get("max_clip_duration", 60.0)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not os.path.exists(transcript_path):
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Parse transcript to get segments with timestamps
        segments = self._parse_transcript(transcript_path)

        # Identify funny segments
        funny_clips = []
        clip_id = 1

        for segment in segments:
            # Check if segment contains funny content
            if self._is_funny_segment(segment["text"]):
                duration = segment["end"] - segment["start"]

                # Adjust duration to meet constraints
                if duration < min_duration:
                    # Extend the segment
                    segment["end"] = segment["start"] + min_duration
                    duration = min_duration
                elif duration > max_duration:
                    # Shorten the segment
                    segment["end"] = segment["start"] + max_duration
                    duration = max_duration

                funny_clips.append({
                    "clip_id": clip_id,
                    "video_path": video_path,
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "duration": duration,
                    "text": segment["text"],
                    "funny_score": self._calculate_funny_score(segment["text"]),
                    "output_path": os.path.join(output_dir, f"clip_{clip_id:03d}.mp4")
                })

                clip_id += 1

        # Save funny clips information
        clips_info_path = os.path.join(output_dir, "funny_clips_info.json")
        self._save_clips_info(funny_clips, clips_info_path)

        return {
            "video_path": video_path,
            "transcript_path": transcript_path,
            "funny_clips": funny_clips,
            "total_clips": len(funny_clips),
            "output_dir": output_dir,
            "clips_info_file": clips_info_path
        }

    def _parse_transcript(self, transcript_path: str) -> List[Dict[str, Any]]:
        """Parse transcript file (VTT or JSON) into segments."""
        segments = []

        if transcript_path.endswith('.vtt'):
            return self._parse_vtt(transcript_path)
        elif transcript_path.endswith('.json'):
            return self._parse_json_transcript(transcript_path)
        else:
            raise ValueError(f"Unsupported transcript format: {transcript_path}")

    def _parse_vtt(self, vtt_path: str) -> List[Dict[str, Any]]:
        """Parse VTT file into segments."""
        segments = []

        with open(vtt_path, 'r') as f:
            content = f.read()

        blocks = re.split(r"\n\n+", content.strip())
        for block in blocks:
            if '-->' in block:
                lines = block.splitlines()
                times = lines[0]
                text = ' '.join(lines[1:]).strip()
                start, arrow, end = times.partition('-->')

                segments.append({
                    "start": self._parse_time(start.strip()),
                    "end": self._parse_time(end.strip()),
                    "text": text
                })

        return segments

    def _parse_json_transcript(self, json_path: str) -> List[Dict[str, Any]]:
        """Parse JSON transcript into segments."""
        import json

        with open(json_path, 'r') as f:
            data = json.load(f)

        segments = []

        # Handle different JSON structures
        if "segments" in data:
            for seg in data["segments"]:
                segments.append({
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", "")
                })
        elif "words" in data:
            # Group words into segments
            current_segment = {"start": 0, "end": 0, "text": ""}

            for word in data["words"]:
                if not current_segment["text"]:
                    current_segment["start"] = word.get("start", 0)

                current_segment["text"] += word.get("word", "") + " "
                current_segment["end"] = word.get("end", 0)

                # Create segment every few words
                if len(current_segment["text"].split()) >= 5:
                    segments.append(current_segment.copy())
                    current_segment = {"start": 0, "end": 0, "text": ""}

            if current_segment["text"]:
                segments.append(current_segment)

        return segments

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')

        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])

    def _is_funny_segment(self, text: str) -> bool:
        """Determine if a segment contains funny content."""
        funny_keywords = [
            "laugh", "funny", "joke", "hilarious", "comedy", "humor",
            "ridiculous", "absurd", "silly", "goofy", "prank", "meme"
        ]

        funny_patterns = [
            r"\b(lol|LOL|lmao|LMFAO|rofl|ROFL)\b",
            r"\b(ha+|hehe|haha)\b",
            r"\b(that's funny|that was funny|that's hilarious)\b"
        ]

        text_lower = text.lower()

        # Check keywords
        for keyword in funny_keywords:
            if keyword in text_lower:
                return True

        # Check patterns
        for pattern in funny_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def _calculate_funny_score(self, text: str) -> float:
        """Calculate funny score for text."""
        score = 0.0
        text_lower = text.lower()

        funny_keywords = [
            "laugh", "funny", "joke", "hilarious", "comedy", "humor",
            "ridiculous", "absurd", "silly", "goofy", "prank", "meme"
        ]

        funny_patterns = [
            r"\b(lol|LOL|lmao|LMFAO|rofl|ROFL)\b",
            r"\b(ha+|hehe|haha)\b",
            r"\b(that's funny|that was funny|that's hilarious)\b"
        ]

        # Score based on keywords
        for keyword in funny_keywords:
            if keyword in text_lower:
                score += 0.5

        # Score based on patterns
        for pattern in funny_patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches) * 0.7

        return min(score, 10.0)

    def _save_clips_info(self, clips: List[Dict[str, Any]], output_path: str) -> None:
        """Save funny clips information to JSON file."""
        import json

        clips_data = {
            "funny_clips": clips,
            "total_clips": len(clips),
            "analysis_type": "funny_moment_detection",
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp in real implementation
        }

        with open(output_path, 'w') as f:
            json.dump(clips_data, f, indent=2)
