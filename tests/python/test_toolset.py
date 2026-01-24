"""
Unit tests for podcast production toolset.

Tests cover Video Analysis, Audio Processing, and Content Scheduling tools.
"""

import sys
import os
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

# Add toolsets to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "toolsets"))

from jcsnotfunny.video_analysis import VideoAnalysisTool
from jcsnotfunny.audio_processing import AudioProcessingTool
from jcsnotfunny.content_scheduling import ContentSchedulingTool
from jcsnotfunny.error_handling import (
    VideoAnalysisError,
    AudioProcessingError,
    SchedulingError,
    SchedulingConflictError,
    SchedulingValidationError
)


class TestVideoAnalysisTool:
    """Tests for VideoAnalysisTool"""
    
    def test_init(self):
        """Test tool initialization"""
        tool = VideoAnalysisTool()
        assert tool.tool_name == 'VideoAnalysisTool'
        assert tool.ffmpeg_path == 'ffmpeg'
        assert tool.max_file_size_mb == 5000
        assert tool.temp_dir.exists()
    
    def test_init_with_config(self):
        """Test tool initialization with custom config"""
        config = {
            'ffmpeg_path': '/usr/bin/ffmpeg',
            'max_file_size_mb': 3000,
            'supported_formats': ['mp4', 'mov']
        }
        tool = VideoAnalysisTool(config=config)
        assert tool.ffmpeg_path == '/usr/bin/ffmpeg'
        assert tool.max_file_size_mb == 3000
        assert tool.supported_formats == ['mp4', 'mov']
    
    @patch('subprocess.run')
    def test_config_validation_success(self, mock_run):
        """Test successful config validation"""
        mock_run.return_value = Mock(returncode=0)
        tool = VideoAnalysisTool()
        # Should not raise exception
        assert tool is not None
    
    @patch('subprocess.run')
    def test_config_validation_failure(self, mock_run):
        """Test config validation failure when ffmpeg not found"""
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(VideoAnalysisError) as exc_info:
            VideoAnalysisTool()
        assert 'FFmpeg/FFprobe not found' in str(exc_info.value)
    
    def test_validate_input_missing_video_path(self):
        """Test input validation with missing video_path"""
        tool = VideoAnalysisTool()
        with pytest.raises(VideoAnalysisError) as exc_info:
            tool._validate_tool_input()
        assert 'video_path is required' in str(exc_info.value)
    
    def test_validate_input_file_not_found(self):
        """Test input validation with non-existent file"""
        tool = VideoAnalysisTool()
        with pytest.raises(VideoAnalysisError) as exc_info:
            tool._validate_tool_input(video_path='/nonexistent/file.mp4')
        assert 'Video file not found' in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_validate_input_file_too_large(self, mock_getsize, mock_exists):
        """Test input validation with oversized file"""
        mock_exists.return_value = True
        mock_getsize.return_value = 6000 * 1024 * 1024  # 6GB
        
        tool = VideoAnalysisTool()
        with pytest.raises(VideoAnalysisError) as exc_info:
            tool._validate_tool_input(video_path='/path/to/large.mp4')
        assert 'too large' in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_validate_input_unsupported_format(self, mock_getsize, mock_exists):
        """Test input validation with unsupported format"""
        mock_exists.return_value = True
        mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
        
        tool = VideoAnalysisTool()
        with pytest.raises(VideoAnalysisError) as exc_info:
            tool._validate_tool_input(video_path='/path/to/video.wmv')
        assert 'Unsupported video format' in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_quick_analysis_success(self, mock_getsize, mock_exists, mock_run):
        """Test successful quick analysis"""
        mock_exists.return_value = True
        mock_getsize.return_value = 100 * 1024 * 1024
        
        # Mock ffprobe output
        mock_metadata = {
            'format': {
                'filename': 'test.mp4',
                'format_name': 'mp4',
                'duration': '120.5',
                'size': '104857600',
                'bit_rate': '1048576'
            },
            'streams': [
                {
                    'codec_type': 'video',
                    'codec_name': 'h264',
                    'width': 1920,
                    'height': 1080,
                    'r_frame_rate': '30/1',
                    'display_aspect_ratio': '16:9'
                },
                {
                    'codec_type': 'audio',
                    'codec_name': 'aac',
                    'sample_rate': '48000',
                    'channels': 2,
                    'bit_rate': '128000'
                }
            ]
        }
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_metadata)
        )
        
        tool = VideoAnalysisTool()
        result = tool.execute(video_path='/path/to/test.mp4', analysis_type='quick')
        
        assert result['status'] == 'success'
        assert result['analysis_type'] == 'quick'
        assert 'metadata' in result
        assert 'recommendations' in result
    
    def test_execute_invalid_analysis_type(self):
        """Test execute with invalid analysis type"""
        tool = VideoAnalysisTool()
        with pytest.raises(VideoAnalysisError) as exc_info:
            tool.execute(video_path='/path/to/test.mp4', analysis_type='invalid')
        assert 'Unknown analysis type' in str(exc_info.value)


