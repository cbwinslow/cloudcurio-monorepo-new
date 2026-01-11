# Social Media Toolsets

This document provides detailed documentation for all social media tools available to the Social Media Manager agent.

## Tools Overview

| Tool Name                 | Description                                    | Status |
| ------------------------- | ---------------------------------------------- | ------ |
| `create_content_calendar` | Generate and manage content posting schedule   | Active |
| `schedule_post`           | Schedule posts across multiple platforms       | Active |
| `engage_audience`         | Monitor and respond to comments and messages   | Active |
| `analyze_performance`     | Analyze post performance and generate insights | Active |

---

## create_content_calendar

Generates a content posting schedule for specified date range and platforms.

### Parameters

| Parameter       | Type   | Required | Description                       |
| --------------- | ------ | -------- | --------------------------------- |
| `start_date`    | string | Yes      | Start date (YYYY-MM-DD)           |
| `end_date`      | string | Yes      | End date (YYYY-MM-DD)             |
| `platforms`     | array  | Yes      | List of platforms to schedule for |
| `content_types` | array  | Yes      | Types of content to include       |

### Platform Values

- `twitter` - Twitter/X posts
- `instagram` - Instagram posts and reels
- `tiktok` - TikTok videos
- `youtube` - YouTube posts
- `linkedin` - LinkedIn posts

### Content Type Values

- `episode_promo` - Promotion for new episodes
- `behind_scenes` - Behind-the-scenes content
- `tour_dates` - Tour and event promotion
- `sponsor_content` - Sponsored content and ads

### Example Usage

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "platforms": ["twitter", "instagram", "tiktok"],
  "content_types": ["episode_promo", "behind_scenes"]
}
```

### Output

Returns a content calendar with:

- Scheduled posts with dates and times
- Platform-specific content recommendations
- Optimal posting times based on engagement data

---

## schedule_post

Schedules posts across multiple platforms with platform-specific adaptations.

### Parameters

| Parameter      | Type   | Required | Description                            |
| -------------- | ------ | -------- | -------------------------------------- |
| `content`      | object | Yes      | Post content object                    |
| `platforms`    | array  | Yes      | Platforms to post to                   |
| `publish_time` | string | Yes      | ISO datetime for publishing            |
| `timezone`     | string | No       | Timezone for scheduling (default: UTC) |

### Content Object Structure

```json
{
  "text": "Main post text",
  "media_paths": ["/path/to/image1.jpg"],
  "hashtags": ["podcast", "comedy"],
  "mentions": ["@influencer"]
}
```

### Example Usage

```json
{
  "content": {
    "text": "Check out our latest episode!",
    "media_paths": ["/assets/promo.jpg"],
    "hashtags": ["podcast", "newepisode"]
  },
  "platforms": ["twitter", "instagram"],
  "publish_time": "2024-01-15T14:00:00Z",
  "timezone": "America/New_York"
}
```

---

## engage_audience

Monitors and responds to audience interactions across platforms.

### Parameters

| Parameter         | Type   | Required | Description           |
| ----------------- | ------ | -------- | --------------------- |
| `platform`        | string | Yes      | Platform to engage on |
| `engagement_type` | enum   | Yes      | Type of engagement    |
| `response_style`  | enum   | No       | Style of responses    |

### Engagement Types

- `comments` - Post and comment responses
- `dms` - Direct messages
- `mentions` - @mentions and tags

### Response Styles

- `professional` - Formal and brand-appropriate
- `casual` - Friendly and conversational
- `humorous` - Fun and engaging (podcast style)

### Example Usage

```json
{
  "platform": "instagram",
  "engagement_type": "comments",
  "response_style": "casual"
}
```

---

## analyze_performance

Analyzes post performance across platforms and generates insights.

### Parameters

| Parameter     | Type   | Required | Description            |
| ------------- | ------ | -------- | ---------------------- |
| `time_period` | string | Yes      | Time period to analyze |
| `platforms`   | array  | Yes      | Platforms to analyze   |
| `metrics`     | array  | Yes      | Metrics to retrieve    |

### Metric Values

- `engagement` - Likes, comments, shares
- `reach` - Total audience reach
- `conversion` - Link clicks and signups
- `followers` - Follower growth

### Example Usage

```json
{
  "time_period": "last_30_days",
  "platforms": ["twitter", "instagram"],
  "metrics": ["engagement", "reach", "conversion"]
}
```

### Output

Returns performance report with:

- Engagement rates by platform
- Reach and impressions data
- Top performing content
- Audience growth trends
- Recommendations for improvement

---

## MCP Social Media Tools

The project also includes MCP server tools for social media integration:

| Tool                | Description                | Status |
| ------------------- | -------------------------- | ------ |
| `post_to_twitter`   | Post to Twitter/X          | Active |
| `post_to_instagram` | Post to Instagram          | Active |
| `post_to_tiktok`    | Post to TikTok             | Active |
| `upload_to_youtube` | Upload to YouTube          | Active |
| `post_to_linkedin`  | Post to LinkedIn           | Active |
| `cross_post`        | Post to multiple platforms | Active |
| `get_analytics`     | Get analytics data         | Active |

### MCP Tool Usage

All MCP tools are available via the social-media-manager MCP server and support platform-specific parameters.

---

## Workflow Integration

### Content Distribution Workflow

```
create_content_calendar → schedule_post → engage_audience → analyze_performance
```

### Quick Post Workflow

```
schedule_post → cross_post
```

### Performance Review Workflow

```
analyze_performance → create_content_calendar (optimized)
```

---

## Best Practices

1. **Post consistently** - Maintain regular posting schedule
2. **Adapt content per platform** - Each platform has unique requirements
3. **Engage promptly** - Respond to comments within 24 hours
4. **Track performance** - Use analytics to optimize content strategy
5. **Cross-promote strategically** - Use cross_post for maximum reach
