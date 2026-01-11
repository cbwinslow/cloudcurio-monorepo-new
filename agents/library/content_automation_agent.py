#!/usr/bin/env python3
"""
Content Automation Agent for Jared's Not Funny Podcast

This agent handles automated content distribution across multiple platforms,
YouTube clip generation, and social media posting using MCP servers and AI.

Features:
- Multi-platform content distribution via MCP servers
- YouTube episode clip generation with AI analysis
- Social media automation with platform-specific optimization
- Content scheduling and analytics tracking
- Error handling and retry logic
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from agents.base_agent import BaseAgent
from agents.robust_tool import RobustTool


class ContentAutomationAgent(BaseAgent):
    """Content Automation Agent for cross-platform distribution and YouTube clip generation."""
    
    def __init__(self, config_path: str = "agents/config.json"):
        super().__init__(config_path)
        self.name = "ContentAutomationAgent"
        self.description = "Handles automated content distribution and YouTube clip generation"
        
        # Load API keys and configurations
        self.api_keys = self._load_api_keys()
        self.mcp_servers = self._load_mcp_servers()
        self.platform_configs = self._load_platform_configs()
        
        # Initialize tools
        self.tools = {
            "content_distributor": RobustTool(
                name="content_distributor",
                description="Distributes content to multiple platforms via MCP servers",
                func=self.distribute_content
            ),
            "youtube_clip_generator": RobustTool(
                name="youtube_clip_generator",
                description="Generates optimized clips from YouTube episodes using AI",
                func=self.generate_youtube_clips
            ),
            "social_media_scheduler": RobustTool(
                name="social_media_scheduler",
                description="Schedules social media posts across platforms",
                func=self.schedule_social_posts
            ),
            "analytics_tracker": RobustTool(
                name="analytics_tracker",
                description="Tracks content performance and engagement metrics",
                func=self.track_content_performance
            )
        }
        
        # Content queue for processing
        self.content_queue = []
        self.processed_content = []
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables and config files."""
        return {
            "youtube": os.getenv("YOUTUBE_API_KEY", ""),
            "tiktok": os.getenv("TIKTOK_API_KEY", ""),
            "instagram": os.getenv("INSTAGRAM_API_KEY", ""),
            "twitter": os.getenv("TWITTER_API_KEY", ""),
            "facebook": os.getenv("FACEBOOK_API_KEY", ""),
            "linkedin": os.getenv("LINKEDIN_API_KEY", ""),
            "mcp_social": os.getenv("MCP_SOCIAL_API_KEY", ""),
            "mcp_video": os.getenv("MCP_VIDEO_API_KEY", "")
        }
    
    def _load_mcp_servers(self) -> Dict[str, Any]:
        """Load MCP server configurations."""
        return {
            "social_media": {
                "url": "http://localhost:3001",
                "endpoints": {
                    "post": "/api/post",
                    "schedule": "/api/schedule",
                    "analytics": "/api/analytics"
                }
            },
            "video_processing": {
                "url": "http://localhost:3002",
                "endpoints": {
                    "analyze": "/api/analyze",
                    "clip": "/api/clip",
                    "optimize": "/api/optimize"
                }
            },
            "content_management": {
                "url": "http://localhost:3003",
                "endpoints": {
                    "publish": "/api/publish",
                    "archive": "/api/archive",
                    "search": "/api/search"
                }
            }
        }
    
    def _load_platform_configs(self) -> Dict[str, Any]:
        """Load platform-specific configurations."""
        return {
            "youtube": {
                "max_title_length": 100,
                "max_description_length": 5000,
                "optimal_tags": 15,
                "clip_durations": [15, 30, 60, 90],
                "aspect_ratios": ["16:9", "9:16", "1:1"]
            },
            "tiktok": {
                "max_caption_length": 2200,
                "optimal_hashtags": 5,
                "max_duration": 60,
                "aspect_ratio": "9:16"
            },
            "instagram": {
                "max_caption_length": 2200,
                "optimal_hashtags": 10,
                "max_duration": 60,
                "aspect_ratios": ["1:1", "4:5", "9:16"]
            },
            "twitter": {
                "max_tweet_length": 280,
                "optimal_hashtags": 2,
                "max_media": 4
            },
            "facebook": {
                "max_post_length": 63206,
                "optimal_hashtags": 5,
                "max_duration": 240
            }
        }
    
    def add_to_queue(self, content: Dict[str, Any]) -> bool:
        """Add content to the processing queue."""
        try:
            required_fields = ["title", "description", "content_type", "source_url"]
            
            if not all(field in content for field in required_fields):
                self.logger.error(f"Content missing required fields: {required_fields}")
                return False
                
            content["queue_time"] = datetime.now().isoformat()
            content["status"] = "queued"
            
            self.content_queue.append(content)
            self.logger.info(f"Added content to queue: {content['title']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding content to queue: {str(e)}")
            return False
    
    def process_queue(self) -> None:
        """Process all items in the content queue."""
        self.logger.info(f"Processing {len(self.content_queue)} items in queue")
        
        for content in self.content_queue:
            try:
                if content["content_type"] == "youtube_episode":
                    # Generate clips first
                    clips = self.generate_youtube_clips(content)
                    
                    # Then distribute main content
                    distribution_result = self.distribute_content(content)
                    
                    # Distribute clips
                    for clip in clips:
                        clip_content = {
                            **content,
                            "title": clip["title"],
                            "description": clip["description"],
                            "content_type": "youtube_clip",
                            "clip_data": clip
                        }
                        self.distribute_content(clip_content)
                        
                else:
                    # Distribute other content types
                    self.distribute_content(content)
                    
                # Update status and move to processed
                content["status"] = "processed"
                content["processed_time"] = datetime.now().isoformat()
                self.processed_content.append(content)
                
                self.logger.info(f"Processed content: {content['title']}")
                
            except Exception as e:
                content["status"] = "error"
                content["error"] = str(e)
                self.logger.error(f"Error processing content {content.get('title', 'unknown')}: {str(e)}")
    
    def distribute_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute content to multiple platforms via MCP servers."""
        result = {
            "success": False,
            "platforms": {},
            "errors": []
        }
        
        try:
            # Determine target platforms based on content type
            platforms = self._get_target_platforms(content["content_type"])
            
            for platform in platforms:
                try:
                    # Get platform-specific content
                    platform_content = self._adapt_content_for_platform(content, platform)
                    
                    # Send to MCP server
                    mcp_result = self._send_to_mcp_server(platform, platform_content)
                    
                    if mcp_result.get("success", False):
                        result["platforms"][platform] = {
                            "status": "success",
                            "post_id": mcp_result.get("post_id"),
                            "url": mcp_result.get("url")
                        }
                    else:
                        result["platforms"][platform] = {
                            "status": "failed",
                            "error": mcp_result.get("error", "Unknown error")
                        }
                        result["errors"].append(f"{platform}: {mcp_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    result["platforms"][platform] = {
                        "status": "failed",
                        "error": str(e)
                    }
                    result["errors"].append(f"{platform}: {str(e)}")
            
            result["success"] = len(result["errors"]) == 0
            return result
            
        except Exception as e:
            result["errors"].append(f"Distribution failed: {str(e)}")
            return result
    
    def _get_target_platforms(self, content_type: str) -> List[str]:
        """Determine target platforms based on content type."""
        platform_mapping = {
            "youtube_episode": ["youtube", "website", "twitter", "facebook"],
            "youtube_clip": ["youtube_shorts", "tiktok", "instagram", "twitter", "facebook"],
            "podcast_episode": ["website", "apple_podcasts", "spotify", "google_podcasts", "twitter"],
            "blog_post": ["website", "twitter", "linkedin", "facebook"],
            "social_post": ["twitter", "instagram", "facebook", "linkedin"],
            "newsletter": ["email", "website", "twitter"]
        }
        
        return platform_mapping.get(content_type, ["website", "twitter"])
    
    def _adapt_content_for_platform(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Adapt content for specific platform requirements."""
        platform_config = self.platform_configs.get(platform, {})
        adapted_content = content.copy()
        
        # Platform-specific adaptations
        if platform in ["twitter", "tiktok", "instagram"]:
            adapted_content = self._adapt_for_social_media(adapted_content, platform)
            
        elif platform in ["youtube", "youtube_shorts"]:
            adapted_content = self._adapt_for_youtube(adapted_content, platform)
            
        elif platform == "website":
            adapted_content = self._adapt_for_website(adapted_content)
            
        # Add UTM parameters for tracking
        adapted_content["utm_params"] = self._generate_utm_params(content, platform)
        
        return adapted_content
    
    def _adapt_for_social_media(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Adapt content for social media platforms."""
        config = self.platform_configs[platform]
        
        # Truncate text to platform limits
        if "caption" in content and config.get("max_caption_length"):
            content["caption"] = content["caption"][:config["max_caption_length"]]
            
        # Add platform-specific hashtags
        if "hashtags" not in content:
            content["hashtags"] = self._generate_hashtags(content, platform)
            
        # Ensure hashtag count is optimal
        if content["hashtags"] and config.get("optimal_hashtags"):
            content["hashtags"] = content["hashtags"][:config["optimal_hashtags"]]
            
        # Add emojis for engagement
        content["caption"] = self._add_engagement_emojis(content["caption"], platform)
        
        return content
    
    def _adapt_for_youtube(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Adapt content for YouTube platforms."""
        config = self.platform_configs[platform]
        
        # Format title for YouTube
        if "title" in content:
            content["title"] = self._format_youtube_title(content["title"], platform)
            
        # Optimize description
        if "description" in content:
            content["description"] = self._optimize_youtube_description(content["description"], platform)
            
        # Ensure tags are optimal
        if "tags" not in content:
            content["tags"] = self._generate_youtube_tags(content)
            
        if content["tags"] and config.get("optimal_tags"):
            content["tags"] = content["tags"][:config["optimal_tags"]]
            
        # Add timestamps if available
        if platform == "youtube" and "chapters" in content:
            content["description"] += "\n\n" + self._generate_youtube_timestamps(content["chapters"])
            
        return content
    
    def _adapt_for_website(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for website publishing."""
        # Ensure proper SEO fields
        if "seo_title" not in content:
            content["seo_title"] = content.get("title", "")
            
        if "seo_description" not in content:
            content["seo_description"] = content.get("description", "")[:160]
            
        if "keywords" not in content:
            content["keywords"] = self._generate_keywords(content)
            
        # Add schema markup
        content["schema_markup"] = self._generate_schema_markup(content)
        
        return content
    
    def _generate_utm_params(self, content: Dict[str, Any], platform: str) -> Dict[str, str]:
        """Generate UTM parameters for tracking."""
        return {
            "utm_source": platform,
            "utm_medium": "social" if platform in ["twitter", "facebook", "instagram", "linkedin", "tiktok"] else "organic",
            "utm_campaign": content.get("campaign", "content_distribution"),
            "utm_content": content.get("title", "podcast_content").replace(" ", "_").lower()
        }
    
    def _generate_hashtags(self, content: Dict[str, Any], platform: str) -> List[str]:
        """Generate platform-appropriate hashtags."""
        base_hashtags = ["#jaredsnotfunny", "#podcast", "#comedy"]
        
        # Add content-specific hashtags
        if "keywords" in content:
            base_hashtags.extend([f"#{kw.replace(' ', '')}" for kw in content["keywords"][:3]])
            
        # Add platform-specific hashtags
        platform_hashtags = {
            "twitter": ["#tech", "#culture"],
            "instagram": ["#comedyclips", "#podcastlife"],
            "tiktok": ["#fyp", "#viral", "#comedy"],
            "youtube": ["#podcast", "#interview", "#comedy"]
        }
        
        if platform in platform_hashtags:
            base_hashtags.extend(platform_hashtags[platform])
            
        # Remove duplicates and return
        return list(set(base_hashtags))
    
    def _generate_youtube_tags(self, content: Dict[str, Any]) -> List[str]:
        """Generate YouTube-specific tags."""
        tags = ["jared's not funny", "podcast", "comedy"]
        
        # Add guest name if available
        if "guest" in content:
            tags.append(content["guest"])
            
        # Add keywords
        if "keywords" in content:
            tags.extend(content["keywords"])
            
        # Add topics
        if "topics" in content:
            tags.extend(content["topics"])
            
        # Remove duplicates and limit to 500 characters total
        unique_tags = list(set(tags))
        
        # YouTube has a 500 character limit for tags
        current_length = sum(len(tag) for tag in unique_tags) + len(unique_tags) - 1  # +1 for commas
        
        if current_length > 500:
            # Sort by length and remove longest tags until under limit
            unique_tags.sort(key=len)
            while current_length > 500 and len(unique_tags) > 1:
                removed = unique_tags.pop()
                current_length -= (len(removed) + 1)
                
        return unique_tags
    
    def _format_youtube_title(self, title: str, platform: str) -> str:
        """Format title for YouTube optimization."""
        if platform == "youtube_shorts":
            # For shorts, make it more engaging
            if not title.startswith(("🎤", "🎙️", "😂", "🔥", "💥")):
                title = "🎙️ " + title
            
            # Add #shorts hashtag
            if not title.endswith("#shorts"):
                title += " #shorts"
                
        # Ensure title is within limits
        config = self.platform_configs[platform]
        if len(title) > config.get("max_title_length", 100):
            title = title[:config["max_title_length"] - 3] + "..."
            
        return title
    
    def _optimize_youtube_description(self, description: str, platform: str) -> str:
        """Optimize YouTube description for SEO and engagement."""
        config = self.platform_configs[platform]
        
        # Add call to action
        if platform == "youtube":
            cta = ("\n\n🔔 Subscribe for more comedy and tech content! "
                  "🎧 Listen to the full podcast: https://jcsnotfunny.com "
                  "📲 Follow us on social media @jaredsnotfunny")
        else:  # shorts
            cta = ("\n\n🔥 Want more? Full episode: https://jcsnotfunny.com "
                  "😂 Follow @jaredsnotfunny for daily comedy!")
            
        description += cta
        
        # Ensure description is within limits
        if len(description) > config.get("max_description_length", 5000):
            description = description[:config["max_description_length"] - 3] + "..."
            
        return description
    
    def _generate_youtube_timestamps(self, chapters: List[Dict[str, Any]]) -> str:
        """Generate YouTube timestamp links from chapters."""
        timestamps = "📋 Chapters:\n"
        
        for i, chapter in enumerate(chapters, 1):
            if "timestamp" in chapter and "title" in chapter:
                # Convert timestamp to YouTube format (HH:MM:SS)
                if ":" in str(chapter["timestamp"]):
                    ts = chapter["timestamp"]
                else:
                    # Convert seconds to HH:MM:SS
                    seconds = int(chapter["timestamp"])
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60
                    ts = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                timestamps += f"{i}. {ts} - {chapter['title']}\n"
                
        return timestamps.strip()
    
    def _generate_schema_markup(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema markup for content."""
        if content["content_type"] == "youtube_episode":
            return {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": content["title"],
                "description": content["description"],
                "thumbnailUrl": content.get("thumbnail", ""),
                "uploadDate": content.get("publish_date", datetime.now().isoformat()),
                "duration": content.get("duration", "PT1H"),
                "contentUrl": content["source_url"],
                "embedUrl": content.get("embed_url", content["source_url"]),
                "interactionStatistic": {
                    "@type": "InteractionCounter",
                    "interactionType": {"@type": "http://schema.org/WatchAction"},
                    "userInteractionCount": content.get("views", 0)
                }
            }
        elif content["content_type"] == "podcast_episode":
            return {
                "@context": "https://schema.org",
                "@type": "PodcastEpisode",
                "name": content["title"],
                "description": content["description"],
                "datePublished": content.get("publish_date", datetime.now().isoformat()),
                "duration": content.get("duration", "PT1H"),
                "url": content["source_url"],
                "associatedMedia": {
                    "@type": "MediaObject",
                    "contentUrl": content.get("audio_url", ""),
                    "encodingFormat": "audio/mpeg"
                }
            }
        else:
            return {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": content["title"],
                "description": content["description"],
                "datePublished": content.get("publish_date", datetime.now().isoformat()),
                "url": content["source_url"]
            }
    
    def _send_to_mcp_server(self, platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send content to appropriate MCP server."""
        try:
            # Determine which MCP server to use
            if platform in ["youtube", "youtube_shorts"]:
                mcp_server = self.mcp_servers["video_processing"]
                endpoint = "/api/publish"
            elif platform in ["twitter", "facebook", "instagram", "tiktok", "linkedin"]:
                mcp_server = self.mcp_servers["social_media"]
                endpoint = "/api/post"
            else:
                mcp_server = self.mcp_servers["content_management"]
                endpoint = "/api/publish"
            
            # Prepare payload
            payload = {
                "platform": platform,
                "content": content,
                "api_key": self.api_keys.get(f"mcp_{'video' if 'youtube' in platform else 'social'}", "")
            }
            
            # Send request
            response = requests.post(
                f"{mcp_server['url']}{endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, **response.json()}
            else:
                return {
                    "success": False,
                    "error": f"MCP Server Error: {response.status_code} - {response.text}",
                    "platform": platform
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "platform": platform
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "platform": platform
            }
    
    def generate_youtube_clips(self, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimized clips from YouTube episodes using AI analysis."""
        clips = []
        
        try:
            # Send episode to video processing MCP server for analysis
            analysis_result = self._analyze_video_for_clips(episode)
            
            if not analysis_result.get("success", False):
                self.logger.error(f"Video analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return clips
                
            # Generate clips based on analysis
            for segment in analysis_result.get("segments", []):
                if segment["score"] > 8.0:  # Only use high-quality segments
                    clip = self._create_clip_from_segment(episode, segment)
                    clips.append(clip)
            
            # Ensure we have at least 3 clips
            if len(clips) < 3:
                top_segments = sorted(analysis_result.get("segments", []), 
                                     key=lambda x: x["score"], reverse=True)[:3]
                for segment in top_segments:
                    if segment not in [c["source_segment"] for c in clips]:
                        clip = self._create_clip_from_segment(episode, segment)
                        clips.append(clip)
            
            return clips
            
        except Exception as e:
            self.logger.error(f"Error generating YouTube clips: {str(e)}")
            return []
    
    def _analyze_video_for_clips(self, episode: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video for optimal clip segments using AI."""
        try:
            # Prepare analysis request
            payload = {
                "video_url": episode["source_url"],
                "video_id": episode.get("video_id", ""),
                "title": episode["title"],
                "description": episode["description"],
                "duration": episode.get("duration", "PT1H"),
                "analysis_type": "clip_optimization",
                "api_key": self.api_keys["mcp_video"]
            }
            
            # Send to video processing MCP server
            response = requests.post(
                f"{self.mcp_servers['video_processing']['url']}/api/analyze",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                return {"success": True, **response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Analysis failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis error: {str(e)}"
            }
    
    def _create_clip_from_segment(self, episode: Dict[str, Any], segment: Dict[str, Any]) -> Dict[str, Any]:
        """Create a clip configuration from a video segment."""
        # Determine clip type based on segment
        clip_type = self._determine_clip_type(segment)
        
        # Generate clip metadata
        clip = {
            "source_episode": episode["title"],
            "source_url": episode["source_url"],
            "source_segment": segment,
            "clip_type": clip_type,
            "start_time": segment["start_time"],
            "end_time": segment["end_time"],
            "duration": segment["end_time"] - segment["start_time"],
            "score": segment["score"],
            "topic": segment.get("topic", "comedy"),
            "title": self._generate_clip_title(episode, segment, clip_type),
            "description": self._generate_clip_description(episode, segment, clip_type),
            "hashtags": self._generate_clip_hashtags(episode, segment, clip_type),
            "platforms": self._determine_clip_platforms(clip_type),
            "aspect_ratio": self._determine_aspect_ratio(clip_type),
            "text_overlays": self._generate_text_overlays(episode, segment, clip_type),
            "background_music": self._suggest_background_music(clip_type),
            "subtitles": True,
            "optimization_suggestions": segment.get("optimization_suggestions", [])
        }
        
        return clip
    
    def _determine_clip_type(self, segment: Dict[str, Any]) -> str:
        """Determine the type of clip based on segment analysis."""
        topic = segment.get("topic", "").lower()
        
        if "funny" in topic or "hilarious" in topic or segment.get("humor_score", 0) > 0.8:
            return "funny_moment"
        elif "tech" in topic or "technology" in topic:
            return "tech_insight"
        elif "story" in topic or "experience" in topic:
            return "personal_story"
        elif "debate" in topic or "discussion" in topic:
            return "hot_take"
        elif "food" in topic or "challenge" in topic:
            return "challenge"
        else:
            return "highlight"
    
    def _generate_clip_title(self, episode: Dict[str, Any], segment: Dict[str, Any], clip_type: str) -> str:
        """Generate an engaging title for the clip."""
        emojis = {
            "funny_moment": "😂",
            "tech_insight": "💻",
            "personal_story": "📖",
            "hot_take": "🔥",
            "challenge": "🍽️",
            "highlight": "✨"
        }
        
        prefixes = {
            "funny_moment": "Hilarious moment",
            "tech_insight": "Tech insight",
            "personal_story": "Amazing story",
            "hot_take": "Hot take",
            "challenge": "Challenge accepted",
            "highlight": "Must watch"
        }
        
        # Get guest name if available
        guest = episode.get("guest", "")
        guest_phrase = f" with {guest}" if guest else ""
        
        # Create base title
        title = f"{emojis[clip_type]} {prefixes[clip_type]}{guest_phrase}..."
        
        # Add topic if available
        topic = segment.get("topic", "")
        if topic and topic not in title.lower():
            title += f" about {topic}"
        
        # Ensure title is engaging and within limits
        if len(title) > 60:  # Shorter for social media
            title = title[:57] + "..."
            
        return title
    
    def _generate_clip_description(self, episode: Dict[str, Any], segment: Dict[str, Any], clip_type: str) -> str:
        """Generate a description for the clip."""
        descriptions = {
            "funny_moment": "Can't stop laughing at this moment from our podcast! {guest} shares a hilarious {topic} that you don't want to miss. Full episode: {url}",
            "tech_insight": "Great tech insight from {guest} about {topic}. Learn something new in this clip from our podcast. Full episode: {url}",
            "personal_story": "Fascinating personal story from {guest} about {topic}. This emotional moment shows why our podcast is special. Full episode: {url}",
            "hot_take": "Controversial hot take from {guest} on {topic}! Do you agree? Let us know in the comments. Full episode: {url}",
            "challenge": "Watch {guest} take on the {topic} challenge! Things get wild in this clip from our podcast. Full episode: {url}",
            "highlight": "Don't miss this highlight from our podcast! {guest} discusses {topic} in this engaging moment. Full episode: {url}"
        }
        
        # Fill in template
        guest = episode.get("guest", "Jared Christianson")
        topic = segment.get("topic", "comedy and technology")
        url = episode.get("source_url", "https://jcsnotfunny.com")
        
        description = descriptions[clip_type].format(guest=guest, topic=topic, url=url)
        
        # Add hashtags
        description += "\n\n" + " ".join(self._generate_clip_hashtags(episode, segment, clip_type))
        
        return description
    
    def _generate_clip_hashtags(self, episode: Dict[str, Any], segment: Dict[str, Any], clip_type: str) -> List[str]:
        """Generate hashtags for the clip."""
        base_hashtags = ["#jaredsnotfunny", "#podcast", "#comedy"]
        
        # Add clip type specific hashtags
        type_hashtags = {
            "funny_moment": ["#funny", "#lol", "#comedyclips"],
            "tech_insight": ["#tech", "#techtalk", "#technology"],
            "personal_story": ["#storytime", "#personal", "#emotional"],
            "hot_take": ["#hottake", "#opinion", "#debate"],
            "challenge": ["#challenge", "#foodchallenge", "#trynottolaugh"],
            "highlight": ["#highlight", "#mustwatch", "#bestmoment"]
        }
        
        base_hashtags.extend(type_hashtags[clip_type])
        
        # Add guest hashtag if available
        guest = episode.get("guest", "")
        if guest:
            base_hashtags.append(f"#{guest.replace(' ', '')}")
            
        # Add topic hashtags
        topic = segment.get("topic", "")
        if topic:
            base_hashtags.extend([f"#{t}" for t in topic.split()[:2]])
            
        # Platform-specific hashtags will be added during distribution
        
        return list(set(base_hashtags))
    
    def _determine_clip_platforms(self, clip_type: str) -> List[str]:
        """Determine optimal platforms for each clip type."""
        platform_mapping = {
            "funny_moment": ["tiktok", "instagram", "youtube_shorts", "twitter"],
            "tech_insight": ["youtube_shorts", "linkedin", "twitter", "facebook"],
            "personal_story": ["instagram", "facebook", "youtube_shorts", "twitter"],
            "hot_take": ["twitter", "tiktok", "facebook", "youtube_shorts"],
            "challenge": ["tiktok", "instagram", "youtube_shorts", "facebook"],
            "highlight": ["youtube_shorts", "instagram", "twitter", "facebook"]
        }
        
        return platform_mapping[clip_type]
    
    def _determine_aspect_ratio(self, clip_type: str) -> str:
        """Determine optimal aspect ratio for each clip type."""
        ratio_mapping = {
            "funny_moment": "9:16",  # Vertical for mobile
            "tech_insight": "16:9",  # Horizontal for professional
            "personal_story": "1:1",  # Square for versatility
            "hot_take": "9:16",     # Vertical for engagement
            "challenge": "9:16",     # Vertical for mobile viewing
            "highlight": "16:9"      # Horizontal for general use
        }
        
        return ratio_mapping[clip_type]
    
    def _generate_text_overlays(self, episode: Dict[str, Any], segment: Dict[str, Any], clip_type: str) -> List[str]:
        """Generate text overlays for the clip."""
        overlays = ["JAREDSNOTFUNNY PODCAST"]
        
        # Add guest name
        guest = episode.get("guest", "")
        if guest:
            overlays.append(f"Featuring: {guest}")
            
        # Add clip type specific overlay
        type_overlays = {
            "funny_moment": "😂 Hilarious Moment!",
            "tech_insight": "💻 Tech Insight",
            "personal_story": "📖 Personal Story",
            "hot_take": "🔥 Hot Take!",
            "challenge": "🍽️ Challenge Time!",
            "highlight": "✨ Must Watch!"
        }
        
        overlays.append(type_overlays[clip_type])
        
        # Add topic overlay
        topic = segment.get("topic", "")
        if topic:
            overlays.append(f"Topic: {topic}")
            
        return overlays
    
    def _suggest_background_music(self, clip_type: str) -> str:
        """Suggest appropriate background music for the clip."""
        music_mapping = {
            "funny_moment": "upbeat comedy",
            "tech_insight": "modern tech",
            "personal_story": "emotional piano",
            "hot_take": "intense debate",
            "challenge": "fun challenge",
            "highlight": "engaging podcast"
        }
        
        return music_mapping[clip_type]
    
    def schedule_social_posts(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule social media posts for optimal engagement."""
        result = {"success": False, "scheduled_posts": [], "errors": []}
        
        try:
            # Determine optimal posting times
            platforms = content.get("platforms", ["twitter", "instagram", "facebook"])
            
            for platform in platforms:
                try:
                    # Get optimal time for platform
                    optimal_time = self._get_optimal_posting_time(platform)
                    
                    # Prepare post data
                    post_data = {
                        "platform": platform,
                        "content": content,
                        "schedule_time": optimal_time.isoformat(),
                        "timezone": "America/New_York",
                        "priority": content.get("priority", "normal")
                    }
                    
                    # Send to MCP server
                    mcp_result = self._send_to_mcp_server(platform, post_data)
                    
                    if mcp_result.get("success", False):
                        result["scheduled_posts"].append({
                            "platform": platform,
                            "scheduled_time": optimal_time.isoformat(),
                            "post_id": mcp_result.get("post_id")
                        })
                    else:
                        result["errors"].append({
                            "platform": platform,
                            "error": mcp_result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    result["errors"].append({
                        "platform": platform,
                        "error": str(e)
                    })
            
            result["success"] = len(result["errors"]) == 0
            return result
            
        except Exception as e:
            result["errors"].append(f"Scheduling failed: {str(e)}")
            return result
    
    def _get_optimal_posting_time(self, platform: str) -> datetime:
        """Get optimal posting time for a platform."""
        from datetime import datetime, timedelta
        
        # Get current time in EST
        now = datetime.now()
        
        # Optimal posting times (EST)
        optimal_times = {
            "twitter": [9, 12, 15, 18],      # Morning and afternoon
            "instagram": [11, 19, 21],       # Late morning and evening
            "facebook": [13, 16, 20],        # Afternoon and evening
            "linkedin": [8, 12, 17],        # Business hours
            "tiktok": [18, 21, 23],          # Evening and late night
            "youtube": [14, 19]              # Afternoon and evening
        }
        
        # Find next optimal time
        current_hour = now.hour
        platform_times = optimal_times.get(platform, [12])
        
        # Find first time after current hour
        next_time = None
        for hour in sorted(platform_times):
            if hour > current_hour:
                next_time = hour
                break
        
        # If no time today, use first time tomorrow
        if next_time is None:
            next_time = sorted(platform_times)[0]
            base_date = now + timedelta(days=1)
        else:
            base_date = now
            
        # Create datetime object
        return datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            next_time,
            0,  # Minutes
            0   # Seconds
        )
    
    def track_content_performance(self, content_id: str, platform: str) -> Dict[str, Any]:
        """Track content performance and engagement metrics."""
        try:
            # Prepare tracking request
            payload = {
                "content_id": content_id,
                "platform": platform,
                "metrics": ["views", "likes", "shares", "comments", "clicks"],
                "api_key": self.api_keys.get(f"mcp_{'social' if platform in ['twitter', 'facebook', 'instagram', 'tiktok', 'linkedin'] else 'video'}", "")
            }
            
            # Send to appropriate MCP server
            if platform in ["twitter", "facebook", "instagram", "tiktok", "linkedin"]:
                mcp_server = self.mcp_servers["social_media"]
                endpoint = "/api/analytics"
            else:
                mcp_server = self.mcp_servers["video_processing"]
                endpoint = "/api/analytics"
            
            response = requests.post(
                f"{mcp_server['url']}{endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, **response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Tracking failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Tracking error: {str(e)}"
            }
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation system status."""
        return {
            "queue_size": len(self.content_queue),
            "processed_count": len(self.processed_content),
            "api_status": {
                "youtube": "connected" if self.api_keys["youtube"] else "disconnected",
                "social_media": "connected" if self.api_keys["mcp_social"] else "disconnected",
                "video_processing": "connected" if self.api_keys["mcp_video"] else "disconnected"
            },
            "recent_activity": [
                {
                    "timestamp": content.get("processed_time", ""),
                    "content": content.get("title", ""),
                    "status": content.get("status", "")
                }
                for content in self.processed_content[-5:]  # Last 5 items
            ]
        }


if __name__ == "__main__":
    # Example usage
    agent = ContentAutomationAgent()
    
    # Example content to process
    example_episode = {
        "title": "JAREDSNOTFUNNY Feat. Toron Rodgers #6",
        "description": "Jared Christianson sits down with Toron Rodgers as they discuss performing stand up comedy, production and life experiences.",
        "content_type": "youtube_episode",
        "source_url": "https://www.youtube.com/watch?v=yCPDYXORg-A",
        "video_id": "yCPDYXORg-A",
        "duration": "PT1H8M40S",
        "publish_date": "2025-09-10T00:00:00Z",
        "guest": "Toron Rodgers",
        "topics": ["stand up comedy", "production", "life experiences"],
        "keywords": ["comedy", "podcast", "standup", "ToronRodgers", "JaredChristianson"],
        "views": 131,
        "priority": "high"
    }
    
    # Add to queue and process
    agent.add_to_queue(example_episode)
    agent.process_queue()
    
    # Get status
    status = agent.get_automation_status()
    print(f"Automation Status: {status}")