class TestAudioProcessingTool:
    """Tests for AudioProcessingTool"""
    
    def test_init(self):
        """Test tool initialization"""
        tool = AudioProcessingTool()
        assert tool.tool_name == 'AudioProcessingTool'
        assert tool.ffmpeg_path == 'ffmpeg'
        assert tool.max_file_size_mb == 1000
        assert tool.temp_dir.exists()
    
    def test_init_with_config(self):
        """Test tool initialization with custom config"""
        config = {
            'ffmpeg_path': '/usr/bin/ffmpeg',
            'max_file_size_mb': 500,
            'default_sample_rate': 44100
        }
        tool = AudioProcessingTool(config=config)
        assert tool.ffmpeg_path == '/usr/bin/ffmpeg'
        assert tool.max_file_size_mb == 500
        assert tool.default_sample_rate == 44100
    
    @patch('subprocess.run')
    def test_validate_audio_file_not_found(self, mock_run):
        """Test audio file validation with non-existent file"""
        mock_run.return_value = Mock(returncode=0)
        tool = AudioProcessingTool()
        
        with pytest.raises(AudioProcessingError) as exc_info:
            tool._validate_audio_file('/nonexistent/audio.mp3')
        assert 'Audio file not found' in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('subprocess.run')
    def test_validate_audio_file_too_large(self, mock_run, mock_getsize, mock_exists):
        """Test audio file validation with oversized file"""
        mock_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True
        mock_getsize.return_value = 1500 * 1024 * 1024  # 1.5GB
        
        tool = AudioProcessingTool()
        with pytest.raises(AudioProcessingError) as exc_info:
            tool._validate_audio_file('/path/to/large.mp3')
        assert 'too large' in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('subprocess.run')
    def test_cleanup_audio_success(self, mock_run, mock_getsize, mock_exists):
        """Test successful audio cleanup"""
        mock_run.return_value = Mock(returncode=0, stderr='', stdout='')
        mock_exists.return_value = True
        mock_getsize.return_value = 50 * 1024 * 1024  # 50MB
        
        tool = AudioProcessingTool()
        result = tool.execute(
            operation='cleanup',
            audio_path='/path/to/audio.mp3',
            noise_reduction='medium'
        )
        
        assert result['status'] == 'success'
        assert result['operation'] == 'cleanup'
        assert 'output_path' in result
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('subprocess.run')
    def test_enhance_audio_success(self, mock_run, mock_getsize, mock_exists):
        """Test successful audio enhancement"""
        mock_run.return_value = Mock(returncode=0, stderr='', stdout='')
        mock_exists.return_value = True
        mock_getsize.return_value = 50 * 1024 * 1024
        
        tool = AudioProcessingTool()
        result = tool.execute(
            operation='enhance',
            audio_path='/path/to/audio.mp3',
            preset='podcast'
        )
        
        assert result['status'] == 'success'
        assert result['operation'] == 'enhance'
        assert result['preset'] == 'podcast'
    
    def test_execute_invalid_operation(self):
        """Test execute with invalid operation"""
        tool = AudioProcessingTool()
        with pytest.raises(AudioProcessingError) as exc_info:
            tool.execute(operation='invalid', audio_path='/path/to/audio.mp3')
        assert 'Unknown operation' in str(exc_info.value)
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('subprocess.run')
    def test_insert_sponsor_missing_params(self, mock_run, mock_getsize, mock_exists):
        """Test sponsor insertion with missing parameters"""
        mock_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True
        mock_getsize.return_value = 50 * 1024 * 1024
        
        tool = AudioProcessingTool()
        with pytest.raises(AudioProcessingError) as exc_info:
            tool.execute(
                operation='insert_sponsor',
                audio_path='/path/to/audio.mp3'
            )
        assert 'sponsor_audio' in str(exc_info.value)


