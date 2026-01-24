# Core Tools API Documentation

This document provides comprehensive API documentation for the three core podcast production tools.

## Table of Contents

1. [Video Analysis Tool](#video-analysis-tool)
2. [Audio Processing Tool](#audio-processing-tool)
3. [Content Scheduling Tool](#content-scheduling-tool)

---

## Video Analysis Tool

### Overview

The VideoAnalysisTool provides comprehensive video analysis capabilities for podcast production, including speaker detection, engagement scoring, optimal cut points identification, and scene segmentation.

### Installation & Setup

```python
from agents.toolsets.jcsnotfunny import VideoAnalysisTool

# Basic initialization
tool = VideoAnalysisTool()

# With custom configuration
config = {
    'ffmpeg_path': '/usr/bin/ffmpeg',
    'ffprobe_path': '/usr/bin/ffprobe',
    'temp_dir': '/custom/temp',
    'max_file_size_mb': 3000,
    'supported_formats': ['mp4', 'mov', 'avi']
}
tool = VideoAnalysisTool(config=config)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ffmpeg_path` | str | 'ffmpeg' | Path to ffmpeg binary |
| `ffprobe_path` | str | 'ffprobe' | Path to ffprobe binary |
| `temp_dir` | str | '/tmp/video_analysis' | Temporary directory for analysis |
| `max_file_size_mb` | int | 5000 | Maximum file size in MB |
| `supported_formats` | list | ['mp4', 'mov', 'avi', 'mkv'] | Supported video formats |

### Methods

#### execute(video_path, analysis_type='full', **kwargs)

Execute video analysis on the specified file.

**Parameters:**
- `video_path` (str, required): Path to the video file to analyze
- `analysis_type` (str, optional): Type of analysis to perform
  - `'quick'`: Basic metadata and technical analysis
  - `'full'`: Complete analysis with all features (default)
  - `'speaker'`: Focus on speaker detection
  - `'cuts'`: Focus on optimal cut points
- `**kwargs`: Additional analysis parameters

**Returns:**
Dict containing analysis results:
```python
{
    'status': 'success',
    'analysis_type': 'full',
    'video_path': '/path/to/video.mp4',
    'metadata': {...},
    'speaker_detection': {...},
    'cut_points': [...],
    'engagement_scores': {...},
    'recommendations': [...],
    'performance': {...}
}
```

**Raises:**
- `VideoAnalysisError`: If analysis fails

**Example:**
```python
# Quick analysis
result = tool.execute(
    video_path='/path/to/episode.mp4',
    analysis_type='quick'
)

# Full analysis
result = tool.execute(
    video_path='/path/to/episode.mp4',
    analysis_type='full'
)

print(f"Duration: {result['metadata']['duration']}s")
print(f"Resolution: {result['metadata']['video']['width']}x{result['metadata']['video']['height']}")
print(f"Recommendations: {result['recommendations']}")
```

### Output Structure

#### Quick Analysis Output

```python
{
    'status': 'success',
    'analysis_type': 'quick',
    'video_path': '/path/to/video.mp4',
    'metadata': {
        'filename': 'video.mp4',
        'format': 'mp4',
        'duration': 120.5,
        'size': 104857600,
        'bit_rate': 1048576,
        'video': {
            'codec': 'h264',
            'width': 1920,
            'height': 1080,
            'fps': 30.0,
            'aspect_ratio': '16:9'
        },
        'audio': {
            'codec': 'aac',
            'sample_rate': 48000,
            'channels': 2,
            'bit_rate': 128000
        }
    },
    'recommendations': [
        'Video meets quality standards'
    ]
}
```

#### Full Analysis Output

Includes all quick analysis data plus:
```python
{
    'speaker_detection': {
        'speakers_detected': 2,
        'confidence': 0.85,
        'segments': [
            {
                'speaker_id': 1,
                'start_time': 0.0,
                'end_time': 30.5,
                'position': 'left'
            }
        ]
    },
    'cut_points': [
        {
            'time': 10.5,
            'confidence': 0.9,
            'reason': 'speaker_change'
        }
    ],
    'engagement_scores': {
        'overall_score': 0.75,
        'segments': [...]
    }
}
```

### Error Handling

```python
from agents.toolsets.jcsnotfunny import VideoAnalysisError

try:
    result = tool.execute(video_path='/path/to/video.mp4')
except VideoAnalysisError as e:
    print(f"Analysis failed: {e.message}")
    print(f"Context: {e.context}")
    print(f"Suggestions: {e.recovery_suggestions}")
```

---

## Audio Processing Tool

### Overview

The AudioProcessingTool provides comprehensive audio processing capabilities including noise reduction, voice enhancement, sponsor insertion, and audio mastering.

### Installation & Setup

```python
from agents.toolsets.jcsnotfunny import AudioProcessingTool

# Basic initialization
tool = AudioProcessingTool()

# With custom configuration
config = {
    'ffmpeg_path': '/usr/bin/ffmpeg',
    'temp_dir': '/custom/temp',
    'max_file_size_mb': 500,
    'default_sample_rate': 44100,
    'default_bit_rate': '256k'
}
tool = AudioProcessingTool(config=config)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ffmpeg_path` | str | 'ffmpeg' | Path to ffmpeg binary |
| `temp_dir` | str | '/tmp/audio_processing' | Temporary directory |
| `max_file_size_mb` | int | 1000 | Maximum file size in MB |
| `supported_formats` | list | ['mp3', 'wav', 'flac', 'm4a', 'aac'] | Supported formats |
| `default_sample_rate` | int | 48000 | Default sample rate |
| `default_bit_rate` | str | '192k' | Default bit rate |

### Methods

#### execute(operation, audio_path, output_path=None, **kwargs)

Execute audio processing operation.

**Parameters:**
- `operation` (str, required): Operation to perform
  - `'cleanup'`: Remove background noise and artifacts
  - `'enhance'`: Enhance voice quality (EQ, compression, de-essing)
  - `'insert_sponsor'`: Insert sponsor read at specific points
  - `'master'`: Master audio for distribution
  - `'convert'`: Convert audio format
  - `'normalize'`: Normalize audio levels
- `audio_path` (str, required): Path to the input audio file
- `output_path` (str, optional): Path for output (auto-generated if not provided)
- `**kwargs`: Operation-specific parameters

**Returns:**
Dict containing processing results

**Raises:**
- `AudioProcessingError`: If processing fails

### Operation Examples

#### Cleanup Audio

```python
result = tool.execute(
    operation='cleanup',
    audio_path='/path/to/raw_audio.wav',
    noise_reduction='medium',  # 'light', 'medium', 'aggressive'
    hum_removal=True
)

print(f"Output: {result['output_path']}")
print(f"File size: {result['file_size']} bytes")
```

#### Enhance Audio

```python
result = tool.execute(
    operation='enhance',
    audio_path='/path/to/audio.wav',
    preset='podcast',  # 'podcast', 'interview', 'narration'
    compression_ratio=4,
    de_essing=0.6
)
```

#### Insert Sponsor

```python
result = tool.execute(
    operation='insert_sponsor',
    audio_path='/path/to/main_audio.wav',
    sponsor_audio='/path/to/sponsor_read.wav',
    insertion_points=[120.5, 360.0],  # Timestamps in seconds
    transition_duration=1.0
)
```

#### Master Audio

```python
result = tool.execute(
    operation='master',
    audio_path='/path/to/processed_audio.wav',
    target_lufs=-16,
    true_peak=-1.5
)
```

#### Convert Audio

```python
result = tool.execute(
    operation='convert',
    audio_path='/path/to/audio.wav',
    output_path='/path/to/audio.mp3',
    target_format='mp3',
    sample_rate=44100,
    bit_rate='320k'
)
```

#### Normalize Audio

```python
result = tool.execute(
    operation='normalize',
    audio_path='/path/to/audio.wav',
    method='lufs'  # 'peak' or 'lufs'
)
```

### Output Structure

```python
{
    'status': 'success',
    'operation': 'enhance',
    'input_path': '/path/to/input.wav',
    'output_path': '/tmp/audio_processing/input_enhance.mp3',
    'preset': 'podcast',
    'compression_ratio': 4,
    'de_essing': 0.6,
    'file_size': 12345678,
    'performance': {...}
}
```

### Error Handling

```python
from agents.toolsets.jcsnotfunny import AudioProcessingError

try:
    result = tool.execute(operation='cleanup', audio_path='/path/to/audio.mp3')
except AudioProcessingError as e:
    print(f"Processing failed: {e.message}")
    print(f"Suggestions: {e.recovery_suggestions}")
```

---

## Content Scheduling Tool

### Overview

The ContentSchedulingTool provides multi-platform content scheduling capabilities including calendar management, conflict detection, and optimal timing recommendations.

### Installation & Setup

```python
from agents.toolsets.jcsnotfunny import ContentSchedulingTool

# Basic initialization
tool = ContentSchedulingTool()

# With custom configuration
config = {
    'supported_platforms': ['twitter', 'instagram', 'tiktok'],
    'max_posts_per_day': 5,
    'min_interval_minutes': 120,
    'working_hours_start': 8,
    'working_hours_end': 20,
    'timezone': 'America/New_York'
}
tool = ContentSchedulingTool(config=config)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `supported_platforms` | list | ['twitter', 'instagram', 'tiktok', 'youtube', 'linkedin', 'facebook'] | Supported platforms |
| `max_posts_per_day` | int | 10 | Maximum posts per day |
| `min_interval_minutes` | int | 60 | Minimum interval between posts |
| `working_hours_start` | int | 9 | Working hours start (0-23) |
| `working_hours_end` | int | 18 | Working hours end (0-24) |
| `timezone` | str | 'UTC' | Timezone for scheduling |

### Methods

#### execute(operation, **kwargs)

Execute content scheduling operation.

**Parameters:**
- `operation` (str, required): Operation to perform
  - `'schedule'`: Schedule a new post
  - `'calendar'`: Generate content calendar
  - `'check_conflicts'`: Check for scheduling conflicts
  - `'optimize'`: Optimize posting schedule
  - `'cancel'`: Cancel a scheduled post
  - `'list'`: List scheduled posts
- `**kwargs`: Operation-specific parameters

**Returns:**
Dict containing operation results

**Raises:**
- `SchedulingError`: For general scheduling failures
- `SchedulingConflictError`: When conflicts are detected
- `SchedulingValidationError`: For validation errors

### Operation Examples

#### Schedule a Post

```python
from datetime import datetime, timedelta

future_time = (datetime.now() + timedelta(hours=2)).isoformat()

result = tool.execute(
    operation='schedule',
    content='Check out our latest episode!',
    platforms=['twitter', 'instagram'],
    schedule_time=future_time,
    media_paths=['/path/to/image.jpg'],
    tags=['podcast', 'newepisode']
)

print(f"Post ID: {result['post_id']}")
print(f"Recommendations: {result['recommendation']}")
```

#### Generate Calendar

```python
result = tool.execute(
    operation='calendar',
    start_date='2024-03-01',
    end_date='2024-03-31',
    platforms=['twitter', 'instagram']
)

print(f"Total posts: {result['total_posts']}")
for date, data in result['calendar'].items():
    print(f"{date}: {data['post_count']} posts")
```

#### Check Conflicts

```python
result = tool.execute(
    operation='check_conflicts',
    schedule_time='2024-03-15T14:00:00',
    platforms=['twitter']
)

if result['has_conflicts']:
    print("Conflicts found:")
    for conflict in result['conflicts']:
        print(f"  - {conflict}")
    print("Alternative times:", result['alternative_times'])
```

#### Optimize Schedule

```python
result = tool.execute(
    operation='optimize',
    date='2024-03-15',
    platforms=['twitter', 'instagram']
)

print(f"Improvement potential: {result['improvement_potential']}")
for suggestion in result['suggestions']:
    print(f"Post {suggestion['post_id']}:")
    print(f"  Current: {suggestion['current_time']}")
    print(f"  Suggested: {suggestion['suggested_time']}")
    print(f"  Reason: {suggestion['reason']}")
```

#### List Posts

```python
# List all posts
result = tool.execute(operation='list')

# List posts for specific date
result = tool.execute(
    operation='list',
    date='2024-03-15'
)

# List posts for specific platform
result = tool.execute(
    operation='list',
    platform='twitter'
)

print(f"Found {result['post_count']} posts")
for post in result['posts']:
    print(f"  {post['post_id']}: {post['content'][:50]}...")
```

#### Cancel Post

```python
result = tool.execute(
    operation='cancel',
    post_id='post_abc123'
)

print(result['message'])
```

### Output Structures

#### Schedule Post Output

```python
{
    'status': 'success',
    'operation': 'schedule',
    'post_id': 'post_abc123',
    'post_entry': {
        'post_id': 'post_abc123',
        'content': 'Check out our latest episode!',
        'platforms': ['twitter', 'instagram'],
        'schedule_time': '2024-03-15T14:00:00',
        'media_paths': ['/path/to/image.jpg'],
        'tags': ['podcast', 'newepisode'],
        'status': 'scheduled',
        'created_at': '2024-03-14T10:30:00'
    },
    'conflicts': [],
    'recommendation': {
        'is_optimal_time': True,
        'engagement_estimate': 'high',
        'tips': [...]
    }
}
```

#### Calendar Output

```python
{
    'status': 'success',
    'operation': 'calendar',
    'start_date': '2024-03-01',
    'end_date': '2024-03-31',
    'calendar': {
        '2024-03-01': {
            'date': '2024-03-01',
            'posts': [...],
            'post_count': 3,
            'capacity': 7,
            'recommended_times': [...]
        }
    },
    'total_posts': 45
}
```

### Error Handling

```python
from agents.toolsets.jcsnotfunny import (
    SchedulingError,
    SchedulingConflictError,
    SchedulingValidationError
)

try:
    result = tool.execute(
        operation='schedule',
        content='Test post',
        platforms=['twitter'],
        schedule_time='2024-03-15T14:00:00'
    )
except SchedulingConflictError as e:
    print(f"Conflict detected: {e.message}")
    print(f"Conflicts: {e.context['conflicts']}")
except SchedulingValidationError as e:
    print(f"Validation error: {e.message}")
except SchedulingError as e:
    print(f"Scheduling error: {e.message}")
```

---

## Common Patterns

### Error Handling Pattern

All tools follow the same error handling pattern:

```python
from agents.toolsets.jcsnotfunny import ToolError

try:
    result = tool.execute(...)
except ToolError as e:
    # All tool errors provide:
    print(f"Error type: {e.error_type}")
    print(f"Message: {e.message}")
    print(f"Context: {e.context}")
    print(f"Recovery suggestions: {e.recovery_suggestions}")
    
    # Log the error
    e.log_error(logger)
```

### Performance Monitoring Pattern

All tools track performance metrics:

```python
result = tool.execute(...)

# Get performance metrics
metrics = result['performance']
print(f"Execution time: {metrics['execution_time']}s")
print(f"Start time: {metrics['start_time']}")
print(f"End time: {metrics['end_time']}")
```

### Tool Status Pattern

All tools provide status information:

```python
status = tool.get_status()
print(f"Tool: {status['tool_name']}")
print(f"Status: {status['status']}")
print(f"Last error: {status['last_error']}")
```

---

## Best Practices

### 1. Always Handle Errors

```python
try:
    result = tool.execute(...)
    # Process result
except ToolError as e:
    # Handle error gracefully
    logger.error(f"Tool execution failed: {e.message}")
    # Take recovery action based on suggestions
```

### 2. Use Configuration for Production

```python
# Development
dev_config = {
    'max_file_size_mb': 100,
    'temp_dir': '/tmp/dev'
}

# Production
prod_config = {
    'max_file_size_mb': 5000,
    'temp_dir': '/var/podcast/temp',
    'ffmpeg_path': '/usr/local/bin/ffmpeg'
}

tool = VideoAnalysisTool(config=prod_config)
```

### 3. Monitor Performance

```python
result = tool.execute(...)

if result['performance']['execution_time'] > 60:
    logger.warning(f"Tool execution took {result['performance']['execution_time']}s")
```

### 4. Clean Up Temp Files

```python
import shutil

result = tool.execute(...)
# Process result...

# Clean up if needed
if hasattr(tool, 'temp_dir'):
    # Remove only specific files, not the entire directory
    pass
```

### 5. Use Appropriate Analysis Types

```python
# Quick analysis for validation
quick = video_tool.execute(video_path, analysis_type='quick')
if quick['metadata']['duration'] > 3600:
    # Video too long
    return

# Full analysis only when needed
full = video_tool.execute(video_path, analysis_type='full')
```

---

## Troubleshooting

### Common Issues

#### FFmpeg Not Found

```
VideoAnalysisError: FFmpeg/FFprobe not found or not working
```

**Solution:** Install ffmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Or specify custom path
config = {'ffmpeg_path': '/usr/local/bin/ffmpeg'}
```

#### File Too Large

```
VideoAnalysisError: Video file too large
```

**Solution:** Increase limit or split file
```python
config = {'max_file_size_mb': 10000}
# Or split video into smaller segments
```

#### Scheduling Conflict

```
SchedulingConflictError: Scheduling conflict detected
```

**Solution:** Use alternative times
```python
result = tool.execute(operation='check_conflicts', ...)
alternative_times = result['alternative_times']
# Use one of the suggested times
```

---

## Version Information

- **API Version:** 1.0.0
- **Last Updated:** 2026-01-24
- **Python Version:** 3.10+
- **Dependencies:** ffmpeg (for video/audio tools)

---

## Support

For issues, questions, or feature requests:
1. Check this documentation
2. Review error messages and recovery suggestions
3. Check tool logs for detailed information
4. Consult the implementation guides in the toolset directory
