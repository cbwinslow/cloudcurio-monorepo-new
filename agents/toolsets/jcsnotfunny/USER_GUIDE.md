# Podcast Production Toolset - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Typical Workflows](#typical-workflows)
4. [Tool Overview](#tool-overview)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

The Podcast Production Toolset provides three powerful tools for automating podcast production workflows:

- **Video Analysis Tool**: Analyze video footage for speaker detection and optimal editing
- **Audio Processing Tool**: Clean, enhance, and master audio for distribution
- **Content Scheduling Tool**: Schedule and manage multi-platform social media posts

These tools are designed to work together to streamline your podcast production from recording to distribution.

---

## Getting Started

### Prerequisites

Before using the tools, ensure you have:

1. **Python 3.10 or higher** installed
2. **FFmpeg** installed (for video and audio tools)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```
3. The toolset package installed in your Python environment

### Installation

```bash
# Navigate to the repository
cd /path/to/cloudcurio-monorepo-new

# Install the package
pip install -e .
```

### Basic Setup

```python
from agents.toolsets.jcsnotfunny import (
    VideoAnalysisTool,
    AudioProcessingTool,
    ContentSchedulingTool
)

# Initialize tools
video_tool = VideoAnalysisTool()
audio_tool = AudioProcessingTool()
scheduling_tool = ContentSchedulingTool()
```

---

## Typical Workflows

### Workflow 1: Complete Episode Production

This workflow takes you from raw footage to published content.

```python
from datetime import datetime, timedelta

# Step 1: Analyze raw video
print("Step 1: Analyzing video...")
video_analysis = video_tool.execute(
    video_path='/path/to/raw_footage.mp4',
    analysis_type='full'
)

print(f"✓ Detected {video_analysis['speaker_detection']['speakers_detected']} speakers")
print(f"✓ Found {len(video_analysis['cut_points'])} optimal cut points")

# Step 2: Clean up audio
print("\nStep 2: Cleaning audio...")
audio_cleanup = audio_tool.execute(
    operation='cleanup',
    audio_path='/path/to/raw_audio.wav',
    noise_reduction='medium',
    hum_removal=True
)

print(f"✓ Audio cleaned: {audio_cleanup['output_path']}")

# Step 3: Enhance audio
print("\nStep 3: Enhancing audio...")
audio_enhanced = audio_tool.execute(
    operation='enhance',
    audio_path=audio_cleanup['output_path'],
    preset='podcast'
)

print(f"✓ Audio enhanced: {audio_enhanced['output_path']}")

# Step 4: Master audio for distribution
print("\nStep 4: Mastering audio...")
audio_mastered = audio_tool.execute(
    operation='master',
    audio_path=audio_enhanced['output_path'],
    target_lufs=-16
)

print(f"✓ Audio mastered: {audio_mastered['output_path']}")

# Step 5: Schedule social media posts
print("\nStep 5: Scheduling social media posts...")

# Schedule announcement 1 hour after current time
announcement_time = (datetime.now() + timedelta(hours=1)).isoformat()

schedule_result = scheduling_tool.execute(
    operation='schedule',
    content='🎙️ New episode out now! Check out our conversation about...',
    platforms=['twitter', 'instagram', 'linkedin'],
    schedule_time=announcement_time,
    media_paths=['/path/to/episode_cover.jpg'],
    tags=['podcast', 'newepisode']
)

print(f"✓ Post scheduled (ID: {schedule_result['post_id']})")
print("\n✅ Episode production complete!")
```

### Workflow 2: Sponsored Content Production

This workflow handles sponsor integration and multi-post campaigns.

```python
# Step 1: Clean main audio
main_audio = audio_tool.execute(
    operation='cleanup',
    audio_path='/path/to/episode_audio.wav'
)

# Step 2: Prepare sponsor read
sponsor_audio = audio_tool.execute(
    operation='enhance',
    audio_path='/path/to/sponsor_read.wav',
    preset='podcast'
)

# Step 3: Insert sponsor at specific timestamps
final_audio = audio_tool.execute(
    operation='insert_sponsor',
    audio_path=main_audio['output_path'],
    sponsor_audio=sponsor_audio['output_path'],
    insertion_points=[180.0, 1200.0],  # 3 min and 20 min marks
    transition_duration=1.5
)

print(f"✓ Sponsor inserted: {final_audio['output_path']}")

# Step 4: Master final audio
mastered = audio_tool.execute(
    operation='master',
    audio_path=final_audio['output_path']
)

# Step 5: Schedule sponsor acknowledgment posts
sponsor_post_time = (datetime.now() + timedelta(hours=2)).isoformat()

scheduling_tool.execute(
    operation='schedule',
    content='Big thanks to @SponsorName for supporting the show! Use code PODCAST10 for 10% off.',
    platforms=['twitter', 'instagram'],
    schedule_time=sponsor_post_time,
    tags=['sponsored', 'ad']
)

print("✅ Sponsored content production complete!")
```

### Workflow 3: Content Calendar Management

This workflow helps you plan and optimize your posting schedule.

```python
from datetime import date

# Step 1: Generate content calendar for the month
calendar = scheduling_tool.execute(
    operation='calendar',
    start_date='2024-03-01',
    end_date='2024-03-31'
)

print(f"Content calendar: {calendar['total_posts']} posts scheduled")

# Step 2: Identify low-engagement days
for date_str, day_data in calendar['calendar'].items():
    if day_data['post_count'] == 0:
        print(f"⚠️ No posts scheduled for {date_str}")
        print(f"   Recommended times: {day_data['recommended_times'][:2]}")

# Step 3: Optimize existing schedule
optimization = scheduling_tool.execute(
    operation='optimize',
    date='2024-03-15'
)

print(f"\nOptimization opportunities: {optimization['improvement_potential']}")
for suggestion in optimization['suggestions']:
    print(f"  Post {suggestion['post_id']}")
    print(f"    Move from {suggestion['current_time']}")
    print(f"    to {suggestion['suggested_time']}")
    print(f"    Reason: {suggestion['reason']}")

# Step 4: Check for conflicts before scheduling new post
conflict_check = scheduling_tool.execute(
    operation='check_conflicts',
    schedule_time='2024-03-15T14:00:00',
    platforms=['twitter']
)

if conflict_check['has_conflicts']:
    print("\n⚠️ Conflicts detected!")
    print("Alternative times:", conflict_check['alternative_times'])
else:
    print("\n✓ No conflicts - safe to schedule")
```

### Workflow 4: Batch Processing Multiple Episodes

This workflow efficiently processes multiple episodes.

```python
import glob
from pathlib import Path

# Get all episode files
episode_files = glob.glob('/path/to/episodes/*.wav')

print(f"Found {len(episode_files)} episodes to process")

for episode_file in episode_files:
    episode_name = Path(episode_file).stem
    print(f"\nProcessing: {episode_name}")
    
    try:
        # Clean
        cleaned = audio_tool.execute(
            operation='cleanup',
            audio_path=episode_file,
            noise_reduction='medium'
        )
        
        # Enhance
        enhanced = audio_tool.execute(
            operation='enhance',
            audio_path=cleaned['output_path'],
            preset='podcast'
        )
        
        # Master
        mastered = audio_tool.execute(
            operation='master',
            audio_path=enhanced['output_path']
        )
        
        print(f"  ✓ {episode_name} complete: {mastered['output_path']}")
        
    except Exception as e:
        print(f"  ✗ {episode_name} failed: {e}")
        continue

print("\n✅ Batch processing complete!")
```

---

## Tool Overview

### Video Analysis Tool

**Purpose**: Analyze video footage to identify speakers, engagement moments, and optimal editing points.

**Key Features**:
- Speaker detection and tracking
- Engagement scoring
- Optimal cut point identification
- Technical quality analysis

**When to Use**:
- Before editing multi-camera footage
- To identify highlight moments
- For quality assurance checks

**Example**:
```python
result = video_tool.execute(
    video_path='/path/to/footage.mp4',
    analysis_type='full'
)

# Use cut points for editing
for cut in result['cut_points']:
    print(f"Cut at {cut['time']}s - {cut['reason']}")
```

### Audio Processing Tool

**Purpose**: Clean, enhance, and prepare audio for distribution.

**Key Operations**:
- **cleanup**: Remove noise and artifacts
- **enhance**: Improve vocal clarity
- **insert_sponsor**: Add sponsor reads
- **master**: Finalize for distribution
- **normalize**: Adjust levels
- **convert**: Change formats

**When to Use**:
- After recording to clean audio
- Before distribution to ensure quality
- When adding sponsored content

**Example**:
```python
# Complete audio pipeline
cleaned = audio_tool.execute(operation='cleanup', audio_path='raw.wav')
enhanced = audio_tool.execute(operation='enhance', audio_path=cleaned['output_path'])
mastered = audio_tool.execute(operation='master', audio_path=enhanced['output_path'])
```

### Content Scheduling Tool

**Purpose**: Manage multi-platform social media posting schedule.

**Key Operations**:
- **schedule**: Schedule new posts
- **calendar**: View posting calendar
- **check_conflicts**: Detect scheduling conflicts
- **optimize**: Improve post timing
- **list**: View scheduled posts
- **cancel**: Remove scheduled posts

**When to Use**:
- Planning content campaigns
- Coordinating multi-platform posts
- Optimizing engagement timing

**Example**:
```python
# Schedule coordinated posts
for platform in ['twitter', 'instagram', 'tiktok']:
    scheduling_tool.execute(
        operation='schedule',
        content=f'Episode out now!',
        platforms=[platform],
        schedule_time='2024-03-15T14:00:00'
    )
```

---

## Best Practices

### 1. Always Validate Input Files

```python
import os

def process_episode(audio_path):
    # Check file exists
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        return None
    
    # Check file size
    size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if size_mb > 1000:
        print(f"Warning: Large file ({size_mb:.1f}MB) may take time to process")
    
    # Process
    return audio_tool.execute(operation='cleanup', audio_path=audio_path)
```

### 2. Use Appropriate Quality Settings

```python
# Development/testing - fast processing
dev_result = audio_tool.execute(
    operation='enhance',
    audio_path='test.wav',
    preset='podcast'
)

# Production - high quality
prod_result = audio_tool.execute(
    operation='master',
    audio_path='final.wav',
    target_lufs=-16,
    true_peak=-1.5
)
```

### 3. Handle Errors Gracefully

```python
from agents.toolsets.jcsnotfunny import AudioProcessingError

def safe_process(audio_path):
    try:
        result = audio_tool.execute(
            operation='cleanup',
            audio_path=audio_path
        )
        return result
    except AudioProcessingError as e:
        print(f"Processing failed: {e.message}")
        print("Suggestions:")
        for suggestion in e.recovery_suggestions:
            print(f"  - {suggestion}")
        return None
```

### 4. Monitor Performance

```python
import time

start = time.time()
result = video_tool.execute(
    video_path='large_file.mp4',
    analysis_type='full'
)
elapsed = time.time() - start

print(f"Analysis took {elapsed:.2f}s")

# Check tool-reported performance
perf = result['performance']
print(f"Tool execution time: {perf['execution_time']:.2f}s")
```

### 5. Organize Output Files

```python
from pathlib import Path
from datetime import datetime

# Create organized output structure
date_str = datetime.now().strftime('%Y-%m-%d')
output_dir = Path(f'/podcast/episodes/{date_str}')
output_dir.mkdir(parents=True, exist_ok=True)

# Process with organized output
result = audio_tool.execute(
    operation='master',
    audio_path='episode.wav',
    output_path=str(output_dir / 'episode_mastered.mp3')
)
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: FFmpeg Not Found

**Error**: `VideoAnalysisError: FFmpeg/FFprobe not found or not working`

**Solution**:
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS

# Or specify custom path
config = {'ffmpeg_path': '/usr/local/bin/ffmpeg'}
tool = VideoAnalysisTool(config=config)
```

#### Issue: File Too Large

**Error**: `VideoAnalysisError: Video file too large: 6000MB exceeds limit of 5000MB`

**Solution**:
```python
# Option 1: Increase limit
config = {'max_file_size_mb': 10000}
tool = VideoAnalysisTool(config=config)

# Option 2: Split video into segments
# (Use external video editing tool)
```

#### Issue: Scheduling Conflict

**Error**: `SchedulingConflictError: Scheduling conflict detected`

**Solution**:
```python
# Check conflicts first
conflict_check = scheduling_tool.execute(
    operation='check_conflicts',
    schedule_time=desired_time,
    platforms=['twitter']
)

if conflict_check['has_conflicts']:
    # Use alternative time
    alt_time = conflict_check['alternative_times'][0]
    scheduling_tool.execute(
        operation='schedule',
        content=content,
        platforms=['twitter'],
        schedule_time=alt_time
    )
```

#### Issue: Poor Audio Quality

**Problem**: Audio still has noise after cleanup

**Solution**:
```python
# Try aggressive noise reduction
result = audio_tool.execute(
    operation='cleanup',
    audio_path='noisy.wav',
    noise_reduction='aggressive',  # Instead of 'medium'
    hum_removal=True
)

# Then enhance with appropriate preset
enhanced = audio_tool.execute(
    operation='enhance',
    audio_path=result['output_path'],
    preset='podcast',
    compression_ratio=6  # Increase compression
)
```

#### Issue: Slow Processing

**Problem**: Processing takes too long

**Solutions**:
```python
# 1. Use quick analysis when possible
result = video_tool.execute(
    video_path='video.mp4',
    analysis_type='quick'  # Instead of 'full'
)

# 2. Process smaller segments
# Split large files into smaller chunks

# 3. Monitor and log performance
start = time.time()
result = tool.execute(...)
print(f"Processing took {time.time() - start:.2f}s")
```

### Getting Help

1. **Check Error Messages**: Error messages include recovery suggestions
2. **Review Logs**: Tools log detailed information
3. **Consult API Documentation**: See `API_DOCUMENTATION.md`
4. **Check Configuration**: Verify tool configuration settings

---

## Tips and Tricks

### 1. Create Reusable Configurations

```python
# Save configurations for different scenarios
CONFIGS = {
    'dev': {
        'max_file_size_mb': 100,
        'temp_dir': '/tmp/dev'
    },
    'prod': {
        'max_file_size_mb': 5000,
        'temp_dir': '/var/podcast/temp'
    }
}

# Use appropriate config
env = 'prod'
tool = VideoAnalysisTool(config=CONFIGS[env])
```

### 2. Chain Operations Efficiently

```python
def process_audio_pipeline(input_path):
    """Complete audio processing pipeline"""
    
    # Cleanup
    cleaned = audio_tool.execute(
        operation='cleanup',
        audio_path=input_path,
        noise_reduction='medium'
    )
    
    # Enhance
    enhanced = audio_tool.execute(
        operation='enhance',
        audio_path=cleaned['output_path'],
        preset='podcast'
    )
    
    # Master
    final = audio_tool.execute(
        operation='master',
        audio_path=enhanced['output_path']
    )
    
    return final['output_path']
```

### 3. Use Scheduling Optimization

```python
# Instead of manually choosing times,
# let the tool optimize your schedule
optimization = scheduling_tool.execute(
    operation='optimize',
    date='2024-03-15'
)

# Review and apply suggestions
for suggestion in optimization['suggestions']:
    # Reschedule to suggested time
    pass
```

---

## Next Steps

1. **Read the API Documentation**: See `API_DOCUMENTATION.md` for detailed API reference
2. **Try the Example Workflows**: Start with the workflows in this guide
3. **Customize for Your Needs**: Adapt the tools to your specific workflow
4. **Monitor and Optimize**: Track performance and optimize your processes

---

## Version Information

- **Guide Version:** 1.0.0
- **Last Updated:** 2026-01-24
- **Compatible With:** Toolset v1.0.0+

---

For technical details, see `API_DOCUMENTATION.md`. For implementation details, see the tool source files in the `jcsnotfunny` directory.
