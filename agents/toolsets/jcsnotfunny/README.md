# Toolsets Documentation

This directory contains detailed documentation for all toolsets used in the podcast production workflow.

## Index

| Category             | File                                                 | Description                                     |
| -------------------- | ---------------------------------------------------- | ----------------------------------------------- |
| Video Editing        | [VIDEO_EDITING.md](./VIDEO_EDITING.md)               | Video cutting, overlays, and short-form content |
| Audio Production     | [AUDIO_PRODUCTION.md](./AUDIO_PRODUCTION.md)         | Audio cleanup, enhancement, and mastering       |
| Social Media         | [SOCIAL_MEDIA.md](./SOCIAL_MEDIA.md)                 | Content scheduling, posting, and analytics      |
| Content Distribution | [CONTENT_DISTRIBUTION.md](./CONTENT_DISTRIBUTION.md) | Episode publishing, CDN, and SEO                |
| Sponsorship & Tour   | [SPONSORSHIP_TOUR.md](./SPONSORSHIP_TOUR.md)         | Sponsor management and live events              |

## Quick Reference

### Agent to Tools Mapping

| Agent                | Tools                                                                                |
| -------------------- | ------------------------------------------------------------------------------------ |
| Video Editor         | `video_analysis`, `auto_cut`, `create_short`, `add_overlays`                         |
| Audio Engineer       | `audio_cleanup`, `voice_enhancement`, `sponsor_insertion`, `audio_mastering`         |
| Social Media Manager | `create_content_calendar`, `schedule_post`, `engage_audience`, `analyze_performance` |
| Content Distributor  | `publish_episode`, `update_tour_dates`, `manage_cdn`, `seo_optimization`             |
| Sponsorship Manager  | `sponsor_research`, `create_sponsor_read`, `track_performance`, `generate_report`    |
| Tour Manager         | `venue_research`, `create_tour_schedule`, `manage_tickets`, `promote_event`          |

## Common Workflows

### Episode Production

```
Video: video_analysis → auto_cut → add_overlays
Audio: audio_cleanup → voice_enhancement → sponsor_insertion → audio_mastering
Distribution: publish_episode → seo_optimization → manage_cdn
Social: create_content_calendar → schedule_post
```

### Tour Promotion

```
Tour: create_tour_schedule → manage_tickets → promote_event
Distribution: update_tour_dates
Social: schedule_post
```

## Related Documentation

- [AGENTS.md](../../AGENTS.md) - Agent overview and workflows
- [agents_config.json](../../agents_config.json) - Agent configuration
- [mcp-servers/social-media-manager/](../../mcp-servers/social-media-manager/) - MCP server implementation
- [mcp-servers/supermemory-ai/](../../mcp-servers/supermemory-ai/) - Memory MCP server
