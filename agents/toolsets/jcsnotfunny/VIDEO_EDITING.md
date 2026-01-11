# Video Editing Toolsets

This document provides detailed documentation for all video editing tools available to the Video Editor agent.

## Tools Overview

| Tool Name        | Description                                                            | Status |
| ---------------- | ---------------------------------------------------------------------- | ------ |
| `video_analysis` | Analyze video footage for speaker detection and optimal cutting points | Active |
| `auto_cut`       | Automatically cut between camera angles based on speaker activity      | Active |
| `create_short`   | Generate short-form content from long-form podcast                     | Active |
| `add_overlays`   | Add text overlays, lower thirds, and visual elements                   | Active |

---

## video_analysis

Analyzes video footage to identify speakers, optimal cut points, and engagement scoring.

### Parameters

| Parameter       | Type   | Required | Description                       |
| --------------- | ------ | -------- | --------------------------------- |
| `video_path`    | string | Yes      | Path to the video file to analyze |
| `analysis_type` | enum   | No       | Type of analysis to perform       |

### Analysis Types

- `speaker_detection` - Identify and track speakers using facial detection
- `engagement_scoring` - Score segments based on viewer engagement potential
- `optimal_cut_points` - Identify the best points to cut between camera angles

### Example Usage

```json
{
  "video_path": "/path/to/footage/episode_001.mp4",
  "analysis_type": "speaker_detection"
}
```

### Output

Returns a JSON object containing:

- Speaker positions and timestamps
- Engagement scores for each segment
- Recommended cut points

---

## auto_cut

Automatically cuts between camera angles based on speaker activity and visual analysis.

### Parameters

| Parameter       | Type   | Required | Description                    |
| --------------- | ------ | -------- | ------------------------------ |
| `input_video`   | string | Yes      | Path to the input video file   |
| `output_video`  | string | Yes      | Path for the output video file |
| `cutting_style` | enum   | No       | Style of cutting to apply      |

### Cutting Styles

- `dynamic` - Frequent cuts, high energy
- `conservative` - Moderate cuts, focuses on speaker stability
- `aggressive` - Very frequent cuts, maximum engagement

### Example Usage

```json
{
  "input_video": "/path/to/raw_footage.mp4",
  "output_video": "/path/to/cut_footage.mp4",
  "cutting_style": "dynamic"
}
```

---

## create_short

Generates short-form content (60-120 seconds) from long-form podcast episodes.

### Parameters

| Parameter      | Type   | Required | Description                              |
| -------------- | ------ | -------- | ---------------------------------------- |
| `source_video` | string | Yes      | Path to the source video                 |
| `duration`     | number | No       | Target duration in seconds (default: 90) |
| `focus_topic`  | string | No       | Topic to focus on for the short          |
| `platform`     | enum   | No       | Target platform for optimization         |

### Target Platforms

- `tiktok` - 9:16 vertical format, max 3 minutes
- `instagram` - 1:1 or 4:5 format, max 90 seconds
- `youtube_shorts` - 9:16 vertical format, max 60 seconds

### Example Usage

```json
{
  "source_video": "/path/to/episode_full.mp4",
  "duration": 60,
  "focus_topic": "comedy clip",
  "platform": "tiktok"
}
```

---

## add_overlays

Adds text overlays, lower thirds, branding elements, and visual effects.

### Parameters

| Parameter        | Type   | Required | Description                |
| ---------------- | ------ | -------- | -------------------------- |
| `video_path`     | string | Yes      | Path to the video file     |
| `overlay_config` | object | Yes      | Configuration for overlays |

### Overlay Configuration

```json
{
  "lower_third": {
    "enabled": true,
    "style": "modern",
    "position": "bottom_left"
  },
  "branding": {
    "enabled": true,
    "logo_path": "/path/to/logo.png",
    "position": "top_right"
  },
  "captions": {
    "enabled": true,
    "style": "styled",
    "font": "Inter"
  },
  "timestamps": {
    "enabled": false
  }
}
```

### Example Usage

```json
{
  "video_path": "/path/to/video.mp4",
  "overlay_config": {
    "lower_third": {
      "enabled": true,
      "style": "modern",
      "text": "Guest Name - Title"
    },
    "branding": {
      "enabled": true,
      "logo_path": "/assets/logo.png"
    }
  }
}
```

---

## Workflow Integration

### Episode Edit Workflow

```
video_analysis → auto_cut → add_overlays → export_final
```

### Short Creation Workflow

```
video_analysis → create_short → add_captions → optimize_for_platform
```

---

## Best Practices

1. **Always run video_analysis first** - This provides data for all subsequent operations
2. **Match cutting style to content** - Use `conservative` for interviews, `dynamic` for comedy
3. **Optimize for platform** - Different platforms have different aspect ratio requirements
4. **Test overlay positions** - Ensure text doesn't cover important visual elements
