# Content Distribution Toolsets

This document provides detailed documentation for all content distribution tools available to the Content Distribution Manager agent.

## Tools Overview

| Tool Name           | Description                                          | Status |
| ------------------- | ---------------------------------------------------- | ------ |
| `publish_episode`   | Publish new episode to website and podcast platforms | Active |
| `update_tour_dates` | Update tour schedule on website                      | Active |
| `manage_cdn`        | Optimize CDN settings and cache invalidation         | Active |
| `seo_optimization`  | Optimize content for search engines                  | Active |

---

## publish_episode

Publishes new episodes to the website and podcast platforms.

### Parameters

| Parameter      | Type   | Required | Description                      |
| -------------- | ------ | -------- | -------------------------------- |
| `episode_data` | object | Yes      | Episode metadata and information |
| `audio_file`   | string | Yes      | Path to the audio file           |
| `video_file`   | string | No       | Path to the video file           |
| `show_notes`   | string | Yes      | Show notes and description       |

### Episode Data Structure

```json
{
  "title": "Episode Title",
  "episode_number": 42,
  "season": 3,
  "publish_date": "2024-01-15",
  "duration_minutes": 45,
  "guests": ["Guest Name"],
  "topics": ["Topic 1", "Topic 2"],
  "explicit": false
}
```

### Example Usage

```json
{
  "episode_data": {
    "title": "Best of 2023",
    "episode_number": 100,
    "season": 4,
    "publish_date": "2024-01-01",
    "duration_minutes": 60,
    "guests": ["Various"],
    "topics": ["year_review", "highlights"]
  },
  "audio_file": "/path/to/episode_100.mp3",
  "video_file": "/path/to/episode_100.mp4",
  "show_notes": "## Highlights\\n- Topic 1\\n- Topic 2"
}
```

### Output

Returns publish confirmation with:

- Episode URL
- RSS feed update confirmation
- Platform syndication status

---

## update_tour_dates

Updates tour schedule information on the website.

### Parameters

| Parameter      | Type  | Required | Description                    |
| -------------- | ----- | -------- | ------------------------------ |
| `tour_data`    | array | Yes      | Array of tour date objects     |
| `venues`       | array | Yes      | Array of venue information     |
| `ticket_links` | array | Yes      | Array of ticket purchase links |

### Tour Data Structure

```json
[
  {
    "date": "2024-03-15",
    "city": "New York",
    "state": "NY",
    "venue": "Madison Square Garden",
    "doors_open": "18:00",
    "show_time": "20:00",
    "sold_out": false
  }
]
```

### Example Usage

```json
{
  "tour_data": [
    {
      "date": "2024-03-15",
      "city": "New York",
      "state": "NY",
      "venue": "Madison Square Garden",
      "doors_open": "18:00",
      "show_time": "20:00"
    },
    {
      "date": "2024-03-20",
      "city": "Los Angeles",
      "state": "CA",
      "venue": "The Forum",
      "doors_open": "19:00",
      "show_time": "21:00"
    }
  ],
  "venues": [
    { "name": "Madison Square Garden", "capacity": 20000 },
    { "name": "The Forum", "capacity": 17000 }
  ],
  "ticket_links": ["https://tickets.example.com/msg", "https://tickets.example.com/forum"]
}
```

---

## manage_cdn

Manages CDN settings, cache invalidation, and performance optimization.

### Parameters

| Parameter | Type  | Required | Description           |
| --------- | ----- | -------- | --------------------- |
| `action`  | enum  | Yes      | Action to perform     |
| `targets` | array | Yes      | Files/paths to target |

### Actions

- `purge_cache` - Clear cached content
- `update_settings` - Modify CDN configuration
- `analyze_performance` - Analyze CDN performance

### Example Usage

```json
{
  "action": "purge_cache",
  "targets": ["/episodes/*.mp3", "/assets/logo.png"]
}
```

### Output

Returns CDN management results with:

- Cache purge status
- Performance metrics
- Configuration updates

---

## seo_optimization

Optimizes content for search engines with metadata and keywords.

### Parameters

| Parameter         | Type   | Required | Description                 |
| ----------------- | ------ | -------- | --------------------------- |
| `content_type`    | enum   | Yes      | Type of content to optimize |
| `target_keywords` | array  | Yes      | Keywords to target          |
| `metadata`        | object | Yes      | SEO metadata                |

### Content Types

- `episode` - Podcast episode
- `page` - Website page
- `blog_post` - Blog article

### Metadata Structure

```json
{
  "title": "SEO Optimized Title",
  "description": "Meta description for search results",
  "canonical_url": "https://example.com/content",
  "og_image": "https://example.com/og-image.jpg",
  "schema_type": "PodcastEpisode"
}
```

### Example Usage

```json
{
  "content_type": "episode",
  "target_keywords": ["podcast", "comedy", "interview"],
  "metadata": {
    "title": "Comedy Podcast Episode - Guest Interview",
    "description": "Listen to our hilarious interview with special guest",
    "og_image": "/assets/episode-og.jpg"
  }
}
```

---

## Workflow Integration

### Episode Publishing Workflow

```
publish_episode → seo_optimization → manage_cdn (purge_cache)
```

### Tour Update Workflow

```
update_tour_dates → seo_optimization (page type)
```

### CDN Maintenance Workflow

```
manage_cdn (analyze_performance) → manage_cdn (update_settings)
```

---

## Best Practices

1. **Optimize before publishing** - Run SEO optimization before publishing content
2. **Purge cache after updates** - Clear CDN cache after content changes
3. **Use canonical URLs** - Prevent duplicate content issues
4. **Include rich metadata** - Improves search visibility and social sharing
5. **Test after publishing** - Verify content is accessible and indexed
