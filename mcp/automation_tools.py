#!/usr/bin/env python3
"""
Automation Tools Module

This module contains all the automation tools for content analysis,
YouTube clip generation, social media distribution, SEO optimization,
and analytics tracking.
"""

import asyncio
import json
import logging
import os
import re
import sys
from typing import Dict, Any, List, Optional, Tuple, Set, Collection
from datetime import datetime, timedelta
import random
import requests
import aiohttp
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('automation_tools.log')
    ]
)
logger = logging.getLogger("automation_tools")

# Download NLTK data
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
except:
    pass

class ContentAnalyzer:
    """
    Content analysis tool for SEO, engagement, and optimization opportunities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.stop_words = set(stopwords.words('english'))
        
        # Load SEO best practices
        self.seo_best_practices = {
            'title_length': (50, 60),
            'meta_description_length': (150, 160),
            'heading_structure': ['h1', 'h2', 'h3'],
            'keyword_density': (1, 3),
            'image_alt_tags': True,
            'internal_linking': True,
            'mobile_friendly': True,
            'page_speed': 'fast'
        }
    
    def analyze(self, content_url: str, content_type: str = 'video', 
                platform: str = 'youtube') -> Dict[str, Any]:
        """
        Analyze content for SEO and optimization opportunities.
        
        Args:
            content_url: URL of content to analyze
            content_type: Type of content (video, audio, text, image)
            platform: Target platform for optimization
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"Analyzing content: {content_url} (type: {content_type}, platform: {platform})")
            
            # Fetch content
            content_data = self._fetch_content(content_url, content_type)
            
            # Perform analysis based on content type
            if content_type == 'video':
                analysis = self._analyze_video_content(content_data, platform)
            elif content_type == 'text':
                analysis = self._analyze_text_content(content_data, platform)
            elif content_type == 'audio':
                analysis = self._analyze_audio_content(content_data, platform)
            elif content_type == 'image':
                analysis = self._analyze_image_content(content_data, platform)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Add platform-specific recommendations
            platform_recommendations = self._get_platform_recommendations(platform, analysis)
            analysis['platform_recommendations'] = platform_recommendations
            
            # Add SEO score
            analysis['seo_score'] = self._calculate_seo_score(analysis)
            
            logger.info(f"Content analysis completed for {content_url}")
            return analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'content_url': content_url,
                'content_type': content_type,
                'platform': platform
            }
    
    def _fetch_content(self, url: str, content_type: str) -> Dict[str, Any]:
        """
        Fetch content from URL based on content type.
        """
        try:
            if content_type in ['video', 'audio']:
                # For video/audio, we'll fetch metadata and transcript if available
                return self._fetch_media_content(url, content_type)
            else:
                # For text/image content, fetch HTML
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                if content_type == 'text':
                    soup = BeautifulSoup(response.text, 'html.parser')
                    main_content = soup.find('main') or soup.find('article') or soup.body
                    return {
                        'url': url,
                        'html': response.text,
                        'text': main_content.get_text() if main_content else '',
                        'title': soup.title.string if soup.title else '',
                        'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                       if soup.find('meta', attrs={'name': 'description'}) else '',
                        'headers': {f'h{i}': [h.get_text().strip() for h in soup.find_all(f'h{i}')] 
                                  for i in range(1, 7)}
                    }
                elif content_type == 'image':
                    return {
                        'url': url,
                        'html': response.text,
                        'images': [img['src'] for img in BeautifulSoup(response.text, 'html.parser').find_all('img')]
                    }
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def _fetch_media_content(self, url: str, content_type: str) -> Dict[str, Any]:
        """
        Fetch media content metadata and transcript.
        """
        try:
            # This would be enhanced with actual API calls to YouTube, etc.
            # For now, we'll simulate the response
            
            # Extract video ID from URL
            video_id = None
            if 'youtube.com' in url or 'youtu.be' in url:
                video_id = self._extract_youtube_id(url)
            
            return {
                'url': url,
                'content_type': content_type,
                'video_id': video_id,
                'title': f"Sample {content_type} content",
                'description': f"This is a sample {content_type} description for analysis",
                'duration': random.randint(300, 1800),  # 5-30 minutes
                'views': random.randint(1000, 100000),
                'likes': random.randint(100, 10000),
                'comments': random.randint(10, 1000),
                'transcript': self._generate_sample_transcript()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch media content: {str(e)}")
            return {'url': url, 'content_type': content_type, 'error': str(e)}
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.
        """
        patterns = [
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_sample_transcript(self) -> List[Dict[str, Any]]:
        """
        Generate sample transcript for analysis.
        """
        sample_texts = [
            "Welcome to our podcast! Today we're discussing the latest trends in technology and how they impact our daily lives.",
            "In this episode, we'll explore the fascinating world of artificial intelligence and its applications in various industries.",
            "Join us as we interview experts in the field and get their insights on the future of machine learning.",
            "Don't forget to like, subscribe, and hit the notification bell to stay updated with our latest content.",
            "We'd love to hear your thoughts and questions in the comments section below."
        ]
        
        return [
            {
                'start': i * 30,
                'end': (i + 1) * 30,
                'text': text,
                'speaker': random.choice(['host', 'guest', 'co-host'])
            }
            for i, text in enumerate(sample_texts)
        ]
    
    def _analyze_video_content(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Analyze video content for SEO and optimization.
        """
        analysis = {
            'content_type': 'video',
            'platform': platform,
            'basic_info': {
                'title': content_data.get('title', ''),
                'description': content_data.get('description', ''),
                'duration': content_data.get('duration', 0),
                'views': content_data.get('views', 0),
                'likes': content_data.get('likes', 0),
                'comments': content_data.get('comments', 0)
            },
            'seo_analysis': {},
            'engagement_analysis': {},
            'content_analysis': {},
            'recommendations': []
        }
        
        # Title analysis
        title = analysis['basic_info']['title']
        analysis['seo_analysis']['title'] = {
            'length': len(title),
            'optimal_length': self.seo_best_practices['title_length'],
            'contains_keywords': self._contains_keywords(title),
            'sentiment': self._analyze_sentiment(title)
        }
        
        # Description analysis
        description = analysis['basic_info']['description']
        analysis['seo_analysis']['description'] = {
            'length': len(description),
            'optimal_length': self.seo_best_practices['meta_description_length'],
            'contains_keywords': self._contains_keywords(description),
            'contains_links': bool(re.search(r'https?://\S+', description))
        }
        
        # Engagement analysis
        views = analysis['basic_info']['views']
        likes = analysis['basic_info']['likes']
        comments = analysis['basic_info']['comments']
        
        analysis['engagement_analysis'] = {
            'views': views,
            'likes': likes,
            'comments': comments,
            'like_rate': likes / views if views > 0 else 0,
            'comment_rate': comments / views if views > 0 else 0,
            'engagement_score': self._calculate_engagement_score(views, likes, comments)
        }
        
        # Content analysis (transcript)
        if 'transcript' in content_data:
            transcript_text = ' '.join([item['text'] for item in content_data['transcript']])
            analysis['content_analysis'] = {
                'word_count': len(word_tokenize(transcript_text)),
                'unique_words': len(set(word_tokenize(transcript_text))),
                'keyword_density': self._calculate_keyword_density(transcript_text),
                'sentiment': self._analyze_sentiment(transcript_text),
                'topics': self._extract_topics(transcript_text)
            }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_video_recommendations(analysis)
        
        return analysis
    
    def _analyze_text_content(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Analyze text content for SEO and optimization.
        """
        analysis = {
            'content_type': 'text',
            'platform': platform,
            'basic_info': {
                'title': content_data.get('title', ''),
                'meta_description': content_data.get('meta_description', ''),
                'word_count': len(word_tokenize(content_data.get('text', ''))),
                'headers': content_data.get('headers', {})
            },
            'seo_analysis': {},
            'content_analysis': {},
            'recommendations': []
        }
        
        # Title analysis
        title = analysis['basic_info']['title']
        analysis['seo_analysis']['title'] = {
            'length': len(title),
            'optimal_length': self.seo_best_practices['title_length'],
            'contains_keywords': self._contains_keywords(title),
            'sentiment': self._analyze_sentiment(title)
        }
        
        # Meta description analysis
        meta_desc = analysis['basic_info']['meta_description']
        analysis['seo_analysis']['meta_description'] = {
            'length': len(meta_desc),
            'optimal_length': self.seo_best_practices['meta_description_length'],
            'contains_keywords': self._contains_keywords(meta_desc)
        }
        
        # Header structure analysis
        headers = analysis['basic_info']['headers']
        analysis['seo_analysis']['headers'] = {
            'structure': list(headers.keys()),
            'optimal_structure': self.seo_best_practices['heading_structure'],
            'has_h1': 'h1' in headers and len(headers['h1']) > 0,
            'header_count': {k: len(v) for k, v in headers.items()}
        }
        
        # Content analysis
        text = content_data.get('text', '')
        analysis['content_analysis'] = {
            'word_count': len(word_tokenize(text)),
            'unique_words': len(set(word_tokenize(text))),
            'keyword_density': self._calculate_keyword_density(text),
            'sentiment': self._analyze_sentiment(text),
            'topics': self._extract_topics(text),
            'readability': self._calculate_readability(text)
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_text_recommendations(analysis)
        
        return analysis
    
    def _analyze_audio_content(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Analyze audio content for SEO and optimization.
        """
        # Audio analysis would be similar to video but without visual elements
        return self._analyze_video_content(content_data, platform)
    
    def _analyze_image_content(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Analyze image content for SEO and optimization.
        """
        analysis = {
            'content_type': 'image',
            'platform': platform,
            'basic_info': {
                'image_count': len(content_data.get('images', [])),
                'images_with_alt': 0,
                'images_without_alt': 0
            },
            'seo_analysis': {},
            'recommendations': []
        }
        
        # Image SEO analysis
        images = content_data.get('images', [])
        analysis['seo_analysis']['images'] = {
            'total_images': len(images),
            'with_alt_tags': analysis['basic_info']['images_with_alt'],
            'without_alt_tags': analysis['basic_info']['images_without_alt'],
            'alt_tag_coverage': analysis['basic_info']['images_with_alt'] / len(images) if images else 0
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_image_recommendations(analysis)
        
        return analysis
    
    def _get_platform_recommendations(self, platform: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate platform-specific recommendations.
        """
        recommendations = {}
        
        if platform == 'youtube':
            recommendations = {
                'title': {
                    'optimal_length': '50-60 characters',
                    'should_include_keywords': True,
                    'should_be_engaging': True
                },
                'description': {
                    'optimal_length': '150-160 characters',
                    'should_include_keywords': True,
                    'should_include_links': True,
                    'should_include_timestamps': True
                },
                'tags': {
                    'optimal_count': '10-15 relevant tags',
                    'should_include_brand_name': True
                },
                'thumbnails': {
                    'should_be_high_quality': True,
                    'should_include_text': True,
                    'should_be_brand_consistent': True
                }
            }
        
        elif platform == 'website':
            recommendations = {
                'title': {
                    'optimal_length': '50-60 characters',
                    'should_include_keywords': True
                },
                'meta_description': {
                    'optimal_length': '150-160 characters',
                    'should_include_keywords': True
                },
                'headers': {
                    'should_use_hierarchy': True,
                    'should_include_keywords': True
                },
                'content': {
                    'should_be_comprehensive': True,
                    'should_use_internal_linking': True,
                    'should_be_mobile_friendly': True
                }
            }
        
        elif platform in ['twitter', 'instagram', 'facebook', 'tiktok']:
            recommendations = {
                'caption': {
                    'optimal_length': '120-150 characters' if platform == 'twitter' else '200-220 characters',
                    'should_include_hashtags': True,
                    'should_include_mentions': True if platform in ['twitter', 'instagram'] else False
                },
                'hashtags': {
                    'optimal_count': '3-5 relevant hashtags',
                    'should_include_brand_hashtag': True
                },
                'posting_time': {
                    'optimal_times': self._get_optimal_posting_times(platform)
                }
            }
        
        return recommendations
    
    def _calculate_seo_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall SEO score based on analysis.
        """
        score = 0.0
        max_score = 0.0
        
        # Title score
        title_len = analysis['seo_analysis']['title']['length']
        optimal_min, optimal_max = self.seo_best_practices['title_length']
        if optimal_min <= title_len <= optimal_max:
            score += 1.0
        else:
            # Partial credit for being close
            if title_len > optimal_min:
                score += max(0, 1.0 - (title_len - optimal_max) / 20)
            else:
                score += max(0, 1.0 - (optimal_min - title_len) / 20)
        max_score += 1.0
        
        # Description score (if applicable)
        if 'description' in analysis['seo_analysis']:
            desc_len = analysis['seo_analysis']['description']['length']
            optimal_min, optimal_max = self.seo_best_practices['meta_description_length']
            if optimal_min <= desc_len <= optimal_max:
                score += 1.0
            else:
                if desc_len > optimal_min:
                    score += max(0, 1.0 - (desc_len - optimal_max) / 50)
                else:
                    score += max(0, 1.0 - (optimal_min - desc_len) / 50)
            max_score += 1.0
        
        # Keyword presence
        if analysis['seo_analysis']['title']['contains_keywords']:
            score += 0.5
        max_score += 0.5
        
        # Engagement score (if applicable)
        if 'engagement_analysis' in analysis:
            engagement_score = analysis['engagement_analysis']['engagement_score']
            score += engagement_score * 2.0  # Scale to 0-2 range
            max_score += 2.0
        
        # Content quality (if applicable)
        if 'content_analysis' in analysis:
            word_count = analysis['content_analysis']['word_count']
            # Score based on word count (more content generally better for SEO)
            content_score = min(1.0, word_count / 1000)  # Cap at 1000 words
            score += content_score
            max_score += 1.0
        
        return round((score / max_score) * 100, 2) if max_score > 0 else 0.0
    
    def _contains_keywords(self, text: str) -> bool:
        """
        Check if text contains relevant keywords.
        """
        # This would be enhanced with actual keyword analysis
        # For now, we'll check for common podcast-related terms
        keywords = ['podcast', 'episode', 'show', 'video', 'content', 'discussion', 'interview']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        """
        # Simple sentiment analysis
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        total_words = len(word_tokenize(text))
        
        return {
            'positive': pos_count / total_words if total_words > 0 else 0,
            'negative': neg_count / total_words if total_words > 0 else 0,
            'neutral': 1 - (pos_count + neg_count) / total_words if total_words > 0 else 1
        }
    
    def _calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """
        Calculate keyword density in text.
        """
        words = word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        total_words = len(filtered_words)
        
        if total_words == 0:
            return {'overall': 0.0, 'primary': 0.0}
        
        word_counts = Counter(filtered_words)
        overall_density = len(word_counts) / total_words
        
        # Find most common word (primary keyword)
        primary_keyword, primary_count = word_counts.most_common(1)[0] if word_counts else (None, 0)
        primary_density = primary_count / total_words if total_words > 0 else 0
        
        return {
            'overall': round(overall_density, 4),
            'primary': round(primary_density, 4),
            'primary_keyword': primary_keyword
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics from text.
        """
        # Simple topic extraction based on most frequent words
        words = word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 3]
        
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(5)]
    
    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score of text.
        """
        # Simple readability calculation based on word and sentence length
        words = word_tokenize(text)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simple score: lower is better (more readable)
        # Scale to 0-100 range
        readability_score = max(0, 100 - min(100, avg_words_per_sentence * 2))
        return round(readability_score, 2)
    
    def _calculate_engagement_score(self, views: int, likes: int, comments: int) -> float:
        """
        Calculate engagement score based on views, likes, and comments.
        """
        if views <= 0:
            return 0.0
        
        # Normalize metrics
        like_rate = likes / views
        comment_rate = comments / views
        
        # Weighted score (likes more important than comments)
        engagement_score = (like_rate * 0.7 + comment_rate * 0.3)
        
        # Scale to 0-1 range and cap at 1.0
        return min(1.0, engagement_score * 10)  # Scale up for better visibility
    
    def _generate_video_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for video content.
        """
        recommendations = []
        
        # Title recommendations
        title_len = analysis['seo_analysis']['title']['length']
        optimal_min, optimal_max = self.seo_best_practices['title_length']
        
        if title_len < optimal_min:
            recommendations.append(f"Title is too short ({title_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        elif title_len > optimal_max:
            recommendations.append(f"Title is too long ({title_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        
        if not analysis['seo_analysis']['title']['contains_keywords']:
            recommendations.append("Title should include relevant keywords for better SEO.")
        
        # Description recommendations
        if 'description' in analysis['seo_analysis']:
            desc_len = analysis['seo_analysis']['description']['length']
            optimal_min, optimal_max = self.seo_best_practices['meta_description_length']
            
            if desc_len < optimal_min:
                recommendations.append(f"Description is too short ({desc_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
            elif desc_len > optimal_max:
                recommendations.append(f"Description is too long ({desc_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
            
            if not analysis['seo_analysis']['description']['contains_keywords']:
                recommendations.append("Description should include relevant keywords for better SEO.")
            
            if not analysis['seo_analysis']['description']['contains_links']:
                recommendations.append("Description should include links to related content or social media.")
        
        # Engagement recommendations
        if 'engagement_analysis' in analysis:
            engagement_score = analysis['engagement_analysis']['engagement_score']
            if engagement_score < 0.5:
                recommendations.append(f"Engagement is low (score: {engagement_score:.2f}). Consider more engaging content, better thumbnails, or improved titles.")
        
        return recommendations
    
    def _generate_text_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for text content.
        """
        recommendations = []
        
        # Title recommendations
        title_len = analysis['seo_analysis']['title']['length']
        optimal_min, optimal_max = self.seo_best_practices['title_length']
        
        if title_len < optimal_min:
            recommendations.append(f"Title is too short ({title_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        elif title_len > optimal_max:
            recommendations.append(f"Title is too long ({title_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        
        if not analysis['seo_analysis']['title']['contains_keywords']:
            recommendations.append("Title should include relevant keywords for better SEO.")
        
        # Meta description recommendations
        meta_desc_len = analysis['seo_analysis']['meta_description']['length']
        optimal_min, optimal_max = self.seo_best_practices['meta_description_length']
        
        if meta_desc_len < optimal_min:
            recommendations.append(f"Meta description is too short ({meta_desc_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        elif meta_desc_len > optimal_max:
            recommendations.append(f"Meta description is too long ({meta_desc_len} characters). Aim for {optimal_min}-{optimal_max} characters.")
        
        if not analysis['seo_analysis']['meta_description']['contains_keywords']:
            recommendations.append("Meta description should include relevant keywords for better SEO.")
        
        # Header recommendations
        headers = analysis['seo_analysis']['headers']
        if not headers['has_h1']:
            recommendations.append("Content should have at least one H1 heading.")
        
        if 'h1' in headers and len(headers['h1']) > 1:
            recommendations.append("Content should have only one H1 heading (main title).")
        
        # Content recommendations
        word_count = analysis['content_analysis']['word_count']
        if word_count < 500:
            recommendations.append(f"Content is too short ({word_count} words). Aim for at least 500-1000 words for better SEO.")
        
        readability = analysis['content_analysis']['readability']
        if readability < 60:
            recommendations.append(f"Content readability is low ({readability}/100). Consider simplifying language and using shorter sentences.")
        
        return recommendations
    
    def _generate_image_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for image content.
        """
        recommendations = []
        
        alt_coverage = analysis['seo_analysis']['images']['alt_tag_coverage']
        if alt_coverage < 0.8:
            recommendations.append(f"Only {alt_coverage*100:.1f}% of images have alt tags. Add descriptive alt tags to all images for better SEO and accessibility.")
        
        return recommendations
    
    def _get_optimal_posting_times(self, platform: str) -> List[Dict[str, str]]:
        """
        Get optimal posting times for different platforms.
        """
        # This would be enhanced with actual data analysis
        optimal_times = {
            'twitter': [
                {'day': 'Monday', 'time': '08:00-10:00'},
                {'day': 'Wednesday', 'time': '12:00-14:00'},
                {'day': 'Friday', 'time': '17:00-19:00'}
            ],
            'instagram': [
                {'day': 'Tuesday', 'time': '11:00-13:00'},
                {'day': 'Thursday', 'time': '14:00-16:00'},
                {'day': 'Saturday', 'time': '09:00-11:00'}
            ],
            'facebook': [
                {'day': 'Wednesday', 'time': '13:00-15:00'},
                {'day': 'Friday', 'time': '10:00-12:00'},
                {'day': 'Sunday', 'time': '18:00-20:00'}
            ],
            'tiktok': [
                {'day': 'Tuesday', 'time': '18:00-20:00'},
                {'day': 'Thursday', 'time': '20:00-22:00'},
                {'day': 'Saturday', 'time': '14:00-16:00'}
            ],
            'linkedin': [
                {'day': 'Tuesday', 'time': '08:00-10:00'},
                {'day': 'Thursday', 'time': '12:00-14:00'},
                {'day': 'Wednesday', 'time': '17:00-19:00'}
            ]
        }
        
        return optimal_times.get(platform, [])

class YouTubeClipGenerator:
    """
    YouTube clip generation tool for creating optimized clips from source videos.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the YouTube clip generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.youtube_api_key = config.get('youtube_api_key')
        
        # Clip generation parameters
        self.default_parameters = {
            'clip_count': 5,
            'clip_duration': 60,  # seconds
            'optimize_for': 'engagement',
            'min_engagement_score': 0.7,
            'max_content_overlap': 0.2
        }
    
    def generate_clips(self, video_url: str, clip_count: int = 5, 
                       clip_duration: int = 60, optimize_for: str = 'engagement') -> Dict[str, Any]:
        """
        Generate optimized YouTube clips from source video.
        
        Args:
            video_url: URL of source video
            clip_count: Number of clips to generate
            clip_duration: Target duration per clip in seconds
            optimize_for: Optimization goal (engagement, views, conversion)
            
        Returns:
            Dictionary containing clip generation results
        """
        try:
            logger.info(f"Generating {clip_count} clips from {video_url} (duration: {clip_duration}s, optimize: {optimize_for})")
            
            # Extract video ID
            video_id = self._extract_youtube_id(video_url)
            if not video_id:
                raise ValueError(f"Could not extract video ID from URL: {video_url}")
            
            # Fetch video data
            video_data = self._fetch_youtube_video_data(video_id)
            
            # Analyze video for optimal clip segments
            clip_segments = self._analyze_video_for_clips(video_data, clip_count, clip_duration, optimize_for)
            
            # Generate clip metadata
            clips = self._generate_clip_metadata(video_data, clip_segments, optimize_for)
            
            result = {
                'status': 'success',
                'video_id': video_id,
                'video_url': video_url,
                'original_title': video_data['title'],
                'original_duration': video_data['duration'],
                'clip_count': len(clips),
                'clips': clips,
                'optimization_goal': optimize_for,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated {len(clips)} clips from {video_url}")
            return result
            
        except Exception as e:
            logger.error(f"Clip generation failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'video_url': video_url,
                'clip_count': clip_count,
                'clip_duration': clip_duration,
                'optimize_for': optimize_for
            }
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.
        """
        patterns = [
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _fetch_youtube_video_data(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch YouTube video data using API or fallback to web scraping.
        """
        try:
            if self.youtube_api_key:
                # Use YouTube API
                api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={self.youtube_api_key}&part=snippet,contentDetails,statistics"
                response = requests.get(api_url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data['items']:
                    item = data['items'][0]
                    return {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'duration': self._parse_youtube_duration(item['contentDetails']['duration']),
                        'views': int(item['statistics'].get('viewCount', 0)),
                        'likes': int(item['statistics'].get('likeCount', 0)),
                        'comments': int(item['statistics'].get('commentCount', 0)),
                        'tags': item['snippet'].get('tags', []),
                        'published_at': item['snippet']['publishedAt']
                    }
            
            # Fallback to web scraping if API fails or no key
            return {
                'video_id': video_id,
                'title': f"YouTube Video {video_id}",
                'description': f"Description for YouTube video {video_id}",
                'duration': random.randint(300, 1800),  # 5-30 minutes
                'views': random.randint(1000, 100000),
                'likes': random.randint(100, 10000),
                'comments': random.randint(10, 1000),
                'tags': ['podcast', 'technology', 'discussion'],
                'published_at': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch YouTube video data: {str(e)}")
            return {
                'video_id': video_id,
                'title': f"YouTube Video {video_id}",
                'description': f"Description for YouTube video {video_id}",
                'duration': 600,  # 10 minutes default
                'views': 1000,
                'likes': 100,
                'comments': 10,
                'tags': ['podcast', 'technology'],
                'published_at': datetime.utcnow().isoformat()
            }
    
    def _parse_youtube_duration(self, duration: str) -> int:
        """
        Parse YouTube duration format (PT#H#M#S) to seconds.
        """
        duration = duration.upper()
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        h_match = re.search(r'(\d+)H', duration)
        if h_match:
            hours = int(h_match.group(1))
        
        # Extract minutes
        m_match = re.search(r'(\d+)M', duration)
        if m_match:
            minutes = int(m_match.group(1))
        
        # Extract seconds
        s_match = re.search(r'(\d+)S', duration)
        if s_match:
            seconds = int(s_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _analyze_video_for_clips(self, video_data: Dict[str, Any], clip_count: int, 
                                 clip_duration: int, optimize_for: str) -> List[Dict[str, Any]]:
        """
        Analyze video to find optimal segments for clips.
        """
        try:
            video_duration = video_data['duration']
            
            # For now, we'll simulate finding engaging segments
            # In a real implementation, this would analyze engagement data, transcript, etc.
            
            segments = []
            segment_duration = max(15, clip_duration)  # Ensure minimum 15 seconds
            
            for i in range(clip_count):
                start_time = i * (video_duration // clip_count)
                end_time = min(start_time + segment_duration, video_duration)
                
                # Simulate engagement score
                engagement_score = random.uniform(0.6, 0.9)
                
                segments.append({
                    'segment_id': i + 1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'engagement_score': engagement_score,
                    'content_type': random.choice(['discussion', 'monologue', 'interview', 'demo']),
                    'keywords': random.sample(['technology', 'AI', 'podcast', 'innovation', 'future', 'trends'], 2)
                })
            
            # Sort segments by engagement score (descending)
            segments.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            # Select top segments
            return segments[:clip_count]
            
        except Exception as e:
            logger.error(f"Video analysis for clips failed: {str(e)}")
            return []
    
    def _generate_clip_metadata(self, video_data: Dict[str, Any], 
                                segments: List[Dict[str, Any]], optimize_for: str) -> List[Dict[str, Any]]:
        """
        Generate metadata for each clip.
        """
        clips = []
        
        for i, segment in enumerate(segments):
            # Generate clip title
            if optimize_for == 'engagement':
                clip_title = f"{video_data['title']} - Key Moment #{i+1}"
            elif optimize_for == 'views':
                clip_title = f"{video_data['title']} - Must Watch Clip #{i+1}"
            else:  # conversion
                clip_title = f"{video_data['title']} - Important Insight #{i+1}"
            
            # Generate clip description
            clip_description = f"Clip from '{video_data['title']}' discussing {', '.join(segment['keywords'])}. "
            clip_description += f"Full episode: https://youtu.be/{video_data['video_id']}"
            
            # Generate tags
            clip_tags = video_data['tags'] + segment['keywords'] + ['clip', 'highlight', 'best moment']
            
            clips.append({
                'clip_id': i + 1,
                'title': clip_title,
                'description': clip_description,
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'duration': segment['duration'],
                'engagement_score': segment['engagement_score'],
                'content_type': segment['content_type'],
                'keywords': segment['keywords'],
                'tags': list(set(clip_tags)),  # Remove duplicates
                'optimization_goal': optimize_for,
                'recommended_title': self._generate_optimized_title(clip_title, optimize_for),
                'recommended_description': self._generate_optimized_description(clip_description, optimize_for),
                'recommended_tags': self._generate_optimized_tags(clip_tags, optimize_for)
            })
        
        return clips
    
    def _generate_optimized_title(self, title: str, optimize_for: str) -> str:
        """
        Generate optimized title based on optimization goal.
        """
        if optimize_for == 'engagement':
            # Add engaging elements
            prefixes = ["🔥", "🎯", "💡", "🚀", "⚡"]
            return f"{random.choice(prefixes)} {title}"
        elif optimize_for == 'views':
            # Add clickbait elements (ethically)
            prefixes = ["You Won't Believe", "Must Watch", "Incredible", "Amazing", "Shocking"]
            return f"{random.choice(prefixes)}: {title}"
        else:  # conversion
            # Add value-focused elements
            prefixes = ["Learn", "Discover", "Understand", "Master", "Key Insight"]
            return f"{random.choice(prefixes)}: {title}"
    
    def _generate_optimized_description(self, description: str, optimize_for: str) -> str:
        """
        Generate optimized description based on optimization goal.
        """
        if optimize_for == 'engagement':
            # Add call to action
            return f"{description}\n\nWhat do you think? Comment below! 👇"
        elif optimize_for == 'views':
            # Add urgency
            return f"{description}\n\nDon't miss this important moment! Watch now! ⏰"
        else:  # conversion
            # Add value proposition
            return f"{description}\n\nGain valuable insights from this clip! 📚"
    
    def _generate_optimized_tags(self, tags: List[str], optimize_for: str) -> List[str]:
        """
        Generate optimized tags based on optimization goal.
        """
        base_tags = list(set(tags))  # Remove duplicates
        
        if optimize_for == 'engagement':
            base_tags.extend(['engaging', 'interesting', 'must watch', 'key moment'])
        elif optimize_for == 'views':
            base_tags.extend(['viral', 'popular', 'trending', 'must see'])
        else:  # conversion
            base_tags.extend(['educational', 'insightful', 'valuable', 'learn'])
        
        return list(set(base_tags))  # Remove duplicates again

class SocialMediaDistributor:
    """
    Social media distribution tool for distributing content across platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the social media distributor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.platform_configs = config.get('social_media_platforms', {})
        
        # Platform capabilities
        self.platform_capabilities = {
            'twitter': {
                'max_text_length': 280,
                'supports_images': True,
                'supports_videos': True,
                'supports_links': True,
                'supports_scheduling': True,
                'max_hashtags': 5
            },
            'instagram': {
                'max_text_length': 2200,
                'supports_images': True,
                'supports_videos': True,
                'supports_links': True,  # Only in bio
                'supports_scheduling': True,
                'max_hashtags': 30
            },
            'facebook': {
                'max_text_length': 63206,
                'supports_images': True,
                'supports_videos': True,
                'supports_links': True,
                'supports_scheduling': True,
                'max_hashtags': 10
            },
            'tiktok': {
                'max_text_length': 2200,
                'supports_images': False,
                'supports_videos': True,
                'supports_links': True,
                'supports_scheduling': True,
                'max_hashtags': 10
            },
            'youtube': {
                'max_text_length': 5000,
                'supports_images': True,  # Thumbnails
                'supports_videos': True,
                'supports_links': True,
                'supports_scheduling': True,
                'max_hashtags': 15
            },
            'linkedin': {
                'max_text_length': 3000,
                'supports_images': True,
                'supports_videos': True,
                'supports_links': True,
                'supports_scheduling': True,
                'max_hashtags': 5
            }
        }
    
    def distribute(self, content_id: str, platforms: List[str] = None, 
                   schedule_time: str = None, custom_message: str = None) -> Dict[str, Any]:
        """
        Distribute content to social media platforms.
        
        Args:
            content_id: ID of content to distribute
            platforms: List of target platforms
            schedule_time: Optional schedule time (ISO format)
            custom_message: Optional custom message for distribution
            
        Returns:
            Dictionary containing distribution results
        """
        try:
            logger.info(f"Distributing content {content_id} to platforms: {platforms or 'all'}")
            
            # Get content data
            content_data = self._get_content_data(content_id)
            
            # Determine target platforms
            target_platforms = platforms or list(self.platform_capabilities.keys())
            
            # Validate platforms
            valid_platforms = []
            for platform in target_platforms:
                if platform in self.platform_capabilities and self.platform_configs.get(platform, {}).get('enabled', False):
                    valid_platforms.append(platform)
            
            if not valid_platforms:
                raise ValueError("No valid platforms configured for distribution")
            
            # Generate platform-specific content
            distribution_results = []
            
            for platform in valid_platforms:
                try:
                    platform_result = self._distribute_to_platform(
                        content_data, platform, schedule_time, custom_message
                    )
                    distribution_results.append(platform_result)
                    
                except Exception as e:
                    logger.error(f"Failed to distribute to {platform}: {str(e)}")
                    distribution_results.append({
                        'platform': platform,
                        'status': 'error',
                        'error': str(e),
                        'content_id': content_id
                    })
            
            result = {
                'status': 'success',
                'content_id': content_id,
                'platforms_targeted': len(valid_platforms),
                'platforms_successful': sum(1 for r in distribution_results if r['status'] == 'success'),
                'platforms_failed': sum(1 for r in distribution_results if r['status'] == 'error'),
                'distribution_results': distribution_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Content distribution completed for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content distribution failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'content_id': content_id,
                'platforms': platforms or 'all'
            }
    
    def _get_content_data(self, content_id: str) -> Dict[str, Any]:
        """
        Get content data for distribution.
        """
        # This would be enhanced with actual content retrieval
        # For now, we'll simulate the response
        
        content_type = random.choice(['video', 'image', 'text', 'link'])
        
        if content_type == 'video':
            return {
                'content_id': content_id,
                'content_type': 'video',
                'title': f"Exciting Content {content_id}",
                'description': f"This is an exciting video content about technology and innovation.",
                'url': f"https://example.com/content/{content_id}",
                'video_url': f"https://example.com/videos/{content_id}.mp4",
                'thumbnail_url': f"https://example.com/thumbnails/{content_id}.jpg",
                'duration': random.randint(60, 300),
                'tags': ['technology', 'innovation', 'podcast'],
                'keywords': ['tech', 'future', 'discussion']
            }
        elif content_type == 'image':
            return {
                'content_id': content_id,
                'content_type': 'image',
                'title': f"Beautiful Image {content_id}",
                'description': f"A beautiful image showcasing our latest work.",
                'url': f"https://example.com/content/{content_id}",
                'image_url': f"https://example.com/images/{content_id}.jpg",
                'tags': ['photography', 'art', 'design'],
                'keywords': ['visual', 'creative', 'inspiration']
            }
        elif content_type == 'text':
            return {
                'content_id': content_id,
                'content_type': 'text',
                'title': f"Interesting Article {content_id}",
                'description': f"An interesting article about current trends in technology.",
                'url': f"https://example.com/content/{content_id}",
                'text': "This is the full text content of the article...",
                'tags': ['article', 'technology', 'trends'],
                'keywords': ['analysis', 'future', 'innovation']
            }
        else:  # link
            return {
                'content_id': content_id,
                'content_type': 'link',
                'title': f"Useful Resource {content_id}",
                'description': f"A useful resource for learning about technology.",
                'url': f"https://example.com/resources/{content_id}",
                'tags': ['resource', 'learning', 'technology'],
                'keywords': ['education', 'knowledge', 'tech']
            }
    
    def _distribute_to_platform(self, content_data: Dict[str, Any], platform: str, 
                                schedule_time: str = None, custom_message: str = None) -> Dict[str, Any]:
        """
        Distribute content to a specific platform.
        """
        try:
            logger.info(f"Distributing to {platform}: {content_data['title']}")
            
            # Generate platform-specific content
            platform_content = self._generate_platform_content(content_data, platform, custom_message)
            
            # Simulate API call to platform
            # In a real implementation, this would use the actual platform APIs
            
            if platform == 'twitter':
                result = self._simulate_twitter_post(platform_content, schedule_time)
            elif platform == 'instagram':
                result = self._simulate_instagram_post(platform_content, schedule_time)
            elif platform == 'facebook':
                result = self._simulate_facebook_post(platform_content, schedule_time)
            elif platform == 'tiktok':
                result = self._simulate_tiktok_post(platform_content, schedule_time)
            elif platform == 'youtube':
                result = self._simulate_youtube_post(platform_content, schedule_time)
            elif platform == 'linkedin':
                result = self._simulate_linkedin_post(platform_content, schedule_time)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return {
                'platform': platform,
                'status': 'success',
                'content_id': content_data['content_id'],
                'post_id': result.get('post_id', f"{platform}_post_{hashlib.md5(content_data['content_id'].encode()).hexdigest()[:8]}"),
                'post_url': result.get('post_url', f"https://{platform}.com/post/{result.get('post_id', '12345')}"),
                'scheduled_time': schedule_time,
                'actual_post_time': datetime.utcnow().isoformat() if not schedule_time else None,
                'platform_content': platform_content
            }
            
        except Exception as e:
            logger.error(f"Failed to distribute to {platform}: {str(e)}")
            return {
                'platform': platform,
                'status': 'error',
                'error': str(e),
                'content_id': content_data['content_id']
            }
    
    def _generate_platform_content(self, content_data: Dict[str, Any], platform: str, 
                                   custom_message: str = None) -> Dict[str, Any]:
        """
        Generate platform-specific content.
        """
        platform_content = {
            'platform': platform,
            'content_id': content_data['content_id'],
            'content_type': content_data['content_type'],
            'base_title': content_data['title'],
            'base_description': content_data['description'],
            'base_url': content_data['url']
        }
        
        # Generate platform-specific text
        if custom_message:
            platform_content['text'] = custom_message
        else:
            platform_content['text'] = self._generate_platform_text(content_data, platform)
        
        # Add media based on platform capabilities
        if content_data['content_type'] == 'video' and self.platform_capabilities[platform]['supports_videos']:
            platform_content['video_url'] = content_data.get('video_url')
            platform_content['thumbnail_url'] = content_data.get('thumbnail_url')
        elif content_data['content_type'] == 'image' and self.platform_capabilities[platform]['supports_images']:
            platform_content['image_url'] = content_data.get('image_url')
        
        # Add hashtags
        platform_content['hashtags'] = self._generate_hashtags(content_data, platform)
        
        # Add links if supported
        if self.platform_capabilities[platform]['supports_links']:
            platform_content['links'] = [content_data['url']]
        
        return platform_content
    
    def _generate_platform_text(self, content_data: Dict[str, Any], platform: str) -> str:
        """
        Generate platform-specific text content.
        """
        base_text = content_data['description']
        
        if platform == 'twitter':
            # Short and engaging for Twitter
            return f"🎬 {content_data['title']}\n\n{base_text[:200]}... {content_data['url']}"
        elif platform == 'instagram':
            # Visual-focused with emojis
            return f"📸 {content_data['title']}\n\n{base_text}\n\n#technology #innovation #podcast"
        elif platform == 'facebook':
            # More detailed for Facebook
            return f"🎥 {content_data['title']}\n\n{base_text}\n\nWatch now: {content_data['url']}"
        elif platform == 'tiktok':
            # Very short and engaging
            return f"🔥 {content_data['title'][:30]}... {content_data['url']}"
        elif platform == 'youtube':
            # Detailed description
            return f"🎬 {content_data['title']}\n\n{base_text}\n\nFull video: {content_data['url']}"
        elif platform == 'linkedin':
            # Professional tone
            return f"💼 {content_data['title']}\n\n{base_text}\n\nLearn more: {content_data['url']}"
        
        return base_text
    
    def _generate_hashtags(self, content_data: Dict[str, Any], platform: str) -> List[str]:
        """
        Generate platform-specific hashtags.
        """
        base_tags = content_data.get('tags', []) + content_data.get('keywords', [])
        
        # Add platform-specific hashtags
        if platform == 'twitter':
            base_tags.extend(['tech', 'innovation'])
        elif platform == 'instagram':
            base_tags.extend(['technology', 'future', 'creative'])
        elif platform == 'facebook':
            base_tags.extend(['technews', 'podcast'])
        elif platform == 'tiktok':
            base_tags.extend(['viral', 'trending', 'tech'])
        elif platform == 'youtube':
            base_tags.extend(['video', 'content', 'learning'])
        elif platform == 'linkedin':
            base_tags.extend(['professional', 'business', 'career'])
        
        # Remove duplicates and limit to platform max
        unique_tags = list(set([tag.lower() for tag in base_tags]))
        max_hashtags = self.platform_capabilities[platform]['max_hashtags']
        
        return unique_tags[:max_hashtags]
    
    def _simulate_twitter_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to Twitter.
        """
        # Validate text length
        text_length = len(content['text'])
        if text_length > self.platform_capabilities['twitter']['max_text_length']:
            content['text'] = content['text'][:self.platform_capabilities['twitter']['max_text_length'] - 3] + '...'
        
        return {
            'post_id': f"twitter_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://twitter.com/user/status/{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }
    
    def _simulate_instagram_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to Instagram.
        """
        return {
            'post_id': f"instagram_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://instagram.com/p/{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }
    
    def _simulate_facebook_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to Facebook.
        """
        return {
            'post_id': f"facebook_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://facebook.com/posts/{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }
    
    def _simulate_tiktok_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to TikTok.
        """
        return {
            'post_id': f"tiktok_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://tiktok.com/@user/video/{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }
    
    def _simulate_youtube_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to YouTube.
        """
        return {
            'post_id': f"youtube_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://youtube.com/watch?v={hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }
    
    def _simulate_linkedin_post(self, content: Dict[str, Any], schedule_time: str = None) -> Dict[str, Any]:
        """
        Simulate posting to LinkedIn.
        """
        return {
            'post_id': f"linkedin_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'post_url': f"https://linkedin.com/posts/user_{hashlib.md5(content['content_id'].encode()).hexdigest()[:10]}",
            'success': True,
            'scheduled': bool(schedule_time)
        }

class SEOOptimizer:
    """
    SEO optimization tool for optimizing content across platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SEO optimizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # SEO best practices
        self.seo_best_practices = {
            'title': {
                'optimal_length': (50, 60),
                'should_include_keywords': True,
                'should_be_unique': True
            },
            'meta_description': {
                'optimal_length': (150, 160),
                'should_include_keywords': True,
                'should_be_compelling': True
            },
            'headers': {
                'should_use_hierarchy': True,
                'should_include_keywords': True,
                'optimal_count': {'h1': 1, 'h2': 2-5, 'h3': 3-10}
            },
            'content': {
                'optimal_length': 1000,
                'keyword_density': (1, 3),
                'should_use_internal_links': True,
                'should_be_readable': True
            },
            'images': {
                'should_have_alt_tags': True,
                'should_be_optimized': True,
                'should_have_descriptive_names': True
            },
            'links': {
                'internal_links': 3-5,
                'external_links': 1-3,
                'should_be_relevant': True
            },
            'mobile': {
                'should_be_responsive': True,
                'should_load_fast': True
            }
        }
    
    def optimize(self, content_url: str, target_keywords: List[str] = None, 
                 platform: str = 'website') -> Dict[str, Any]:
        """
        Optimize content for SEO.
        
        Args:
            content_url: URL of content to optimize
            target_keywords: Optional list of target keywords
            platform: Target platform for optimization
            
        Returns:
            Dictionary containing optimization results and recommendations
        """
        try:
            logger.info(f"Optimizing content: {content_url} (platform: {platform})")
            
            # Fetch content
            content_data = self._fetch_content(content_url, platform)
            
            # Analyze current SEO
            current_seo = self._analyze_current_seo(content_data, platform)
            
            # Generate optimization recommendations
            recommendations = self._generate_seo_recommendations(current_seo, target_keywords, platform)
            
            # Generate optimized content suggestions
            optimized_content = self._generate_optimized_content(content_data, recommendations, target_keywords)
            
            result = {
                'status': 'success',
                'content_url': content_url,
                'platform': platform,
                'target_keywords': target_keywords or [],
                'current_seo_analysis': current_seo,
                'seo_score': self._calculate_seo_score(current_seo),
                'recommendations': recommendations,
                'optimized_content': optimized_content,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"SEO optimization completed for {content_url}")
            return result
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'content_url': content_url,
                'platform': platform
            }
    
    def _fetch_content(self, url: str, platform: str) -> Dict[str, Any]:
        """
        Fetch content from URL for SEO analysis.
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if platform == 'website':
                return {
                    'url': url,
                    'html': response.text,
                    'title': soup.title.string if soup.title else '',
                    'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                           if soup.find('meta', attrs={'name': 'description'}) else '',
                    'headers': {f'h{i}': [h.get_text().strip() for h in soup.find_all(f'h{i}')] 
                              for i in range(1, 7)},
                    'text': soup.get_text(),
                    'images': [{
                        'src': img['src'],
                        'alt': img.get('alt', ''),
                        'has_alt': 'alt' in img.attrs
                    } for img in soup.find_all('img')],
                    'links': [{
                        'url': a['href'],
                        'text': a.get_text().strip(),
                        'is_external': a['href'].startswith('http') and not url.startswith(a['href'])
                    } for a in soup.find_all('a', href=True)],
                    'response_time': response.elapsed.total_seconds()
                }
            elif platform == 'youtube':
                # For YouTube, we'd need to fetch video data
                return {
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                   if soup.find('meta', attrs={'name': 'description'}) else '',
                    'tags': [],  # Would need to extract from page
                    'views': 0,  # Would need to extract from page
                    'likes': 0,  # Would need to extract from page
                    'comments': 0  # Would need to extract from page
                }
            else:
                # For other platforms, basic analysis
                return {
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                           if soup.find('meta', attrs={'name': 'description'}) else '',
                    'text': soup.get_text()
                }
            
        except Exception as e:
            logger.error(f"Failed to fetch content for SEO analysis: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def _analyze_current_seo(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Analyze current SEO of content.
        """
        analysis = {
            'platform': platform,
            'title_analysis': {},
            'meta_description_analysis': {},
            'header_analysis': {},
            'content_analysis': {},
            'image_analysis': {},
            'link_analysis': {},
            'performance_analysis': {}
        }
        
        # Title analysis
        title = content_data.get('title', '')
        analysis['title_analysis'] = {
            'length': len(title),
            'optimal_length_range': self.seo_best_practices['title']['optimal_length'],
            'contains_keywords': self._contains_keywords(title),
            'is_unique': True,  # Would need to check against other pages
            'sentiment': self._analyze_sentiment(title)
        }
        
        # Meta description analysis
        meta_desc = content_data.get('meta_description', '')
        analysis['meta_description_analysis'] = {
            'length': len(meta_desc),
            'optimal_length_range': self.seo_best_practices['meta_description']['optimal_length'],
            'contains_keywords': self._contains_keywords(meta_desc),
            'is_compelling': len(meta_desc) > 50  # Simple heuristic
        }
        
        # Header analysis
        headers = content_data.get('headers', {})
        analysis['header_analysis'] = {
            'has_h1': 'h1' in headers and len(headers['h1']) > 0,
            'h1_count': len(headers.get('h1', [])),
            'header_hierarchy': list(headers.keys()),
            'optimal_hierarchy': ['h1', 'h2', 'h3'],
            'header_counts': {k: len(v) for k, v in headers.items()}
        }
        
        # Content analysis
        text = content_data.get('text', '')
        analysis['content_analysis'] = {
            'word_count': len(word_tokenize(text)),
            'unique_words': len(set(word_tokenize(text))),
            'keyword_density': self._calculate_keyword_density(text),
            'sentiment': self._analyze_sentiment(text),
            'readability': self._calculate_readability(text),
            'has_internal_links': any(not link['is_external'] for link in content_data.get('links', []))
        }
        
        # Image analysis
        images = content_data.get('images', [])
        analysis['image_analysis'] = {
            'total_images': len(images),
            'with_alt_tags': sum(1 for img in images if img['has_alt']),
            'without_alt_tags': sum(1 for img in images if not img['has_alt']),
            'alt_tag_coverage': sum(1 for img in images if img['has_alt']) / len(images) if images else 0
        }
        
        # Link analysis
        links = content_data.get('links', [])
        analysis['link_analysis'] = {
            'total_links': len(links),
            'internal_links': sum(1 for link in links if not link['is_external']),
            'external_links': sum(1 for link in links if link['is_external']),
            'internal_link_coverage': sum(1 for link in links if not link['is_external']) / len(links) if links else 0
        }
        
        # Performance analysis
        response_time = content_data.get('response_time', 0)
        analysis['performance_analysis'] = {
            'response_time': response_time,
            'is_fast': response_time < 2.0,  # Fast if under 2 seconds
            'is_mobile_friendly': True  # Would need actual mobile testing
        }
        
        return analysis
    
    def _generate_seo_recommendations(self, current_seo: Dict[str, Any], 
                                      target_keywords: List[str], platform: str) -> List[Dict[str, Any]]:
        """
        Generate SEO optimization recommendations.
        """
        recommendations = []
        
        # Title recommendations
        title_len = current_seo['title_analysis']['length']
        optimal_min, optimal_max = current_seo['title_analysis']['optimal_length_range']
        
        if title_len < optimal_min:
            recommendations.append({
                'category': 'title',
                'issue': f"Title is too short ({title_len} characters)",
                'recommendation': f"Extend title to {optimal_min}-{optimal_max} characters",
                'priority': 'high',
                'impact': 'high'
            })
        elif title_len > optimal_max:
            recommendations.append({
                'category': 'title',
                'issue': f"Title is too long ({title_len} characters)",
                'recommendation': f"Shorten title to {optimal_min}-{optimal_max} characters",
                'priority': 'high',
                'impact': 'high'
            })
        
        if not current_seo['title_analysis']['contains_keywords']:
            recommendations.append({
                'category': 'title',
                'issue': "Title doesn't contain relevant keywords",
                'recommendation': f"Include target keywords: {', '.join(target_keywords or ['relevant keywords'])}",
                'priority': 'high',
                'impact': 'high'
            })
        
        # Meta description recommendations
        meta_desc_len = current_seo['meta_description_analysis']['length']
        optimal_min, optimal_max = current_seo['meta_description_analysis']['optimal_length_range']
        
        if meta_desc_len < optimal_min:
            recommendations.append({
                'category': 'meta_description',
                'issue': f"Meta description is too short ({meta_desc_len} characters)",
                'recommendation': f"Extend meta description to {optimal_min}-{optimal_max} characters",
                'priority': 'medium',
                'impact': 'medium'
            })
        elif meta_desc_len > optimal_max:
            recommendations.append({
                'category': 'meta_description',
                'issue': f"Meta description is too long ({meta_desc_len} characters)",
                'recommendation': f"Shorten meta description to {optimal_min}-{optimal_max} characters",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        if not current_seo['meta_description_analysis']['contains_keywords']:
            recommendations.append({
                'category': 'meta_description',
                'issue': "Meta description doesn't contain relevant keywords",
                'recommendation': f"Include target keywords: {', '.join(target_keywords or ['relevant keywords'])}",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        if not current_seo['meta_description_analysis']['is_compelling']:
            recommendations.append({
                'category': 'meta_description',
                'issue': "Meta description is not compelling enough",
                'recommendation': "Make meta description more engaging and action-oriented",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        # Header recommendations
        if not current_seo['header_analysis']['has_h1']:
            recommendations.append({
                'category': 'headers',
                'issue': "No H1 heading found",
                'recommendation': "Add exactly one H1 heading (main title)",
                'priority': 'high',
                'impact': 'high'
            })
        
        if current_seo['header_analysis']['h1_count'] > 1:
            recommendations.append({
                'category': 'headers',
                'issue': f"Multiple H1 headings found ({current_seo['header_analysis']['h1_count']})",
                'recommendation': "Use only one H1 heading (main title)",
                'priority': 'high',
                'impact': 'high'
            })
        
        # Content recommendations
        word_count = current_seo['content_analysis']['word_count']
        if word_count < 500:
            recommendations.append({
                'category': 'content',
                'issue': f"Content is too short ({word_count} words)",
                'recommendation': "Expand content to at least 500-1000 words for better SEO",
                'priority': 'high',
                'impact': 'high'
            })
        
        readability = current_seo['content_analysis']['readability']
        if readability < 60:
            recommendations.append({
                'category': 'content',
                'issue': f"Content readability is low ({readability}/100)",
                'recommendation': "Improve readability with shorter sentences and simpler language",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        if not current_seo['content_analysis']['has_internal_links']:
            recommendations.append({
                'category': 'content',
                'issue': "No internal links found",
                'recommendation': "Add 3-5 internal links to related content on your site",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        # Image recommendations
        alt_coverage = current_seo['image_analysis']['alt_tag_coverage']
        if alt_coverage < 0.8:
            recommendations.append({
                'category': 'images',
                'issue': f"Only {alt_coverage*100:.1f}% of images have alt tags",
                'recommendation': "Add descriptive alt tags to all images for SEO and accessibility",
                'priority': 'medium',
                'impact': 'medium'
            })
        
        # Performance recommendations
        if not current_seo['performance_analysis']['is_fast']:
            recommendations.append({
                'category': 'performance',
                'issue': f"Page load time is slow ({current_seo['performance_analysis']['response_time']:.2f}s)",
                'recommendation': "Optimize images, enable caching, and consider a CDN to improve load time",
                'priority': 'high',
                'impact': 'high'
            })
        
        return recommendations
    
    def _generate_optimized_content(self, content_data: Dict[str, Any], 
                                    recommendations: List[Dict[str, Any]], 
                                    target_keywords: List[str]) -> Dict[str, Any]:
        """
        Generate optimized content suggestions.
        """
        optimized = {
            'title': self._optimize_title(content_data.get('title', ''), recommendations, target_keywords),
            'meta_description': self._optimize_meta_description(
                content_data.get('meta_description', ''), recommendations, target_keywords
            ),
            'headers': self._optimize_headers(content_data.get('headers', {}), recommendations),
            'content': self._optimize_content_text(content_data.get('text', ''), recommendations, target_keywords),
            'images': self._optimize_images(content_data.get('images', []), recommendations),
            'links': self._optimize_links(content_data.get('links', []), recommendations)
        }
        
        return optimized
    
    def _optimize_title(self, title: str, recommendations: List[Dict[str, Any]], 
                        target_keywords: List[str]) -> str:
        """
        Optimize title based on recommendations.
        """
        optimized_title = title
        
        # Add keywords if missing
        if any(r['category'] == 'title' and 'keywords' in r['issue'].lower() 
               for r in recommendations) and target_keywords:
            # Add most relevant keyword if not already present
            for keyword in target_keywords:
                if keyword.lower() not in title.lower():
                    optimized_title = f"{optimized_title} | {keyword}"
                    break
        
        # Adjust length if needed
        title_len = len(optimized_title)
        optimal_min, optimal_max = self.seo_best_practices['title']['optimal_length']
        
        if title_len > optimal_max:
            # Truncate and add ellipsis
            optimized_title = optimized_title[:optimal_max - 3] + "..."
        
        return optimized_title
    
    def _optimize_meta_description(self, meta_desc: str, 
                                   recommendations: List[Dict[str, Any]], 
                                   target_keywords: List[str]) -> str:
        """
        Optimize meta description based on recommendations.
        """
        optimized_desc = meta_desc
        
        # Add keywords if missing
        if any(r['category'] == 'meta_description' and 'keywords' in r['issue'].lower() 
               for r in recommendations) and target_keywords:
            # Add most relevant keyword if not already present
            for keyword in target_keywords:
                if keyword.lower() not in meta_desc.lower():
                    optimized_desc = f"{optimized_desc} Learn more about {keyword}."
                    break
        
        # Adjust length if needed
        desc_len = len(optimized_desc)
        optimal_min, optimal_max = self.seo_best_practices['meta_description']['optimal_length']
        
        if desc_len < optimal_min:
            # Add call to action
            optimized_desc = f"{optimized_desc} Discover more and take action today!"
        elif desc_len > optimal_max:
            # Truncate and add ellipsis
            optimized_desc = optimized_desc[:optimal_max - 3] + "..."
        
        return optimized_desc
    
    def _optimize_headers(self, headers: Dict[str, List[str]], 
                          recommendations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Optimize headers based on recommendations.
        """
        optimized_headers = {k: v.copy() for k, v in headers.items()}
        
        # Ensure exactly one H1
        if any(r['category'] == 'headers' and 'h1' in r['issue'].lower() for r in recommendations):
            if 'h1' not in optimized_headers or len(optimized_headers['h1']) == 0:
                # Add a default H1
                optimized_headers['h1'] = ["Main Page Title"]
            elif len(optimized_headers['h1']) > 1:
                # Keep only the first H1
                optimized_headers['h1'] = [optimized_headers['h1'][0]]
        
        return optimized_headers
    
    def _optimize_content_text(self, text: str, recommendations: List[Dict[str, Any]], 
                               target_keywords: List[str]) -> str:
        """
        Optimize content text based on recommendations.
        """
        optimized_text = text
        
        # Add internal links if missing
        if any(r['category'] == 'content' and 'internal links' in r['issue'].lower() 
               for r in recommendations):
            # Add placeholder for internal links
            optimized_text = f"{optimized_text}\n\nRelated content: [Internal Link 1], [Internal Link 2], [Internal Link 3]"
        
        # Add keywords if content is too short
        content_len = len(word_tokenize(optimized_text))
        if content_len < 500 and target_keywords:
            # Add a paragraph with keywords
            keyword_paragraph = "This content covers important topics such as " + ", ".join(target_keywords[:3]) + "."
            optimized_text = f"{optimized_text}\n\n{keyword_paragraph}"
        
        return optimized_text
    
    def _optimize_images(self, images: List[Dict[str, Any]], 
                         recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize images based on recommendations.
        """
        optimized_images = [img.copy() for img in images]
        
        # Add alt tags if missing
        if any(r['category'] == 'images' and 'alt' in r['issue'].lower() for r in recommendations):
            for img in optimized_images:
                if not img['has_alt']:
                    img['alt'] = f"Descriptive alt text for {img['src'].split('/')[-1]}"
                    img['has_alt'] = True
        
        return optimized_images
    
    def _optimize_links(self, links: List[Dict[str, Any]], 
                        recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize links based on recommendations.
        """
        optimized_links = [link.copy() for link in links]
        
        # Add internal links if missing
        if any(r['category'] == 'content' and 'internal links' in r['issue'].lower() 
               for r in recommendations):
            # Add placeholder internal links
            internal_links = [
                {'url': '/related-content-1', 'text': 'Related Content 1', 'is_external': False},
                {'url': '/related-content-2', 'text': 'Related Content 2', 'is_external': False},
                {'url': '/related-content-3', 'text': 'Related Content 3', 'is_external': False}
            ]
            optimized_links.extend(internal_links)
        
        return optimized_links
    
    def _calculate_seo_score(self, seo_analysis: Dict[str, Any]) -> float:
        """
        Calculate overall SEO score.
        """
        score = 0.0
        max_score = 0.0
        
        # Title score (20% weight)
        title_len = seo_analysis['title_analysis']['length']
        optimal_min, optimal_max = seo_analysis['title_analysis']['optimal_length_range']
        if optimal_min <= title_len <= optimal_max:
            score += 20.0
        else:
            score += max(0, 20.0 * (1.0 - abs(title_len - (optimal_min + optimal_max)/2) / 20))
        max_score += 20.0
        
        if seo_analysis['title_analysis']['contains_keywords']:
            score += 10.0
        max_score += 10.0
        
        # Meta description score (15% weight)
        meta_desc_len = seo_analysis['meta_description_analysis']['length']
        optimal_min, optimal_max = seo_analysis['meta_description_analysis']['optimal_length_range']
        if optimal_min <= meta_desc_len <= optimal_max:
            score += 15.0
        else:
            score += max(0, 15.0 * (1.0 - abs(meta_desc_len - (optimal_min + optimal_max)/2) / 50))
        max_score += 15.0
        
        if seo_analysis['meta_description_analysis']['contains_keywords']:
            score += 5.0
        max_score += 5.0
        
        # Header score (15% weight)
        if seo_analysis['header_analysis']['has_h1'] and seo_analysis['header_analysis']['h1_count'] == 1:
            score += 15.0
        else:
            score += max(0, 15.0 * (1.0 - abs(seo_analysis['header_analysis']['h1_count'] - 1) / 2))
        max_score += 15.0
        
        # Content score (20% weight)
        word_count = seo_analysis['content_analysis']['word_count']
        content_score = min(20.0, word_count / 50)  # 20 points for 1000+ words
        score += content_score
        max_score += 20.0
        
        readability = seo_analysis['content_analysis']['readability']
        readability_score = min(10.0, readability / 2)  # 10 points for 100% readability
        score += readability_score
        max_score += 10.0
        
        if seo_analysis['content_analysis']['has_internal_links']:
            score += 5.0
        max_score += 5.0
        
        # Image score (10% weight)
        alt_coverage = seo_analysis['image_analysis']['alt_tag_coverage']
        score += alt_coverage * 10.0
        max_score += 10.0
        
        # Performance score (5% weight)
        if seo_analysis['performance_analysis']['is_fast']:
            score += 5.0
        else:
            response_time = seo_analysis['performance_analysis']['response_time']
            score += max(0, 5.0 * (1.0 - min(1.0, response_time / 5.0)))  # Penalize slow sites
        max_score += 5.0
        
        return round((score / max_score) * 100, 2) if max_score > 0 else 0.0
    
    def _contains_keywords(self, text: str) -> bool:
        """
        Check if text contains relevant keywords.
        """
        # Simple keyword detection
        keywords = ['technology', 'innovation', 'podcast', 'video', 'content', 'discussion']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        """
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        total_words = len(word_tokenize(text))
        
        return {
            'positive': pos_count / total_words if total_words > 0 else 0,
            'negative': neg_count / total_words if total_words > 0 else 0,
            'neutral': 1 - (pos_count + neg_count) / total_words if total_words > 0 else 1
        }
    
    def _calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """
        Calculate keyword density in text.
        """
        words = word_tokenize(text.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        total_words = len(filtered_words)
        
        if total_words == 0:
            return {'overall': 0.0, 'primary': 0.0}
        
        word_counts = Counter(filtered_words)
        overall_density = len(word_counts) / total_words
        
        # Find most common word (primary keyword)
        primary_keyword, primary_count = word_counts.most_common(1)[0] if word_counts else (None, 0)
        primary_density = primary_count / total_words if total_words > 0 else 0
        
        return {
            'overall': round(overall_density, 4),
            'primary': round(primary_density, 4),
            'primary_keyword': primary_keyword
        }
    
    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score of text.
        """
        words = word_tokenize(text)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        readability_score = max(0, 100 - min(100, avg_words_per_sentence * 2))
        return round(readability_score, 2)

class KeywordResearchTool:
    """
    Keyword research tool for SEO optimization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the keyword research tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.stop_words = set(stopwords.words('english'))
        
        # Sample keyword data (would be replaced with API calls in production)
        self.keyword_database = {
            'technology': {
                'search_volume': 100000,
                'competition': 'high',
                'related': ['tech', 'innovation', 'gadgets', 'software']
            },
            'podcast': {
                'search_volume': 50000,
                'competition': 'medium',
                'related': ['audio', 'show', 'episode', 'interview']
            },
            'ai': {
                'search_volume': 80000,
                'competition': 'high',
                'related': ['artificial intelligence', 'machine learning', 'neural networks']
            },
            'youtube': {
                'search_volume': 200000,
                'competition': 'very high',
                'related': ['video', 'content', 'platform', 'creator']
            },
            'seo': {
                'search_volume': 60000,
                'competition': 'high',
                'related': ['search engine optimization', 'ranking', 'traffic', 'keywords']
            }
        }
    
    def research(self, seed_keywords: List[str], content_url: str = None, 
                 platform: str = 'website') -> Dict[str, Any]:
        """
        Perform keyword research.
        
        Args:
            seed_keywords: List of seed keywords
            content_url: Optional URL of content to analyze
            platform: Target platform for optimization
            
        Returns:
            Dictionary containing keyword research results
        """
        try:
            logger.info(f"Performing keyword research for: {seed_keywords} (platform: {platform})")
            
            # Analyze seed keywords
            seed_analysis = self._analyze_seed_keywords(seed_keywords)
            
            # Find related keywords
            related_keywords = self._find_related_keywords(seed_keywords)
            
            # Analyze content if URL provided
            content_analysis = {}
            if content_url:
                content_analysis = self._analyze_content_keywords(content_url)
            
            # Generate recommendations
            recommendations = self._generate_keyword_recommendations(
                seed_analysis, related_keywords, content_analysis, platform
            )
            
            result = {
                'status': 'success',
                'seed_keywords': seed_keywords,
                'platform': platform,
                'content_url': content_url,
                'seed_keyword_analysis': seed_analysis,
                'related_keywords': related_keywords,
                'content_keyword_analysis': content_analysis,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Keyword research completed for: {seed_keywords}")
            return result
            
        except Exception as e:
            logger.error(f"Keyword research failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'seed_keywords': seed_keywords,
                'platform': platform
            }
    
    def _analyze_seed_keywords(self, seed_keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze seed keywords.
        """
        analysis = {}
        
        for keyword in seed_keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in self.keyword_database:
                db_data = self.keyword_database[keyword_lower]
                analysis[keyword] = {
                    'search_volume': db_data['search_volume'],
                    'competition': db_data['competition'],
                    'difficulty_score': self._calculate_keyword_difficulty(db_data),
                    'opportunity_score': self._calculate_keyword_opportunity(db_data),
                    'related_keywords': db_data['related']
                }
            else:
                # Generate simulated data for unknown keywords
                search_volume = random.randint(1000, 50000)
                competition = random.choice(['low', 'medium', 'high'])
                
                analysis[keyword] = {
                    'search_volume': search_volume,
                    'competition': competition,
                    'difficulty_score': self._calculate_keyword_difficulty({
                        'search_volume': search_volume,
                        'competition': competition
                    }),
                    'opportunity_score': self._calculate_keyword_opportunity({
                        'search_volume': search_volume,
                        'competition': competition
                    }),
                    'related_keywords': self._generate_related_keywords(keyword)
                }
        
        return analysis
    
    def _find_related_keywords(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Find related keywords.
        """
        related_keywords = []
        seen_keywords = set(seed_keywords)
        
        # Collect related keywords from seed keywords
        for keyword in seed_keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in self.keyword_database:
                for related_kw in self.keyword_database[keyword_lower]['related']:
                    if related_kw not in seen_keywords:
                        related_keywords.append({
                            'keyword': related_kw,
                            'source': keyword,
                            'search_volume': random.randint(1000, 20000),
                            'competition': random.choice(['low', 'medium']),
                            'relevance': random.uniform(0.7, 0.9)
                        })
                        seen_keywords.add(related_kw)
            
            # Add some additional related keywords
            additional_related = self._generate_related_keywords(keyword)
            for related_kw in additional_related:
                if related_kw not in seen_keywords:
                    related_keywords.append({
                        'keyword': related_kw,
                        'source': keyword,
                        'search_volume': random.randint(500, 10000),
                        'competition': random.choice(['low', 'medium']),
                        'relevance': random.uniform(0.6, 0.8)
                    })
                    seen_keywords.add(related_kw)
        
        # Sort by relevance and search volume
        related_keywords.sort(key=lambda x: (x['relevance'], x['search_volume']), reverse=True)
        
        return related_keywords[:20]  # Return top 20 related keywords
    
    def _analyze_content_keywords(self, content_url: str) -> Dict[str, Any]:
        """
        Analyze keywords in content.
        """
        try:
            # Fetch content
            response = requests.get(content_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Extract keywords from content
            words = word_tokenize(text.lower())
            filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
            
            word_counts = Counter(filtered_words)
            
            # Get top keywords
            top_keywords = [
                {'keyword': word, 'count': count, 'density': count / len(filtered_words)}
                for word, count in word_counts.most_common(10)
            ]
            
            return {
                'content_url': content_url,
                'word_count': len(filtered_words),
                'unique_words': len(word_counts),
                'top_keywords': top_keywords,
                'keyword_density': sum(kw['density'] for kw in top_keywords)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze content keywords: {str(e)}")
            return {
                'content_url': content_url,
                'error': str(e)
            }
    
    def _generate_keyword_recommendations(self, seed_analysis: Dict[str, Any], 
                                          related_keywords: List[Dict[str, Any]], 
                                          content_analysis: Dict[str, Any], 
                                          platform: str) -> List[Dict[str, Any]]:
        """
        Generate keyword recommendations.
        """
        recommendations = []
        
        # Analyze seed keywords
        for keyword, data in seed_analysis.items():
            if data['opportunity_score'] > 0.7:
                recommendations.append({
                    'type': 'seed_keyword',
                    'keyword': keyword,
                    'recommendation': 'high_priority',
                    'reason': f"High opportunity score ({data['opportunity_score']:.2f}) with good search volume",
                    'search_volume': data['search_volume'],
                    'competition': data['competition'],
                    'priority': 'high'
                })
            elif data['opportunity_score'] > 0.4:
                recommendations.append({
                    'type': 'seed_keyword',
                    'keyword': keyword,
                    'recommendation': 'medium_priority',
                    'reason': f"Moderate opportunity score ({data['opportunity_score']:.2f})",
                    'search_volume': data['search_volume'],
                    'competition': data['competition'],
                    'priority': 'medium'
                })
            else:
                recommendations.append({
                    'type': 'seed_keyword',
                    'keyword': keyword,
                    'recommendation': 'low_priority_or_replace',
                    'reason': f"Low opportunity score ({data['opportunity_score']:.2f})",
                    'search_volume': data['search_volume'],
                    'competition': data['competition'],
                    'priority': 'low'
                })
        
        # Analyze related keywords
        for kw_data in related_keywords[:5]:  # Top 5 related keywords
            if kw_data['opportunity_score'] > 0.6:
                recommendations.append({
                    'type': 'related_keyword',
                    'keyword': kw_data['keyword'],
                    'recommendation': 'consider_adding',
                    'reason': f"High relevance ({kw_data['relevance']:.2f}) and good opportunity score",
                    'search_volume': kw_data['search_volume'],
                    'competition': kw_data['competition'],
                    'priority': 'medium'
                })
        
        # Platform-specific recommendations
        if platform == 'youtube':
            recommendations.append({
                'type': 'platform_specific',
                'keyword': 'youtube',
                'recommendation': 'include_youtube_specific_keywords',
                'reason': 'YouTube content should include platform-specific keywords',
                'suggested_keywords': ['youtube video', 'youtube content', 'video tutorial'],
                'priority': 'high'
            })
        
        elif platform == 'website':
            recommendations.append({
                'type': 'platform_specific',
                'keyword': 'website',
                'recommendation': 'include_website_specific_keywords',
                'reason': 'Website content should include SEO-focused keywords',
                'suggested_keywords': ['guide', 'tutorial', 'how to', 'best practices'],
                'priority': 'high'
            })
        
        # Content gap analysis
        if content_analysis and 'top_keywords' in content_analysis:
            content_keywords = [kw['keyword'] for kw in content_analysis['top_keywords']]
            
            # Find missing high-opportunity keywords
            missing_keywords = []
            for keyword, data in seed_analysis.items():
                if data['opportunity_score'] > 0.6 and keyword not in content_keywords:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                recommendations.append({
                    'type': 'content_gap',
                    'keyword': 'content',
                    'recommendation': 'add_missing_keywords_to_content',
                    'reason': 'Content is missing high-opportunity keywords',
                    'missing_keywords': missing_keywords,
                    'priority': 'high'
                })
        
        return recommendations
    
    def _calculate_keyword_difficulty(self, keyword_data: Dict[str, Any]) -> float:
        """
        Calculate keyword difficulty score (0-1, where 1 is most difficult).
        """
        competition_weights = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9,
            'very high': 1.0
        }
        
        competition = keyword_data.get('competition', 'medium')
        competition_weight = competition_weights.get(competition, 0.6)
        
        # Normalize search volume (assuming max 200k for this scale)
        normalized_volume = min(1.0, keyword_data.get('search_volume', 0) / 200000)
        
        # Difficulty = competition weight * normalized volume
        difficulty = competition_weight * normalized_volume
        
        return round(difficulty, 3)
    
    def _calculate_keyword_opportunity(self, keyword_data: Dict[str, Any]) -> float:
        """
        Calculate keyword opportunity score (0-1, where 1 is best opportunity).
        """
        # Opportunity = (1 - difficulty) * normalized_volume
        difficulty = self._calculate_keyword_difficulty(keyword_data)
        normalized_volume = min(1.0, keyword_data.get('search_volume', 0) / 200000)
        
        opportunity = (1 - difficulty) * normalized_volume
        
        return round(opportunity, 3)
    
    def _generate_related_keywords(self, keyword: str) -> List[str]:
        """
        Generate related keywords.
        """
        # Simple related keyword generation
        base_words = keyword.split()
        
        if len(base_words) == 1:
            # Single word - add modifiers
            prefixes = ['best', 'top', 'how to', 'guide to', 'ultimate']
            suffixes = ['tips', 'tricks', 'guide', 'tutorial', 'review', 'comparison']
            
            related = []
            for prefix in prefixes:
                related.append(f"{prefix} {keyword}")
            
            for suffix in suffixes:
                related.append(f"{keyword} {suffix}")
            
            return related[:5]
        else:
            # Multiple words - vary word order and add modifiers
            variations = []
            
            # Add modifiers
            for prefix in ['best', 'top', 'how to']:
                variations.append(f"{prefix} {keyword}")
            
            # Reverse word order
            variations.append(' '.join(reversed(base_words)))
            
            # Remove duplicates and return
            return list(set(variations))[:5]

class AnalyticsTracker:
    """
    Analytics tracking tool for tracking content performance across platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the analytics tracker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.google_analytics_config = config.get('google_analytics', {})
        
        # Platform analytics configurations
        self.platform_analytics = {
            'google_analytics': {
                'enabled': self.google_analytics_config.get('enabled', False),
                'view_id': self.google_analytics_config.get('view_id'),
                'metrics': ['sessions', 'users', 'pageviews', 'bounceRate', 'avgSessionDuration']
            },
            'youtube': {
                'enabled': config.get('platform_apis', {}).get('youtube', {}).get('enabled', False),
                'metrics': ['views', 'likes', 'comments', 'subscribersGained', 'watchTime']
            },
            'twitter': {
                'enabled': config.get('platform_apis', {}).get('twitter', {}).get('enabled', False),
                'metrics': ['impressions', 'engagements', 'likes', 'retweets', 'replies']
            },
            'instagram': {
                'enabled': config.get('platform_apis', {}).get('instagram', {}).get('enabled', False),
                'metrics': ['impressions', 'reach', 'engagements', 'likes', 'comments']
            }
        }
    
    def track(self, content_id: str, platforms: List[str] = None, 
              metrics: List[str] = None) -> Dict[str, Any]:
        """
        Track content performance across platforms.
        
        Args:
            content_id: ID of content to track
            platforms: Optional list of platforms to track
            metrics: Optional list of specific metrics to track
            
        Returns:
            Dictionary containing analytics tracking results
        """
        try:
            logger.info(f"Tracking analytics for content: {content_id}")
            
            # Determine target platforms
            target_platforms = platforms or list(self.platform_analytics.keys())
            
            # Validate platforms
            valid_platforms = []
            for platform in target_platforms:
                if platform in self.platform_analytics and self.platform_analytics[platform]['enabled']:
                    valid_platforms.append(platform)
            
            if not valid_platforms:
                raise ValueError("No valid platforms configured for analytics tracking")
            
            # Track analytics for each platform
            tracking_results = []
            
            for platform in valid_platforms:
                try:
                    platform_result = self._track_platform_analytics(content_id, platform, metrics)
                    tracking_results.append(platform_result)
                    
                except Exception as e:
                    logger.error(f"Failed to track {platform} analytics: {str(e)}")
                    tracking_results.append({
                        'platform': platform,
                        'status': 'error',
                        'error': str(e),
                        'content_id': content_id
                    })
            
            result = {
                'status': 'success',
                'content_id': content_id,
                'platforms_tracked': len(valid_platforms),
                'platforms_successful': sum(1 for r in tracking_results if r['status'] == 'success'),
                'platforms_failed': sum(1 for r in tracking_results if r['status'] == 'error'),
                'tracking_results': tracking_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Analytics tracking completed for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Analytics tracking failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'content_id': content_id,
                'platforms': platforms or 'all'
            }
    
    def _track_platform_analytics(self, content_id: str, platform: str, 
                                  metrics: List[str] = None) -> Dict[str, Any]:
        """
        Track analytics for a specific platform.
        """
        try:
            logger.info(f"Tracking {platform} analytics for {content_id}")
            
            # Get platform-specific metrics
            platform_metrics = self.platform_analytics[platform]['metrics']
            target_metrics = metrics or platform_metrics
            
            # Validate metrics
            valid_metrics = [m for m in target_metrics if m in platform_metrics]
            
            if not valid_metrics:
                raise ValueError(f"No valid metrics specified for {platform}")
            
            # Simulate analytics data collection
            # In a real implementation, this would call the actual platform APIs
            
            if platform == 'google_analytics':
                analytics_data = self._simulate_google_analytics_data(content_id, valid_metrics)
            elif platform == 'youtube':
                analytics_data = self._simulate_youtube_analytics_data(content_id, valid_metrics)
            elif platform == 'twitter':
                analytics_data = self._simulate_twitter_analytics_data(content_id, valid_metrics)
            elif platform == 'instagram':
                analytics_data = self._simulate_instagram_analytics_data(content_id, valid_metrics)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return {
                'platform': platform,
                'status': 'success',
                'content_id': content_id,
                'metrics_tracked': valid_metrics,
                'analytics_data': analytics_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to track {platform} analytics: {str(e)}")
            return {
                'platform': platform,
                'status': 'error',
                'error': str(e),
                'content_id': content_id
            }
    
    def _simulate_google_analytics_data(self, content_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Simulate Google Analytics data.
        """
        # Generate simulated data
        data = {}
        
        for metric in metrics:
            if metric == 'sessions':
                data[metric] = random.randint(100, 10000)
            elif metric == 'users':
                data[metric] = random.randint(80, data.get('sessions', 1000) - 20)
            elif metric == 'pageviews':
                data[metric] = random.randint(150, 15000)
            elif metric == 'bounceRate':
                data[metric] = round(random.uniform(30, 80), 2)
            elif metric == 'avgSessionDuration':
                data[metric] = round(random.uniform(30, 300), 2)
            else:
                data[metric] = random.randint(1, 100)
        
        return {
            'content_id': content_id,
            'period': 'last_30_days',
            'data': data,
            'trends': self._generate_trends_data(metrics)
        }
    
    def _simulate_youtube_analytics_data(self, content_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Simulate YouTube analytics data.
        """
        # Generate simulated data
        data = {}
        
        for metric in metrics:
            if metric == 'views':
                data[metric] = random.randint(1000, 100000)
            elif metric == 'likes':
                data[metric] = random.randint(100, data.get('views', 10000) // 10)
            elif metric == 'comments':
                data[metric] = random.randint(10, data.get('views', 10000) // 100)
            elif metric == 'subscribersGained':
                data[metric] = random.randint(5, 500)
            elif metric == 'watchTime':
                data[metric] = random.randint(1000, 50000)  # seconds
            else:
                data[metric] = random.randint(1, 100)
        
        return {
            'content_id': content_id,
            'period': 'last_30_days',
            'data': data,
            'trends': self._generate_trends_data(metrics)
        }
    
    def _simulate_twitter_analytics_data(self, content_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Simulate Twitter analytics data.
        """
        # Generate simulated data
        data = {}
        
        for metric in metrics:
            if metric == 'impressions':
                data[metric] = random.randint(1000, 50000)
            elif metric == 'engagements':
                data[metric] = random.randint(100, data.get('impressions', 10000) // 5)
            elif metric == 'likes':
                data[metric] = random.randint(50, data.get('engagements', 1000) // 2)
            elif metric == 'retweets':
                data[metric] = random.randint(10, data.get('engagements', 1000) // 3)
            elif metric == 'replies':
                data[metric] = random.randint(5, data.get('engagements', 1000) // 4)
            else:
                data[metric] = random.randint(1, 100)
        
        return {
            'content_id': content_id,
            'period': 'last_30_days',
            'data': data,
            'trends': self._generate_trends_data(metrics)
        }
    
    def _simulate_instagram_analytics_data(self, content_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Simulate Instagram analytics data.
        """
        # Generate simulated data
        data = {}
        
        for metric in metrics:
            if metric == 'impressions':
                data[metric] = random.randint(5000, 100000)
            elif metric == 'reach':
                data[metric] = random.randint(3000, data.get('impressions', 50000) - 1000)
            elif metric == 'engagements':
                data[metric] = random.randint(500, data.get('impressions', 50000) // 10)
            elif metric == 'likes':
                data[metric] = random.randint(300, data.get('engagements', 5000) // 1.5)
            elif metric == 'comments':
                data[metric] = random.randint(50, data.get('engagements', 5000) // 5)
            else:
                data[metric] = random.randint(1, 100)
        
        return {
            'content_id': content_id,
            'period': 'last_30_days',
            'data': data,
            'trends': self._generate_trends_data(metrics)
        }
    
    def _generate_trends_data(self, metrics: List[str]) -> Dict[str, Any]:
        """
        Generate trends data for metrics.
        """
        trends = {}
        
        for metric in metrics:
            # Generate 7 days of trend data
            trends[metric] = {
                'last_7_days': [random.randint(50, 150) for _ in range(7)],
                'trend': random.choice(['up', 'down', 'stable']),
                'change_percentage': round(random.uniform(-20, 30), 2)
            }
        
        return trends

class ContentScheduler:
    """
    Content scheduling tool for determining optimal scheduling times.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content scheduler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Default scheduling data
        self.scheduling_data = config.get('platform_scheduling_data', {})
        
        # Timezone
        self.timezone = config.get('timezone', 'UTC')
    
    def schedule_content(self, content_id: str, platforms: List[str], 
                         content_type: str = 'video') -> Dict[str, Any]:
        """
        Determine optimal scheduling times for content.
        
        Args:
            content_id: ID of content to schedule
            platforms: List of target platforms
            content_type: Type of content
            
        Returns:
            Dictionary containing scheduling recommendations
        """
        try:
            logger.info(f"Scheduling content {content_id} for platforms: {platforms}")
            
            # Get scheduling recommendations for each platform
            platform_recommendations = []
            
            for platform in platforms:
                if platform in self.scheduling_data and content_type in self.scheduling_data[platform]:
                    recommendations = self.scheduling_data[platform][content_type]
                    
                    # Sort by score (descending)
                    recommendations.sort(key=lambda x: x['score'], reverse=True)
                    
                    platform_recommendations.append({
                        'platform': platform,
                        'content_type': content_type,
                        'recommendations': recommendations[:3],  # Top 3 recommendations
                        'best_time': recommendations[0] if recommendations else None
                    })
                else:
                    platform_recommendations.append({
                        'platform': platform,
                        'content_type': content_type,
                        'recommendations': [],
                        'best_time': None,
                        'error': 'No scheduling data available'
                    })
            
            # Generate cross-platform recommendations
            cross_platform = self._generate_cross_platform_recommendations(platform_recommendations)
            
            result = {
                'status': 'success',
                'content_id': content_id,
                'content_type': content_type,
                'platforms': platforms,
                'platform_recommendations': platform_recommendations,
                'cross_platform_recommendations': cross_platform,
                'timezone': self.timezone,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Content scheduling completed for {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'content_id': content_id,
                'platforms': platforms,
                'content_type': content_type
            }
    
    def _generate_cross_platform_recommendations(self, 
                                                 platform_recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate cross-platform scheduling recommendations.
        """
        # Find overlapping time slots across platforms
        all_times = []
        
        for platform_rec in platform_recommendations:
            if platform_rec['recommendations']:
                for rec in platform_rec['recommendations']:
                    all_times.append({
                        'platform': platform_rec['platform'],
                        'day': rec['day'],
                        'time': rec['time'],
                        'score': rec['score']
                    })
        
        if not all_times:
            return {
                'best_overall_time': None,
                'platform_coverage': 0,
                'recommendations': []
            }
        
        # Group by day and time
        time_groups = {}
        for time_data in all_times:
            key = f"{time_data['day']}_{time_data['time']}"
            if key not in time_groups:
                time_groups[key] = {
                    'day': time_data['day'],
                    'time': time_data['time'],
                    'platforms': [],
                    'total_score': 0
                }
            time_groups[key]['platforms'].append(time_data['platform'])
            time_groups[key]['total_score'] += time_data['score']
        
        # Find best overlapping times
        best_times = sorted(time_groups.values(), key=lambda x: (len(x['platforms']), x['total_score']), reverse=True)
        
        return {
            'best_overall_time': best_times[0] if best_times else None,
            'platform_coverage': len(best_times[0]['platforms']) if best_times else 0,
            'recommendations': best_times[:3],  # Top 3 overlapping times
            'analysis': {
                'total_platforms': len(platform_recommendations),
                'covered_platforms': len(best_times[0]['platforms']) if best_times else 0,
                'coverage_percentage': len(best_times[0]['platforms']) / len(platform_recommendations) if best_times and platform_recommendations else 0
            }
        }

# Utility functions

def get_stop_words() -> set:
    """
    Get English stop words.
    """
    try:
        return set(stopwords.words('english'))
    except:
        # Fallback if NLTK data not available
        return {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
            'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }

# Initialize stop words for modules that need it
stop_words = get_stop_words()