class TestContentSchedulingTool:
    """Tests for ContentSchedulingTool"""
    
    def test_init(self):
        """Test tool initialization"""
        tool = ContentSchedulingTool()
        assert tool.tool_name == 'ContentSchedulingTool'
        assert len(tool.supported_platforms) > 0
        assert tool.max_posts_per_day == 10
        assert tool.min_interval_minutes == 60
    
    def test_init_with_config(self):
        """Test tool initialization with custom config"""
        config = {
            'supported_platforms': ['twitter', 'instagram'],
            'max_posts_per_day': 5,
            'min_interval_minutes': 120
        }
        tool = ContentSchedulingTool(config=config)
        assert tool.supported_platforms == ['twitter', 'instagram']
        assert tool.max_posts_per_day == 5
        assert tool.min_interval_minutes == 120
    
    def test_validate_platform_success(self):
        """Test platform validation with valid platform"""
        tool = ContentSchedulingTool()
        # Should not raise exception
        tool._validate_platform('twitter')
    
    def test_validate_platform_failure(self):
        """Test platform validation with invalid platform"""
        tool = ContentSchedulingTool()
        with pytest.raises(SchedulingValidationError) as exc_info:
            tool._validate_platform('myspace')
        assert 'Unsupported platform' in str(exc_info.value)
    
    def test_validate_datetime_success(self):
        """Test datetime validation with valid ISO format"""
        tool = ContentSchedulingTool()
        dt_str = '2024-03-15T14:30:00'
        dt = tool._validate_datetime(dt_str)
        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 3
        assert dt.day == 15
    
    def test_validate_datetime_failure(self):
        """Test datetime validation with invalid format"""
        tool = ContentSchedulingTool()
        with pytest.raises(SchedulingValidationError) as exc_info:
            tool._validate_datetime('invalid-datetime')
        assert 'Invalid datetime format' in str(exc_info.value)
    
    def test_schedule_post_success(self):
        """Test successful post scheduling"""
        tool = ContentSchedulingTool()
        
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        result = tool.execute(
            operation='schedule',
            content='Test post content',
            platforms=['twitter', 'instagram'],
            schedule_time=future_time
        )
        
        assert result['status'] == 'success'
        assert result['operation'] == 'schedule'
        assert 'post_id' in result
        assert result['post_entry']['content'] == 'Test post content'
    
    def test_schedule_post_missing_content(self):
        """Test scheduling with missing content"""
        tool = ContentSchedulingTool()
        
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        with pytest.raises(SchedulingValidationError) as exc_info:
            tool.execute(
                operation='schedule',
                platforms=['twitter'],
                schedule_time=future_time
            )
        assert 'content parameter is required' in str(exc_info.value)
    
    def test_schedule_post_past_time(self):
        """Test scheduling in the past"""
        tool = ContentSchedulingTool()
        
        past_time = (datetime.now() - timedelta(hours=2)).isoformat()
        with pytest.raises(SchedulingValidationError) as exc_info:
            tool.execute(
                operation='schedule',
                content='Test post',
                platforms=['twitter'],
                schedule_time=past_time
            )
        assert 'Cannot schedule posts in the past' in str(exc_info.value)
    
    def test_generate_calendar_success(self):
        """Test calendar generation"""
        tool = ContentSchedulingTool()
        
        # Schedule a post first
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        tool.execute(
            operation='schedule',
            content='Test post',
            platforms=['twitter'],
            schedule_time=future_time
        )
        
        # Generate calendar
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        result = tool.execute(
            operation='calendar',
            start_date=start_date,
            end_date=end_date
        )
        
        assert result['status'] == 'success'
        assert result['operation'] == 'calendar'
        assert 'calendar' in result
        assert result['total_posts'] >= 1
    
    def test_generate_calendar_invalid_dates(self):
        """Test calendar generation with invalid dates"""
        tool = ContentSchedulingTool()
        
        with pytest.raises(SchedulingValidationError) as exc_info:
            tool.execute(
                operation='calendar',
                start_date='2024-12-31',
                end_date='2024-01-01'  # End before start
            )
        assert 'start_date must be before end_date' in str(exc_info.value)
    
    def test_check_conflicts_no_conflict(self):
        """Test conflict checking with no conflicts"""
        tool = ContentSchedulingTool()
        
        future_time = (datetime.now() + timedelta(hours=3)).isoformat()
        result = tool.execute(
            operation='check_conflicts',
            schedule_time=future_time,
            platforms=['twitter']
        )
        
        assert result['status'] == 'success'
        assert result['has_conflicts'] == False
    
    def test_check_conflicts_with_conflict(self):
        """Test conflict checking with existing conflict"""
        tool = ContentSchedulingTool()
        
        # Schedule first post
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        tool.execute(
            operation='schedule',
            content='First post',
            platforms=['twitter'],
            schedule_time=future_time
        )
        
        # Check conflicts for nearby time
        nearby_time = (datetime.now() + timedelta(hours=2, minutes=30)).isoformat()
        result = tool.execute(
            operation='check_conflicts',
            schedule_time=nearby_time,
            platforms=['twitter']
        )
        
        assert result['status'] == 'success'
        assert result['has_conflicts'] == True
        assert len(result['conflicts']) > 0
    
    def test_list_posts_success(self):
        """Test listing scheduled posts"""
        tool = ContentSchedulingTool()
        
        # Schedule a post
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        tool.execute(
            operation='schedule',
            content='Test post',
            platforms=['twitter'],
            schedule_time=future_time
        )
        
        # List posts
        result = tool.execute(operation='list')
        
        assert result['status'] == 'success'
        assert result['post_count'] >= 1
        assert len(result['posts']) >= 1
    
    def test_cancel_post_success(self):
        """Test successful post cancellation"""
        tool = ContentSchedulingTool()
        
        # Schedule a post
        future_time = (datetime.now() + timedelta(hours=2)).isoformat()
        schedule_result = tool.execute(
            operation='schedule',
            content='Test post',
            platforms=['twitter'],
            schedule_time=future_time
        )
        
        post_id = schedule_result['post_id']
        
        # Cancel the post
        result = tool.execute(
            operation='cancel',
            post_id=post_id
        )
        
        assert result['status'] == 'success'
        assert result['operation'] == 'cancel'
    
    def test_cancel_post_not_found(self):
        """Test canceling non-existent post"""
        tool = ContentSchedulingTool()
        
        with pytest.raises(SchedulingError) as exc_info:
            tool.execute(
                operation='cancel',
                post_id='nonexistent_id'
            )
        assert 'Post not found' in str(exc_info.value)
    
    def test_execute_invalid_operation(self):
        """Test execute with invalid operation"""
        tool = ContentSchedulingTool()
        
        with pytest.raises(SchedulingError) as exc_info:
            tool.execute(operation='invalid_operation')
        assert 'Unknown operation' in str(exc_info.value)


# Integration Tests
class TestToolsetIntegration:
    """Integration tests for toolset interactions"""
    
    def test_all_tools_instantiate(self):
        """Test that all tools can be instantiated"""
        video_tool = VideoAnalysisTool()
        audio_tool = AudioProcessingTool()
        scheduling_tool = ContentSchedulingTool()
        
        assert video_tool is not None
        assert audio_tool is not None
        assert scheduling_tool is not None
    
    def test_tools_have_common_interface(self):
        """Test that all tools implement the common interface"""
        video_tool = VideoAnalysisTool()
        audio_tool = AudioProcessingTool()
        scheduling_tool = ContentSchedulingTool()
        
        # All should have execute method
        assert hasattr(video_tool, 'execute')
        assert hasattr(audio_tool, 'execute')
        assert hasattr(scheduling_tool, 'execute')
        
        # All should have get_status method
        assert hasattr(video_tool, 'get_status')
        assert hasattr(audio_tool, 'get_status')
        assert hasattr(scheduling_tool, 'get_status')
        
        # All should have get_performance_metrics method
        assert hasattr(video_tool, 'get_performance_metrics')
        assert hasattr(audio_tool, 'get_performance_metrics')
        assert hasattr(scheduling_tool, 'get_performance_metrics')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
