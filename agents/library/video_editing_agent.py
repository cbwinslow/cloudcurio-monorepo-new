"""Video Editing Agent - Downloads and edits video content.

This agent provides video download, analysis, and editing capabilities
integrated with the agent framework for automated video production.
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import cv2
except ImportError:
    cv2 = None

from agents.base_agent import BaseAgent, AgentTool
from agents.robust_tool import RobustTool, ToolResult


class VideoEditingAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        super().__init__(name, description)
        self.implementation = implementation

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        return self.implementation


class VideoEditingAgent(BaseAgent):
    """Agent for video downloading, analysis, and editing."""

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize video editing tools."""
        return {
            "download_video": VideoEditingAgentTool(
                "download_video",
                "Download videos from YouTube, Facebook, and other platforms",
                VideoDownloadTool(),
            ),
            "analyze_video": VideoEditingAgentTool(
                "analyze_video",
                "Analyze video for duration, resolution, and basic content info",
                VideoAnalysisTool(),
            ),
            "trim_video": VideoEditingAgentTool(
                "trim_video",
                "Trim video to specified start and end times",
                VideoTrimTool(),
            ),
            "add_watermark": VideoEditingAgentTool(
                "add_watermark",
                "Add text or image watermark to video",
                VideoWatermarkTool(),
            ),
            "extract_audio": VideoEditingAgentTool(
                "extract_audio",
                "Extract audio track from video file",
                AudioExtractionTool(),
            ),
        }


