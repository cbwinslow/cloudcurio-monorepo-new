# Audio Production Toolsets

This document provides detailed documentation for all audio production tools available to the Audio Engineer agent.

## Tools Overview

| Tool Name           | Description                                          | Status |
| ------------------- | ---------------------------------------------------- | ------ |
| `audio_cleanup`     | Remove background noise, hum, and unwanted artifacts | Active |
| `voice_enhancement` | Enhance vocal clarity and presence                   | Active |
| `sponsor_insertion` | Insert sponsor reads at optimal points               | Active |
| `audio_mastering`   | Master final audio for distribution                  | Active |

---

## audio_cleanup

Removes background noise, hum, and unwanted artifacts from audio tracks.

### Parameters

| Parameter               | Type   | Required | Description                     |
| ----------------------- | ------ | -------- | ------------------------------- |
| `audio_file`            | string | Yes      | Path to the audio file to clean |
| `noise_reduction_level` | enum   | No       | Intensity of noise reduction    |

### Noise Reduction Levels

- `light` - Subtle cleanup, preserves natural sound
- `medium` - Moderate cleanup for typical environments
- `aggressive` - Heavy cleanup for noisy environments

### Example Usage

```json
{
  "audio_file": "/path/to/raw_audio.wav",
  "noise_reduction_level": "medium"
}
```

### Output

Returns a cleaned audio file with:

- Reduced background noise
- Removed hum (50/60Hz)
- Normalized levels
- Preserved vocal clarity

---

## voice_enhancement

Enhances vocal clarity and presence using equalization and compression.

### Parameters

| Parameter    | Type   | Required | Description                        |
| ------------ | ------ | -------- | ---------------------------------- |
| `audio_file` | string | Yes      | Path to the audio file             |
| `preset`     | enum   | Yes      | Audio preset based on content type |

### Presets

- `podcast` - Optimized for spoken word, warm and clear
- `interview` - Balanced for multiple speakers
- `narration` - Smooth and professional for narration

### Example Usage

```json
{
  "audio_file": "/path/to/cleaned_audio.wav",
  "preset": "podcast"
}
```

### Processing Includes

- EQ adjustment (presence boost, low-cut)
- Compression (optimal ratio for speech)
- De-essing (sibilance reduction)
- Limiting (peak control)

---

## sponsor_insertion

Inserts sponsor reads at predetermined points in the audio.

### Parameters

| Parameter          | Type   | Required | Description                           |
| ------------------ | ------ | -------- | ------------------------------------- |
| `main_audio`       | string | Yes      | Path to the main audio file           |
| `sponsor_audio`    | string | Yes      | Path to the sponsor read audio        |
| `insertion_points` | array  | Yes      | Timestamps for insertion (in seconds) |
| `transition_style` | enum   | No       | How to transition between audio       |

### Transition Styles

- `hard_cut` - Immediate switch
- `fade` - Crossfade with fixed duration
- `crossfade` - Smart crossfade based on audio content

### Example Usage

```json
{
  "main_audio": "/path/to/episode_audio.wav",
  "sponsor_audio": "/path/to/sponsor_read.wav",
  "insertion_points": [180, 1200, 2400],
  "transition_style": "crossfade"
}
```

### Best Practices

1. Use crossfade for natural transitions
2. Match loudness levels between segments
3. Test insertions before final render

---

## audio_mastering

Masters final audio for distribution to podcast platforms.

### Parameters

| Parameter     | Type   | Required | Description                      |
| ------------- | ------ | -------- | -------------------------------- |
| `audio_file`  | string | Yes      | Path to the audio file to master |
| `target_lufs` | number | No       | Target loudness (default: -14)   |
| `platform`    | enum   | Yes      | Target platform for optimization |

### Target Platforms

- `spotify` - Optimized for Spotify's normalization
- `apple_podcasts` - Optimized for Apple Podcasts
- `youtube` - Optimized for YouTube loudness standards

### Example Usage

```json
{
  "audio_file": "/path/to/final_mix.wav",
  "target_lufs": -14,
  "platform": "spotify"
}
```

### Mastering Includes

- Loudness normalization (LUFS targeting)
- Dynamic range processing
- Spectral balancing
- True peak limiting
- Format conversion (MP3, AAC)

---

## Workflow Integration

### Complete Audio Production Workflow

```
audio_cleanup → voice_enhancement → sponsor_insertion → audio_mastering
```

### Quick Cleanup Workflow

```
audio_cleanup → audio_mastering
```

---

## Loudness Standards

| Platform       | Target LUFS | True Peak Limit |
| -------------- | ----------- | --------------- |
| Spotify        | -14         | -1 dBTP         |
| Apple Podcasts | -16         | -1 dBTP         |
| YouTube        | -14         | -1 dBTP         |

---

## Best Practices

1. **Always start with audio_cleanup** - Clean audio is essential for all subsequent processing
2. **Match presets to content type** - Different content requires different processing
3. **Use crossfade transitions** - Creates seamless sponsor integrations
4. **Master for specific platforms** - Each platform has different requirements
5. **Check loudness before distribution** - Ensure compliance with platform standards
