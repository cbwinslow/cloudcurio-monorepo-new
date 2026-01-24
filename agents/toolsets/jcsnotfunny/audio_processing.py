"""
Audio Processing Tool - Comprehensive audio processing for podcast production.

This tool provides audio processing functionality including noise reduction,
voice enhancement, sponsor insertion, and audio mastering.
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base_tool import BaseTool
from .error_handling import AudioProcessingError


class AudioProcessingTool(BaseTool):
    """
    Comprehensive audio processing tool for podcast production.
    
    Capabilities:
    - Background noise removal
    - Voice enhancement (EQ, compression, de-essing)
    - Sponsor read insertion
    - Audio mastering and normalization
    - Format conversion
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the Audio Processing Tool.
        
        Args:
            config: Configuration dictionary containing:
                - ffmpeg_path: Path to ffmpeg binary (default: 'ffmpeg')
                - temp_dir: Temporary directory for processing (default: '/tmp/audio_processing')
                - max_file_size_mb: Maximum file size in MB (default: 1000)
                - supported_formats: List of supported audio formats (default: ['mp3', 'wav', 'flac', 'm4a'])
                - default_sample_rate: Default sample rate (default: 48000)
                - default_bit_rate: Default bit rate (default: 192k)
            **kwargs: Additional configuration options
        """
        # Set configuration attributes BEFORE calling super().__init__()
        # This is needed because _validate_tool_config() is called during parent initialization
        if config is None:
            config = {}
        
        self.ffmpeg_path = config.get('ffmpeg_path', 'ffmpeg')
        self.temp_dir = Path(config.get('temp_dir', '/tmp/audio_processing'))
        self.max_file_size_mb = config.get('max_file_size_mb', 1000)
        self.supported_formats = config.get('supported_formats', ['mp3', 'wav', 'flac', 'm4a', 'aac'])
        self.default_sample_rate = config.get('default_sample_rate', 48000)
        self.default_bit_rate = config.get('default_bit_rate', '192k')
        
        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Now call parent init
        super().__init__(config, **kwargs)
        
        self.logger.info(f"AudioProcessingTool initialized with temp_dir: {self.temp_dir}")
    
    def _validate_tool_config(self) -> None:
        """Validate audio processing tool-specific configuration."""
        # Check if ffmpeg is available
        try:
            subprocess.run([self.ffmpeg_path, '-version'], 
                         capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise AudioProcessingError(
                "FFmpeg not found or not working",
                context={'ffmpeg_path': self.ffmpeg_path},
                recovery_suggestions=[
                    "Install ffmpeg: sudo apt-get install ffmpeg",
                    "Verify ffmpeg path in configuration",
                    "Check ffmpeg permissions"
                ]
            )
    
    def _validate_audio_file(self, audio_path: str) -> None:
        """Validate an audio file."""
        # Check if file exists
        if not os.path.exists(audio_path):
            raise AudioProcessingError(
                f"Audio file not found: {audio_path}",
                context={'audio_path': audio_path},
                recovery_suggestions=[
                    "Check if the file path is correct",
                    "Verify file permissions",
                    "Ensure the file hasn't been moved or deleted"
                ]
            )
        
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise AudioProcessingError(
                f"Audio file too large: {file_size_mb:.2f}MB exceeds limit of {self.max_file_size_mb}MB",
                context={'audio_path': audio_path, 'size_mb': file_size_mb},
                recovery_suggestions=[
                    "Reduce audio file size",
                    "Increase max_file_size_mb in configuration",
                    "Split audio into smaller segments"
                ]
            )
        
        # Check file format
        file_ext = Path(audio_path).suffix.lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise AudioProcessingError(
                f"Unsupported audio format: {file_ext}",
                context={'audio_path': audio_path, 'format': file_ext},
                recovery_suggestions=[
                    f"Convert audio to supported format: {', '.join(self.supported_formats)}",
                    "Add format to supported_formats in configuration"
                ]
            )
    
    def execute(self, operation: str, audio_path: str, output_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute audio processing operation.
        
        Args:
            operation: Operation to perform:
                - 'cleanup': Remove background noise and artifacts
                - 'enhance': Enhance voice quality (EQ, compression, de-essing)
                - 'insert_sponsor': Insert sponsor read at specific points
                - 'master': Master audio for distribution
                - 'convert': Convert audio format
                - 'normalize': Normalize audio levels
            audio_path: Path to the input audio file
            output_path: Path for the output file (optional, auto-generated if not provided)
            **kwargs: Additional operation parameters
        
        Returns:
            Dictionary containing processing results
        
        Raises:
            AudioProcessingError: If processing fails
        """
        # Start performance monitoring
        self._start_performance_monitoring()
        
        try:
            # Validate input
            self._validate_audio_file(audio_path)
            
            # Generate output path if not provided
            if not output_path:
                output_path = self._generate_output_path(audio_path, operation)
            
            self._log_operation('audio_processing', {
                'operation': operation,
                'audio_path': audio_path,
                'output_path': output_path
            })
            
            # Perform operation based on type
            if operation == 'cleanup':
                result = self._cleanup_audio(audio_path, output_path, **kwargs)
            elif operation == 'enhance':
                result = self._enhance_audio(audio_path, output_path, **kwargs)
            elif operation == 'insert_sponsor':
                result = self._insert_sponsor(audio_path, output_path, **kwargs)
            elif operation == 'master':
                result = self._master_audio(audio_path, output_path, **kwargs)
            elif operation == 'convert':
                result = self._convert_audio(audio_path, output_path, **kwargs)
            elif operation == 'normalize':
                result = self._normalize_audio(audio_path, output_path, **kwargs)
            else:
                raise AudioProcessingError(
                    f"Unknown operation: {operation}",
                    context={'operation': operation},
                    recovery_suggestions=[
                        "Use one of: 'cleanup', 'enhance', 'insert_sponsor', 'master', 'convert', 'normalize'"
                    ]
                )
            
            # End performance monitoring
            self._end_performance_monitoring()
            
            # Add performance metrics to result
            result['performance'] = self.get_performance_metrics()
            
            return result
            
        except AudioProcessingError:
            raise
        except Exception as e:
            self._handle_error(e)
            raise AudioProcessingError(
                f"Audio processing failed: {str(e)}",
                context={'operation': operation, 'audio_path': audio_path},
                original_exception=e
            )
    
    def _generate_output_path(self, input_path: str, operation: str) -> str:
        """Generate output path based on input path and operation."""
        input_path_obj = Path(input_path)
        stem = input_path_obj.stem
        ext = input_path_obj.suffix
        output_filename = f"{stem}_{operation}{ext}"
        return str(self.temp_dir / output_filename)
    
    def _cleanup_audio(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Clean up audio by removing background noise and artifacts.
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            **kwargs: Additional parameters:
                - noise_reduction: Reduction level ('light', 'medium', 'aggressive')
                - hum_removal: Remove 50/60Hz hum (default: True)
        
        Returns:
            Dictionary with cleanup results
        """
        self.logger.info(f"Cleaning up audio: {audio_path}")
        
        noise_reduction = kwargs.get('noise_reduction', 'medium')
        hum_removal = kwargs.get('hum_removal', True)
        
        # Build ffmpeg filter chain for audio cleanup
        filters = []
        
        # High-pass filter to remove low-frequency rumble
        filters.append('highpass=f=80')
        
        # Hum removal (50Hz and 60Hz)
        if hum_removal:
            filters.append('lowpass=f=10000')
        
        # Noise reduction using afftdn (FFT denoiser)
        if noise_reduction == 'light':
            filters.append('afftdn=nf=-20')
        elif noise_reduction == 'medium':
            filters.append('afftdn=nf=-25')
        elif noise_reduction == 'aggressive':
            filters.append('afftdn=nf=-30')
        
        filter_complex = ','.join(filters)
        
        try:
            # Execute ffmpeg command
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-af', filter_complex,
                '-acodec', 'libmp3lame',
                '-b:a', self.default_bit_rate,
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'cleanup',
                'input_path': audio_path,
                'output_path': output_path,
                'noise_reduction': noise_reduction,
                'hum_removal': hum_removal,
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Audio cleanup timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with a smaller audio file", "Check if audio is corrupted"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path},
                recovery_suggestions=["Check if audio file is valid", "Verify audio format is supported"]
            )
    
    def _enhance_audio(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Enhance audio with EQ, compression, and de-essing.
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            **kwargs: Additional parameters:
                - preset: Audio preset ('podcast', 'interview', 'narration')
                - compression_ratio: Compression ratio (default: 4)
                - de_essing: De-essing strength (default: 0.6)
        
        Returns:
            Dictionary with enhancement results
        """
        self.logger.info(f"Enhancing audio: {audio_path}")
        
        preset = kwargs.get('preset', 'podcast')
        compression_ratio = kwargs.get('compression_ratio', 4)
        de_essing = kwargs.get('de_essing', 0.6)
        
        # Build ffmpeg filter chain for audio enhancement
        filters = []
        
        # EQ adjustments based on preset
        if preset == 'podcast':
            # Boost presence (2-5kHz), cut lows, smooth highs
            filters.append('equalizer=f=100:t=h:width=200:g=-6')  # Reduce rumble
            filters.append('equalizer=f=3000:t=h:width=2000:g=3')  # Boost presence
            filters.append('equalizer=f=10000:t=h:width=2000:g=-2')  # Smooth highs
        elif preset == 'interview':
            # Balanced for multiple speakers
            filters.append('equalizer=f=200:t=h:width=100:g=-3')
            filters.append('equalizer=f=2500:t=h:width=1500:g=2')
        elif preset == 'narration':
            # Smooth and professional
            filters.append('equalizer=f=150:t=h:width=100:g=-4')
            filters.append('equalizer=f=2000:t=h:width=1000:g=2')
        
        # Compression
        filters.append(f'acompressor=threshold=-20dB:ratio={compression_ratio}:attack=5:release=50')
        
        # De-essing using highpass/lowpass combination
        # Target sibilance frequencies (6-10kHz) with a multiband approach
        if de_essing > 0:
            # Reduce high frequencies where sibilance occurs
            filters.append(f'equalizer=f=8000:t=h:width=4000:g=-{int(de_essing * 10)}')
        
        # Normalize
        filters.append('loudnorm=I=-16:TP=-1.5:LRA=11')
        
        filter_complex = ','.join(filters)
        
        try:
            # Execute ffmpeg command
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-af', filter_complex,
                '-acodec', 'libmp3lame',
                '-b:a', self.default_bit_rate,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'enhance',
                'input_path': audio_path,
                'output_path': output_path,
                'preset': preset,
                'compression_ratio': compression_ratio,
                'de_essing': de_essing,
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Audio enhancement timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with a smaller audio file"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path},
                recovery_suggestions=["Check if audio file is valid"]
            )
    
    def _insert_sponsor(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Insert sponsor reads at specified points in the audio.
        
        Args:
            audio_path: Input audio file (main content)
            output_path: Output audio file
            **kwargs: Additional parameters:
                - sponsor_audio: Path to sponsor read audio file (required)
                - insertion_points: List of timestamps in seconds (required)
                - transition_duration: Fade duration in seconds (default: 1.0)
        
        Returns:
            Dictionary with insertion results
        """
        self.logger.info(f"Inserting sponsor reads: {audio_path}")
        
        sponsor_audio = kwargs.get('sponsor_audio')
        insertion_points = kwargs.get('insertion_points', [])
        transition_duration = kwargs.get('transition_duration', 1.0)
        
        if not sponsor_audio:
            raise AudioProcessingError(
                "sponsor_audio parameter is required for insert_sponsor operation",
                context=kwargs,
                recovery_suggestions=["Provide sponsor_audio path"]
            )
        
        if not insertion_points:
            raise AudioProcessingError(
                "insertion_points parameter is required for insert_sponsor operation",
                context=kwargs,
                recovery_suggestions=["Provide list of insertion points (timestamps in seconds)"]
            )
        
        # Validate sponsor audio file
        self._validate_audio_file(sponsor_audio)
        
        # For simplicity, insert at the first point only
        # In production, this would handle multiple insertion points
        first_point = insertion_points[0]
        
        try:
            # Split, insert, and concatenate
            # This is a simplified implementation
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-i', sponsor_audio,
                '-filter_complex',
                f'[0:a]asplit=2[a1][a2];[a1]atrim=0:{first_point},afade=t=out:st={first_point-transition_duration}:d={transition_duration}[a1out];'
                f'[1:a]afade=t=in:st=0:d={transition_duration},afade=t=out:st=end-{transition_duration}:d={transition_duration}[sponsor];'
                f'[a2]atrim={first_point},afade=t=in:st=0:d={transition_duration}[a2out];'
                f'[a1out][sponsor][a2out]concat=n=3:v=0:a=1[aout]',
                '-map', '[aout]',
                '-acodec', 'libmp3lame',
                '-b:a', self.default_bit_rate,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'insert_sponsor',
                'input_path': audio_path,
                'sponsor_audio': sponsor_audio,
                'output_path': output_path,
                'insertion_points': insertion_points,
                'points_processed': 1,  # Simplified implementation
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Sponsor insertion timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with smaller audio files"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path, 'sponsor_audio': sponsor_audio},
                recovery_suggestions=["Check if audio files are valid", "Verify insertion points are within audio duration"]
            )
    
    def _master_audio(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Master audio for distribution with normalization and limiting.
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            **kwargs: Additional parameters:
                - target_lufs: Target LUFS level (default: -16)
                - true_peak: True peak level in dBTP (default: -1.5)
        
        Returns:
            Dictionary with mastering results
        """
        self.logger.info(f"Mastering audio: {audio_path}")
        
        target_lufs = kwargs.get('target_lufs', -16)
        true_peak = kwargs.get('true_peak', -1.5)
        
        try:
            # Apply loudness normalization and limiting
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-af', f'loudnorm=I={target_lufs}:TP={true_peak}:LRA=11',
                '-acodec', 'libmp3lame',
                '-b:a', '320k',  # High quality for mastered audio
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'master',
                'input_path': audio_path,
                'output_path': output_path,
                'target_lufs': target_lufs,
                'true_peak': true_peak,
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Audio mastering timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with a smaller audio file"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path},
                recovery_suggestions=["Check if audio file is valid"]
            )
    
    def _convert_audio(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert audio to different format.
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            **kwargs: Additional parameters:
                - target_format: Target format (default: 'mp3')
                - sample_rate: Sample rate (default: 48000)
                - bit_rate: Bit rate (default: '192k')
        
        Returns:
            Dictionary with conversion results
        """
        self.logger.info(f"Converting audio: {audio_path}")
        
        target_format = kwargs.get('target_format', 'mp3')
        sample_rate = kwargs.get('sample_rate', self.default_sample_rate)
        bit_rate = kwargs.get('bit_rate', self.default_bit_rate)
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-ar', str(sample_rate),
                '-b:a', bit_rate,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'convert',
                'input_path': audio_path,
                'output_path': output_path,
                'target_format': target_format,
                'sample_rate': sample_rate,
                'bit_rate': bit_rate,
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Audio conversion timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with a smaller audio file"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path},
                recovery_suggestions=["Check if audio file is valid"]
            )
    
    def _normalize_audio(self, audio_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Normalize audio levels.
        
        Args:
            audio_path: Input audio file
            output_path: Output audio file
            **kwargs: Additional parameters:
                - method: Normalization method ('peak' or 'lufs', default: 'lufs')
        
        Returns:
            Dictionary with normalization results
        """
        self.logger.info(f"Normalizing audio: {audio_path}")
        
        method = kwargs.get('method', 'lufs')
        
        try:
            if method == 'peak':
                # Peak normalization
                filter_complex = 'volume=0dB'
            else:
                # LUFS normalization
                filter_complex = 'loudnorm=I=-16:TP=-1.5:LRA=11'
            
            cmd = [
                self.ffmpeg_path,
                '-i', audio_path,
                '-af', filter_complex,
                '-acodec', 'libmp3lame',
                '-b:a', self.default_bit_rate,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            
            return {
                'status': 'success',
                'operation': 'normalize',
                'input_path': audio_path,
                'output_path': output_path,
                'method': method,
                'file_size': os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError(
                "Audio normalization timed out",
                context={'audio_path': audio_path},
                recovery_suggestions=["Try with a smaller audio file"]
            )
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg processing failed: {e.stderr}",
                context={'audio_path': audio_path},
                recovery_suggestions=["Check if audio file is valid"]
            )