class VideoDownloadTool(RobustTool):
    """Tool for downloading videos from YouTube, Facebook, etc."""

    def __init__(self):
        super().__init__(
            name="download_video",
            description="Download videos from YouTube, Facebook, and other platforms",
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for video download."""
        return {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "Video URL to download"},
                "output_path": {
                    "type": "string",
                    "description": "Path to save downloaded video",
                },
                "quality": {
                    "type": "string",
                    "enum": ["best", "worst", "1080p", "720p", "480p"],
                    "default": "best",
                    "description": "Video quality to download",
                },
                "format": {
                    "type": "string",
                    "enum": ["mp4", "webm", "mkv"],
                    "default": "mp4",
                    "description": "Output video format",
                },
            },
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                "name": "lower_quality",
                "condition": lambda e, p, eid: "quality" in str(e).lower(),
                "action": self._fallback_lower_quality,
                "priority": 1,
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Download video from URL."""
        try:
            import yt_dlp
        except ImportError:
            raise RuntimeError("yt-dlp not installed. Install with: pip install yt-dlp")

        url = parameters["url"]
        output_path = parameters.get("output_path")
        quality = parameters.get("quality", "best")
        format_type = parameters.get("format", "mp4")

        # Generate output path if not provided
        if not output_path:
            # Extract video ID or use execution ID
            video_id = self._extract_video_id(url)
            output_path = f"video_{video_id or execution_id}.{format_type}"

        # Setup yt-dlp options
        ydl_opts = {
            "outtmpl": output_path,
            "format": self._get_format_string(quality, format_type),
            "quiet": True,
            "no_warnings": True,
        }

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Get file info
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        return {
            "video_path": output_path,
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "file_size": file_size,
            "quality": quality,
            "format": format_type,
            "url": url,
        }

    def _fallback_lower_quality(
        self, error: Exception, parameters: Dict[str, Any], execution_id: str
    ) -> ToolResult:
        """Fallback to lower quality download."""
        alt_params = parameters.copy()
        quality_order = ["best", "1080p", "720p", "480p", "worst"]

        current_quality = parameters.get("quality", "best")
        if current_quality in quality_order:
            current_index = quality_order.index(current_quality)
            if current_index < len(quality_order) - 1:
                alt_params["quality"] = quality_order[current_index + 1]

        result = self._execute_core(alt_params, execution_id)
        return ToolResult(
            success=True,
            data=result,
            execution_id=execution_id,
            warnings=[f"Downloaded at lower quality: {alt_params['quality']}"],
        )

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL."""
        # YouTube patterns
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
            r"facebook\.com\/.*\/videos\/(\d+)",
            r"vimeo\.com\/(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_format_string(self, quality: str, format_type: str) -> str:
        """Get yt-dlp format string."""
        if quality == "best":
            return f"best[ext={format_type}]/best"
        elif quality == "worst":
            return f"worst[ext={format_type}]/worst"
        elif quality == "1080p":
            return f"best[height<=1080][ext={format_type}]/best[height<=1080]"
        elif quality == "720p":
            return f"best[height<=720][ext={format_type}]/best[height<=720]"
        elif quality == "480p":
            return f"best[height<=480][ext={format_type}]/best[height<=480]"
        else:
            return f"best[ext={format_type}]/best"


class VideoAnalysisTool(RobustTool):
    """Tool for analyzing video content."""

    def __init__(self):
        super().__init__(
            name="analyze_video",
            description="Analyze video for duration, resolution, and basic content info",
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for video analysis."""
        return {
            "type": "object",
            "required": ["video_path"],
            "properties": {
                "video_path": {
                    "type": "string",
                    "description": "Path to video file to analyze",
                }
            },
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Analyze video file."""
        video_path = parameters["video_path"]

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            import cv2
        except ImportError:
            # Fallback to ffprobe if OpenCV not available
            return self._analyze_with_ffprobe(video_path)

        # Analyze with OpenCV
        if cv2 is None:
            return self._analyze_with_ffprobe(video_path)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise RuntimeError(f"Could not open video file: {video_path}")

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        # Get file size
        file_size = os.path.getsize(video_path)

        cap.release()

        return {
            "video_path": video_path,
            "duration": duration,
            "fps": fps,
            "frame_count": frame_count,
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "file_size": file_size,
            "file_size_mb": file_size / (1024 * 1024),
        }

    def _analyze_with_ffprobe(self, video_path: str) -> Dict[str, Any]:
        """Fallback analysis using ffprobe."""
        import subprocess
        import json

        try:
            # Run ffprobe to get video info
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise RuntimeError(f"ffprobe failed: {result.stderr}")

            data = json.loads(result.stdout)

            # Extract video stream info
            video_stream = None
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                    break

            if not video_stream:
                raise RuntimeError("No video stream found")

            # Extract format info
            format_info = data.get("format", {})

            return {
                "video_path": video_path,
                "duration": float(format_info.get("duration", 0)),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                "frame_count": 0,  # Not easily available from ffprobe
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "file_size": int(format_info.get("size", 0)),
                "file_size_mb": int(format_info.get("size", 0)) / (1024 * 1024),
                "codec": video_stream.get("codec_name"),
                "bitrate": format_info.get("bit_rate"),
            }

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Basic fallback
            file_size = os.path.getsize(video_path)
            return {
                "video_path": video_path,
                "duration": 0,
                "fps": 0,
                "frame_count": 0,
                "resolution": "unknown",
                "width": 0,
                "height": 0,
                "file_size": file_size,
                "file_size_mb": file_size / (1024 * 1024),
                "note": "Basic analysis only - install ffprobe or OpenCV for full analysis",
            }


class VideoTrimTool(RobustTool):
    """Tool for trimming video clips."""

    def __init__(self):
        super().__init__(
            name="trim_video", description="Trim video to specified start and end times"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for video trimming."""
        return {
            "type": "object",
            "required": ["input_video", "start_time", "end_time"],
            "properties": {
                "input_video": {
                    "type": "string",
                    "description": "Path to input video file",
                },
                "output_video": {
                    "type": "string",
                    "description": "Path for output trimmed video",
                },
                "start_time": {
                    "type": "number",
                    "description": "Start time in seconds",
                    "minimum": 0,
                },
                "end_time": {
                    "type": "number",
                    "description": "End time in seconds",
                    "minimum": 0,
                },
            },
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Trim video using ffmpeg."""
        import subprocess

        input_video = parameters["input_video"]
        start_time = parameters["start_time"]
        end_time = parameters["end_time"]
        output_video = parameters.get("output_video")

        if not output_video:
            base_name = Path(input_video).stem
            output_video = f"{base_name}_trimmed_{start_time:.1f}-{end_time:.1f}.mp4"

        duration = end_time - start_time

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-i",
            input_video,  # Input file
            "-ss",
            str(start_time),  # Start time
            "-t",
            str(duration),  # Duration
            "-c",
            "copy",  # Copy streams (fast)
            output_video,
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg trim failed: {result.stderr}")

        # Get output file info
        output_size = (
            os.path.getsize(output_video) if os.path.exists(output_video) else 0
        )

        return {
            "input_video": input_video,
            "output_video": output_video,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "output_size": output_size,
        }


class VideoWatermarkTool(RobustTool):
    """Tool for adding watermarks to videos."""

    def __init__(self):
        super().__init__(
            name="add_watermark", description="Add text or image watermark to video"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for watermarking."""
        return {
            "type": "object",
            "required": ["input_video", "watermark_text"],
            "properties": {
                "input_video": {
                    "type": "string",
                    "description": "Path to input video file",
                },
                "output_video": {
                    "type": "string",
                    "description": "Path for output watermarked video",
                },
                "watermark_text": {
                    "type": "string",
                    "description": "Text to add as watermark",
                },
                "position": {
                    "type": "string",
                    "enum": [
                        "top_left",
                        "top_right",
                        "bottom_left",
                        "bottom_right",
                        "center",
                    ],
                    "default": "bottom_right",
                    "description": "Watermark position",
                },
                "font_size": {
                    "type": "integer",
                    "default": 24,
                    "description": "Font size for text watermark",
                },
            },
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Add watermark to video using ffmpeg."""
        import subprocess

        input_video = parameters["input_video"]
        watermark_text = parameters["watermark_text"]
        output_video = parameters.get("output_video")
        position = parameters.get("position", "bottom_right")
        font_size = parameters.get("font_size", 24)

        if not output_video:
            base_name = Path(input_video).stem
            output_video = f"{base_name}_watermarked.mp4"

        # Map position to ffmpeg coordinates
        position_map = {
            "top_left": "10:10",
            "top_right": "W-tw-10:10",
            "bottom_left": "10:H-th-10",
            "bottom_right": "W-tw-10:H-th-10",
            "center": "(W-tw)/2:(H-th)/2",
        }

        coords = position_map.get(position, "W-tw-10:H-th-10")

        # Build ffmpeg command with text watermark
        filter_complex = f"drawtext=text='{watermark_text}':fontcolor=white:fontsize={font_size}:box=1:boxcolor=black@0.5:boxborderw=5:x={coords}:y={coords}"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_video,
            "-vf",
            filter_complex,
            "-c:a",
            "copy",  # Copy audio
            output_video,
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg watermark failed: {result.stderr}")

        # Get output file info
        output_size = (
            os.path.getsize(output_video) if os.path.exists(output_video) else 0
        )

        return {
            "input_video": input_video,
            "output_video": output_video,
            "watermark_text": watermark_text,
            "position": position,
            "output_size": output_size,
        }


class AudioExtractionTool(RobustTool):
    """Tool for extracting audio from video."""

    def __init__(self):
        super().__init__(
            name="extract_audio", description="Extract audio track from video file"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for audio extraction."""
        return {
            "type": "object",
            "required": ["input_video"],
            "properties": {
                "input_video": {
                    "type": "string",
                    "description": "Path to input video file",
                },
                "output_audio": {
                    "type": "string",
                    "description": "Path for output audio file",
                },
                "format": {
                    "type": "string",
                    "enum": ["mp3", "wav", "aac", "flac"],
                    "default": "mp3",
                    "description": "Output audio format",
                },
                "bitrate": {
                    "type": "string",
                    "default": "192k",
                    "description": "Audio bitrate",
                },
            },
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Extract audio from video using ffmpeg."""
        import subprocess

        input_video = parameters["input_video"]
        output_audio = parameters.get("output_audio")
        format_type = parameters.get("format", "mp3")
        bitrate = parameters.get("bitrate", "192k")

        if not output_audio:
            base_name = Path(input_video).stem
            output_audio = f"{base_name}_audio.{format_type}"

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_video,  # Input video
            "-vn",  # No video
            "-acodec",
            self._get_audio_codec(format_type),
            "-ab",
            bitrate,  # Audio bitrate
            output_audio,
        ]

        # Execute ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg audio extraction failed: {result.stderr}")

        # Get output file info
        output_size = (
            os.path.getsize(output_audio) if os.path.exists(output_audio) else 0
        )

        return {
            "input_video": input_video,
            "output_audio": output_audio,
            "format": format_type,
            "bitrate": bitrate,
            "output_size": output_size,
        }

    def _get_audio_codec(self, format_type: str) -> str:
        """Get appropriate audio codec for format."""
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "aac": "aac",
            "flac": "flac",
        }
        return codec_map.get(format_type, "libmp3lame")
