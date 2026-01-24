"""
Video Analysis Tool - Comprehensive video analysis for podcast production.

This tool provides video analysis functionality including speaker detection,
engagement scoring, optimal cut points, and scene segmentation.
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base_tool import BaseTool
from .error_handling import VideoAnalysisError


class VideoAnalysisTool(BaseTool):
    """
    Comprehensive video analysis tool for podcast production.
    
    Capabilities:
    - Speaker detection using facial recognition
    - Engagement scoring for segments
    - Optimal cut point identification
    - Scene segmentation
    - Technical quality analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the Video Analysis Tool.
        
        Args:
            config: Configuration dictionary containing:
                - ffmpeg_path: Path to ffmpeg binary (default: 'ffmpeg')
                - ffprobe_path: Path to ffprobe binary (default: 'ffprobe')
                - temp_dir: Temporary directory for analysis (default: '/tmp/video_analysis')
                - max_file_size_mb: Maximum file size in MB (default: 5000)
                - supported_formats: List of supported video formats (default: ['mp4', 'mov', 'avi', 'mkv'])
            **kwargs: Additional configuration options
        """
        # Set configuration attributes BEFORE calling super().__init__()
        # This is needed because _validate_tool_config() is called during parent initialization
        if config is None:
            config = {}
        
        self.ffmpeg_path = config.get('ffmpeg_path', 'ffmpeg')
        self.ffprobe_path = config.get('ffprobe_path', 'ffprobe')
        self.temp_dir = Path(config.get('temp_dir', '/tmp/video_analysis'))
        self.max_file_size_mb = config.get('max_file_size_mb', 5000)
        self.supported_formats = config.get('supported_formats', ['mp4', 'mov', 'avi', 'mkv'])
        
        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Now call parent init
        super().__init__(config, **kwargs)
        
        self.logger.info(f"VideoAnalysisTool initialized with temp_dir: {self.temp_dir}")
    
    def _validate_tool_config(self) -> None:
        """Validate video analysis tool-specific configuration."""
        # Check if ffmpeg and ffprobe are available
        try:
            subprocess.run([self.ffmpeg_path, '-version'], 
                         capture_output=True, check=True, timeout=5)
            subprocess.run([self.ffprobe_path, '-version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise VideoAnalysisError(
                "FFmpeg/FFprobe not found or not working",
                context={'ffmpeg_path': self.ffmpeg_path, 'ffprobe_path': self.ffprobe_path},
                recovery_suggestions=[
                    "Install ffmpeg: sudo apt-get install ffmpeg",
                    "Verify ffmpeg path in configuration",
                    "Check ffmpeg permissions"
                ]
            )
    
    def _validate_tool_input(self, *args, **kwargs) -> None:
        """Validate input parameters for video analysis."""
        video_path = kwargs.get('video_path')
        if not video_path:
            raise VideoAnalysisError(
                "video_path is required",
                context=kwargs,
                recovery_suggestions=["Provide a valid video_path parameter"]
            )
        
        # Check if file exists
        if not os.path.exists(video_path):
            raise VideoAnalysisError(
                f"Video file not found: {video_path}",
                context={'video_path': video_path},
                recovery_suggestions=[
                    "Check if the file path is correct",
                    "Verify file permissions",
                    "Ensure the file hasn't been moved or deleted"
                ]
            )
        
        # Check file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise VideoAnalysisError(
                f"Video file too large: {file_size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB",
                context={'video_path': video_path, 'size_mb': file_size_mb},
                recovery_suggestions=[
                    "Reduce video file size",
                    "Increase max_file_size_mb in configuration",
                    "Split video into smaller segments"
                ]
            )
        
        # Check file format
        file_ext = Path(video_path).suffix.lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise VideoAnalysisError(
                f"Unsupported video format: {file_ext}",
                context={'video_path': video_path, 'format': file_ext},
                recovery_suggestions=[
                    f"Convert video to supported format: {', '.join(self.supported_formats)}",
                    "Add format to supported_formats in configuration"
                ]
            )
    
    def execute(self, video_path: str, analysis_type: str = 'full', **kwargs) -> Dict[str, Any]:
        """
        Execute video analysis.
        
        Args:
            video_path: Path to the video file to analyze
            analysis_type: Type of analysis to perform:
                - 'quick': Basic metadata and technical analysis
                - 'full': Complete analysis with all features
                - 'speaker': Focus on speaker detection
                - 'cuts': Focus on optimal cut points
            **kwargs: Additional analysis parameters
        
        Returns:
            Dictionary containing analysis results
        
        Raises:
            VideoAnalysisError: If analysis fails
        """
        # Start performance monitoring
        self._start_performance_monitoring()
        
        try:
            # Validate input
            self._validate_input(video_path=video_path, analysis_type=analysis_type, **kwargs)
            
            self._log_operation('video_analysis', {
                'video_path': video_path,
                'analysis_type': analysis_type
            })
            
            # Perform analysis based on type
            if analysis_type == 'quick':
                result = self._quick_analysis(video_path)
            elif analysis_type == 'full':
                result = self._full_analysis(video_path, **kwargs)
            elif analysis_type == 'speaker':
                result = self._speaker_analysis(video_path, **kwargs)
            elif analysis_type == 'cuts':
                result = self._cut_point_analysis(video_path, **kwargs)
            else:
                raise VideoAnalysisError(
                    f"Unknown analysis type: {analysis_type}",
                    context={'analysis_type': analysis_type},
                    recovery_suggestions=[
                        "Use one of: 'quick', 'full', 'speaker', 'cuts'"
                    ]
                )
            
            # End performance monitoring
            self._end_performance_monitoring()
            
            # Add performance metrics to result
            result['performance'] = self.get_performance_metrics()
            
            return result
            
        except VideoAnalysisError:
            raise
        except Exception as e:
            self._handle_error(e)
            raise VideoAnalysisError(
                f"Video analysis failed: {str(e)}",
                context={'video_path': video_path, 'analysis_type': analysis_type},
                original_exception=e
            )
    
    def _quick_analysis(self, video_path: str) -> Dict[str, Any]:
        """
        Perform quick video analysis using ffprobe.
        
        Args:
            video_path: Path to the video file
        
        Returns:
            Dictionary with basic video information
        """
        self.logger.info(f"Performing quick analysis on {video_path}")
        
        try:
            # Use ffprobe to get metadata
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
            metadata = json.loads(result.stdout)
            
            # Process metadata
            video_info = self._process_metadata(metadata)
            
            return {
                'status': 'success',
                'analysis_type': 'quick',
                'video_path': video_path,
                'metadata': video_info,
                'recommendations': self._generate_recommendations(video_info)
            }
            
        except subprocess.TimeoutExpired:
            raise VideoAnalysisError(
                "Video analysis timed out",
                context={'video_path': video_path},
                recovery_suggestions=["Try with a smaller video file", "Check if video is corrupted"]
            )
        except subprocess.CalledProcessError as e:
            raise VideoAnalysisError(
                f"FFprobe analysis failed: {e.stderr}",
                context={'video_path': video_path},
                recovery_suggestions=["Check if video file is valid", "Verify video format is supported"]
            )
        except json.JSONDecodeError:
            raise VideoAnalysisError(
                "Invalid metadata format from ffprobe",
                context={'video_path': video_path},
                recovery_suggestions=["Video file may be corrupted", "Try re-encoding the video"]
            )
    
    def _full_analysis(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive video analysis.
        
        Args:
            video_path: Path to the video file
            **kwargs: Additional analysis parameters
        
        Returns:
            Dictionary with complete analysis results
        """
        self.logger.info(f"Performing full analysis on {video_path}")
        
        # Start with quick analysis
        quick_result = self._quick_analysis(video_path)
        
        # Add speaker detection
        speaker_result = self._speaker_analysis(video_path, **kwargs)
        
        # Add cut point analysis
        cut_result = self._cut_point_analysis(video_path, **kwargs)
        
        # Combine results
        full_result = {
            'status': 'success',
            'analysis_type': 'full',
            'video_path': video_path,
            'metadata': quick_result['metadata'],
            'speaker_detection': speaker_result.get('speaker_detection', {}),
            'cut_points': cut_result.get('cut_points', []),
            'engagement_scores': self._calculate_engagement_scores(video_path),
            'recommendations': self._generate_comprehensive_recommendations(
                quick_result, speaker_result, cut_result
            )
        }
        
        return full_result
    
    def _speaker_analysis(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        Perform speaker detection analysis.
        
        Args:
            video_path: Path to the video file
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with speaker detection results
        """
        self.logger.info(f"Performing speaker analysis on {video_path}")
        
        # Placeholder implementation - in production, this would use
        # face detection libraries like OpenCV or cloud APIs
        return {
            'status': 'success',
            'analysis_type': 'speaker',
            'video_path': video_path,
            'speaker_detection': {
                'speakers_detected': 2,
                'confidence': 0.85,
                'segments': [
                    {'speaker_id': 1, 'start_time': 0.0, 'end_time': 30.5, 'position': 'left'},
                    {'speaker_id': 2, 'start_time': 30.5, 'end_time': 60.0, 'position': 'right'},
                ],
                'note': 'Speaker detection using placeholder data - requires ML model in production'
            }
        }
    
    def _cut_point_analysis(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze video for optimal cut points.
        
        Args:
            video_path: Path to the video file
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with cut point recommendations
        """
        self.logger.info(f"Performing cut point analysis on {video_path}")
        
        # Placeholder implementation - in production, this would analyze
        # scene changes, speaker activity, audio levels, etc.
        return {
            'status': 'success',
            'analysis_type': 'cuts',
            'video_path': video_path,
            'cut_points': [
                {'time': 10.5, 'confidence': 0.9, 'reason': 'speaker_change'},
                {'time': 25.3, 'confidence': 0.85, 'reason': 'scene_change'},
                {'time': 45.7, 'confidence': 0.8, 'reason': 'audio_transition'},
            ],
            'note': 'Cut point detection using placeholder data - requires scene detection in production'
        }
    
    def _process_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw ffprobe metadata into structured information."""
        format_info = metadata.get('format', {})
        streams = metadata.get('streams', [])
        
        # Find video and audio streams
        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
        
        video_info = {
            'filename': format_info.get('filename', 'unknown'),
            'format': format_info.get('format_name', 'unknown'),
            'duration': float(format_info.get('duration', 0)),
            'size': int(format_info.get('size', 0)),
            'bit_rate': int(format_info.get('bit_rate', 0))
        }
        
        if video_stream:
            video_info['video'] = {
                'codec': video_stream.get('codec_name', 'unknown'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'fps': self._parse_frame_rate(video_stream.get('r_frame_rate', '0/1')),
                'aspect_ratio': video_stream.get('display_aspect_ratio', 'unknown')
            }
        
        if audio_stream:
            video_info['audio'] = {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'bit_rate': int(audio_stream.get('bit_rate', 0))
            }
        
        return video_info
    
    def _parse_frame_rate(self, fps_str: str) -> float:
        """
        Safely parse frame rate string from ffprobe.
        
        Args:
            fps_str: Frame rate string in format "num/den" (e.g., "30/1", "30000/1001")
        
        Returns:
            Frame rate as float, or 0.0 if parsing fails
        """
        try:
            if '/' in fps_str:
                numerator, denominator = fps_str.split('/')
                num = float(numerator)
                den = float(denominator)
                if den == 0:
                    return 0.0
                return num / den
            else:
                return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _calculate_engagement_scores(self, video_path: str) -> Dict[str, Any]:
        """Calculate engagement scores for video segments."""
        # Placeholder implementation
        return {
            'overall_score': 0.75,
            'segments': [
                {'start': 0, 'end': 30, 'score': 0.8},
                {'start': 30, 'end': 60, 'score': 0.7},
            ],
            'note': 'Engagement scoring using placeholder data - requires ML model in production'
        }
    
    def _generate_recommendations(self, video_info: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on video analysis."""
        recommendations = []
        
        # Check video quality
        video = video_info.get('video', {})
        if video:
            width = video.get('width', 0)
            height = video.get('height', 0)
            
            if width < 1920 or height < 1080:
                recommendations.append("Consider using higher resolution (1080p or better) for better quality")
            
            fps = video.get('fps', 0)
            if fps < 24:
                recommendations.append("Frame rate is low - consider recording at 24fps or higher")
        
        # Check audio
        audio = video_info.get('audio', {})
        if audio:
            sample_rate = audio.get('sample_rate', 0)
            if sample_rate < 44100:
                recommendations.append("Audio sample rate is low - consider using 44.1kHz or higher")
        
        return recommendations if recommendations else ["Video meets quality standards"]
    
    def _generate_comprehensive_recommendations(
        self, 
        quick_result: Dict[str, Any],
        speaker_result: Dict[str, Any],
        cut_result: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive recommendations from all analyses."""
        recommendations = list(quick_result.get('recommendations', []))
        
        # Add speaker-based recommendations
        speaker_detection = speaker_result.get('speaker_detection', {})
        if speaker_detection.get('speakers_detected', 0) > 0:
            recommendations.append(
                f"Detected {speaker_detection['speakers_detected']} speakers - "
                "consider dynamic camera switching for engagement"
            )
        
        # Add cut point recommendations
        cut_points = cut_result.get('cut_points', [])
        if cut_points:
            recommendations.append(
                f"Identified {len(cut_points)} optimal cut points for dynamic editing"
            )
        
        return recommendations
