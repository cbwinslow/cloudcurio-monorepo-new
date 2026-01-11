#!/usr/bin/env python3
"""
Content Analyst Agent - Analyzes podcast content for engagement potential and optimization opportunities.

This agent provides advanced content analysis capabilities including:
- Engagement prediction
- Topic extraction and categorization
- Sentiment analysis
- Content optimization recommendations
- Platform-specific performance forecasting
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from collections import Counter

from agents.base_agent import BaseAgent, AgentTool
from agents.robust_tool import RobustTool, ToolResult


class ContentAnalystAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        super().__init__(name, description)
        self.implementation = implementation

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        return self.implementation


class ContentAnalystAgent(BaseAgent):
    """Agent for advanced podcast content analysis and optimization."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the content analyst agent."""
        super().__init__("content_analyst", config_path)

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize content analysis tools."""
        return {
            'analyze_transcript': ContentAnalystAgentTool(
                "analyze_transcript",
                "Analyze podcast transcript for engagement potential and topics",
                TranscriptAnalysisTool()
            ),
            'predict_engagement': ContentAnalystAgentTool(
                "predict_engagement",
                "Predict content performance across different platforms",
                EngagementPredictionTool()
            ),
            'extract_topics': ContentAnalystAgentTool(
                "extract_topics",
                "Extract key topics, themes, and entities from content",
                TopicExtractionTool()
            ),
            'sentiment_analysis': ContentAnalystAgentTool(
                "sentiment_analysis",
                "Analyze sentiment and emotional tone of content",
                SentimentAnalysisTool()
            ),
            'optimize_content': ContentAnalystAgentTool(
                "optimize_content",
                "Generate optimization recommendations for better engagement",
                ContentOptimizationTool()
            ),
            'generate_metadata': ContentAnalystAgentTool(
                "generate_metadata",
                "Create SEO-optimized metadata and descriptions",
                MetadataGenerationTool()
            )
        }


class TranscriptAnalysisTool(RobustTool):
    """Tool for comprehensive transcript analysis."""

    def __init__(self):
        super().__init__(
            name="analyze_transcript",
            description="Analyze podcast transcript for engagement potential and topics"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for transcript analysis."""
        return {
            'type': 'object',
            'required': ['transcript_text'],
            'properties': {
                'transcript_text': {
                    'type': 'string',
                    'description': 'Full transcript text to analyze'
                },
                'episode_title': {
                    'type': 'string',
                    'description': 'Episode title for context'
                },
                'guest_names': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Names of guests/participants'
                },
                'episode_duration': {
                    'type': 'number',
                    'description': 'Duration in minutes'
                },
                'analysis_focus': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'enum': ['engagement', 'topics', 'sentiment', 'timing', 'quality']
                    },
                    'default': ['engagement', 'topics', 'sentiment'],
                    'description': 'Areas to focus analysis on'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'basic_analysis',
                'condition': lambda e, p, eid: 'text' in str(e).lower() or 'processing' in str(e).lower(),
                'action': self._fallback_basic_analysis,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Analyze transcript using NLP techniques."""
        import nltk
        from collections import Counter

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        transcript = parameters['transcript_text']
        episode_title = parameters.get('episode_title', 'Untitled Episode')
        guest_names = parameters.get('guest_names', [])
        episode_duration = parameters.get('episode_duration', 60)
        focus_areas = parameters.get('analysis_focus', ['engagement', 'topics', 'sentiment'])

        # Basic text statistics
        word_count = len(transcript.split())
        words_per_minute = word_count / episode_duration if episode_duration > 0 else 0
        sentence_count = len(nltk.sent_tokenize(transcript))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Extract key metrics
        analysis_results = {
            'episode_title': episode_title,
            'word_count': word_count,
            'words_per_minute': round(words_per_minute, 1),
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'guest_names': guest_names,
            'episode_duration': episode_duration,
            'focus_areas': focus_areas,
            'metrics': {}
        }

        # Engagement analysis
        if 'engagement' in focus_areas:
            analysis_results['metrics']['engagement'] = self._analyze_engagement(transcript)

        # Topic analysis
        if 'topics' in focus_areas:
            analysis_results['metrics']['topics'] = self._extract_topics_basic(transcript)

        # Sentiment analysis
        if 'sentiment' in focus_areas:
            analysis_results['metrics']['sentiment'] = self._analyze_sentiment_basic(transcript)

        # Quality metrics
        if 'quality' in focus_areas:
            analysis_results['metrics']['quality'] = self._assess_quality(transcript, word_count, words_per_minute)

        return analysis_results

    def _analyze_engagement(self, text: str) -> Dict[str, Any]:
        """Analyze engagement potential of transcript."""
        # Count engagement indicators
        laughter_count = len(re.findall(r'(?i)\b(laugh|chuckle|giggle|ha\s*ha)\b', text))
        question_count = len(re.findall(r'\?', text))
        exclamation_count = len(re.findall(r'!', text))

        # Calculate engagement score (simple heuristic)
        engagement_score = min(100, (laughter_count * 2 + question_count + exclamation_count) / max(1, len(text) / 1000) * 10)

        return {
            'laughter_moments': laughter_count,
            'questions_asked': question_count,
            'exclamations': exclamation_count,
            'engagement_score': round(engagement_score, 1),
            'engagement_level': self._get_engagement_level(engagement_score)
        }

    def _extract_topics_basic(self, text: str) -> Dict[str, Any]:
        """Extract basic topics from text."""
        # Simple keyword-based topic extraction
        topics = []
        topic_keywords = {
            'technology': ['tech', 'software', 'hardware', 'ai', 'machine learning', 'programming'],
            'business': ['business', 'startup', 'entrepreneur', 'company', 'market', 'invest'],
            'entertainment': ['movie', 'tv', 'show', 'actor', 'celebrity', 'hollywood'],
            'sports': ['sport', 'game', 'team', 'player', 'league', 'championship'],
            'politics': ['politic', 'government', 'election', 'policy', 'law', 'congress']
        }

        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return {
            'detected_topics': topics,
            'topic_count': len(topics),
            'primary_topic': topics[0] if topics else 'general'
        }

    def _analyze_sentiment_basic(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis."""
        positive_words = ['great', 'excellent', 'awesome', 'fantastic', 'wonderful', 'amazing']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'disappoint']

        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)

        sentiment_score = (positive_count - negative_count) / max(1, (positive_count + negative_count))

        return {
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'sentiment_score': round(sentiment_score, 2),
            'sentiment': self._get_sentiment_label(sentiment_score)
        }

    def _assess_quality(self, text: str, word_count: int, wpm: float) -> Dict[str, Any]:
        """Assess content quality metrics."""
        # Simple quality heuristics
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'basically']
        filler_count = sum(text.lower().count(word) for word in filler_words)

        # Quality indicators
        quality_score = 100

        # Adjust for pacing
        if wpm < 100:
            quality_score -= 10  # Too slow
        elif wpm > 180:
            quality_score -= 15  # Too fast

        # Adjust for filler words
        if filler_count > word_count * 0.02:  # More than 2% filler words
            quality_score -= min(20, (filler_count / word_count) * 500)

        # Adjust for length
        if word_count < 2000:
            quality_score -= 5  # Short episode
        elif word_count > 10000:
            quality_score += 5  # Long, detailed episode

        return {
            'filler_word_count': filler_count,
            'filler_word_percentage': round(filler_count / word_count * 100, 2),
            'pacing_score': max(0, 100 - abs(wpm - 140)),
            'content_length_score': min(100, max(80, word_count / 100)),
            'overall_quality_score': round(quality_score, 1),
            'quality_level': self._get_quality_level(quality_score)
        }

    def _get_engagement_level(self, score: float) -> str:
        """Get engagement level based on score."""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'

    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label based on score."""
        if score > 0.3:
            return 'Positive'
        elif score > -0.3:
            return 'Neutral'
        else:
            return 'Negative'

    def _get_quality_level(self, score: float) -> str:
        """Get quality level based on score."""
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 60:
            return 'Poor'
        else:
            return 'Very Poor'

    def _fallback_basic_analysis(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to basic text analysis."""
        transcript = parameters['transcript_text']

        basic_analysis = {
            'word_count': len(transcript.split()),
            'character_count': len(transcript),
            'line_count': len(transcript.split('\n')),
            'basic_metrics': {
                'has_laughter': 'laugh' in transcript.lower(),
                'has_questions': '?' in transcript,
                'has_exclamations': '!' in transcript
            }
        }

        return ToolResult(
            success=True,
            data=basic_analysis,
            execution_id=execution_id,
            warnings=['Used basic text analysis due to processing limitations']
        )


class EngagementPredictionTool(RobustTool):
    """Tool for predicting content engagement across platforms."""

    def __init__(self):
        super().__init__(
            name="predict_engagement",
            description="Predict content performance across different platforms"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for engagement prediction."""
        return {
            'type': 'object',
            'required': ['content_type', 'platforms'],
            'properties': {
                'content_type': {
                    'type': 'string',
                    'enum': ['full_episode', 'short_clip', 'behind_scenes', 'interview', 'panel'],
                    'description': 'Type of content to predict'
                },
                'platforms': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'enum': ['youtube', 'tiktok', 'instagram', 'twitter', 'linkedin', 'spotify', 'apple_podcasts']
                    },
                    'description': 'Platforms to predict performance for'
                },
                'duration': {
                    'type': 'number',
                    'description': 'Content duration in seconds'
                },
                'topics': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Key topics covered'
                },
                'guest_popularity': {
                    'type': 'string',
                    'enum': ['high', 'medium', 'low', 'none'],
                    'default': 'medium',
                    'description': 'Popularity level of guests'
                },
                'posting_time': {
                    'type': 'string',
                    'description': 'Planned posting time (HH:MM format)'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'default_prediction',
                'condition': lambda e, p, eid: True,  # Always available as fallback
                'action': self._fallback_default_prediction,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Predict engagement based on content characteristics."""
        content_type = parameters['content_type']
        platforms = parameters['platforms']
        duration = parameters.get('duration', 0)
        topics = parameters.get('topics', [])
        guest_popularity = parameters.get('guest_popularity', 'medium')
        posting_time = parameters.get('posting_time', '12:00')

        predictions = {}

        for platform in platforms:
            predictions[platform] = self._predict_for_platform(
                platform, content_type, duration, topics,
                guest_popularity, posting_time
            )

        return {
            'content_type': content_type,
            'platforms_analyzed': platforms,
            'predictions': predictions,
            'overall_potential': self._calculate_overall_potential(predictions)
        }

    def _predict_for_platform(self, platform: str, content_type: str, duration: int,
                             topics: List[str], guest_popularity: str, posting_time: str) -> Dict[str, Any]:
        """Generate platform-specific predictions."""
        # Base engagement rates by platform and content type
        base_rates = {
            'youtube': {
                'full_episode': {'views': 5000, 'likes': 350, 'comments': 45, 'shares': 80},
                'short_clip': {'views': 12000, 'likes': 800, 'comments': 120, 'shares': 250}
            },
            'tiktok': {
                'full_episode': {'views': 8000, 'likes': 600, 'comments': 80, 'shares': 150},
                'short_clip': {'views': 25000, 'likes': 1800, 'comments': 200, 'shares': 400}
            },
            'instagram': {
                'full_episode': {'views': 6000, 'likes': 450, 'comments': 60, 'shares': 120},
                'short_clip': {'views': 18000, 'likes': 1200, 'comments': 150, 'shares': 300}
            }
        }

        # Get base rates or defaults
        base_metrics = base_rates.get(platform, {}).get(content_type,
            {'views': 1000, 'likes': 70, 'comments': 10, 'shares': 20})

        # Apply modifiers based on content characteristics
        metrics = base_metrics.copy()

        # Duration modifier
        if platform in ['tiktok', 'instagram'] and duration > 60:
            metrics = {k: v * 0.7 for k, v in metrics.items()}  # Longer content performs worse on short-form platforms
        elif platform == 'youtube' and duration > 1800:
            metrics = {k: v * 1.3 for k, v in metrics.items()}  # Longer content can perform better on YouTube

        # Topic modifier
        topic_multiplier = 1.0
        if any(topic in ['technology', 'business', 'finance'] for topic in topics):
            if platform in ['linkedin', 'twitter']:
                topic_multiplier = 1.2
        elif any(topic in ['entertainment', 'celebrity', 'movies'] for topic in topics):
            if platform in ['tiktok', 'instagram']:
                topic_multiplier = 1.3

        # Guest popularity modifier
        guest_multiplier = {'high': 1.5, 'medium': 1.0, 'low': 0.8, 'none': 0.7}.get(guest_popularity, 1.0)

        # Time of day modifier
        time_multiplier = self._get_time_multiplier(platform, posting_time)

        # Apply all multipliers
        final_multiplier = topic_multiplier * guest_multiplier * time_multiplier
        for key in metrics:
            metrics[key] = int(metrics[key] * final_multiplier)

        # Calculate engagement rate
        engagement_rate = (metrics['likes'] + metrics['comments'] + metrics['shares']) / max(1, metrics['views']) * 100

        return {
            'estimated_views': metrics['views'],
            'estimated_likes': metrics['likes'],
            'estimated_comments': metrics['comments'],
            'estimated_shares': metrics['shares'],
            'estimated_engagement_rate': round(engagement_rate, 2),
            'potential_reach': int(metrics['views'] * 1.5),  # Estimated additional reach
            'performance_level': self._get_performance_level(engagement_rate)
        }

    def _get_time_multiplier(self, platform: str, time_str: str) -> float:
        """Get time-based performance multiplier."""
        try:
            hour = int(time_str.split(':')[0])

            # Platform-specific optimal times
            if platform == 'tiktok':
                if 6 <= hour < 9 or 19 <= hour < 23:  # 6-9 AM, 7-11 PM
                    return 1.2
            elif platform == 'instagram':
                if 11 <= hour < 14 or 19 <= hour < 21:  # 11 AM-2 PM, 7-9 PM
                    return 1.2
            elif platform == 'youtube':
                if 14 <= hour < 16:  # 2-4 PM
                    return 1.15
            elif platform == 'twitter':
                if 9 <= hour < 11 or 19 <= hour < 21:  # 9-11 AM, 7-9 PM
                    return 1.15
        except:
            pass

        return 1.0

    def _get_performance_level(self, engagement_rate: float) -> str:
        """Get performance level based on engagement rate."""
        if engagement_rate >= 12:
            return 'Excellent'
        elif engagement_rate >= 8:
            return 'Good'
        elif engagement_rate >= 5:
            return 'Fair'
        elif engagement_rate >= 3:
            return 'Poor'
        else:
            return 'Very Poor'

    def _calculate_overall_potential(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall potential across all platforms."""
        total_views = sum(p['estimated_views'] for p in predictions.values())
        total_engagement = sum(p['estimated_likes'] + p['estimated_comments'] + p['estimated_shares']
                              for p in predictions.values())

        avg_engagement_rate = total_engagement / max(1, total_views) * 100

        return {
            'total_estimated_views': total_views,
            'total_estimated_engagement': total_engagement,
            'average_engagement_rate': round(avg_engagement_rate, 2),
            'platform_count': len(predictions),
            'overall_potential': self._get_overall_potential_level(avg_engagement_rate)
        }

    def _get_overall_potential_level(self, engagement_rate: float) -> str:
        """Get overall potential level."""
        if engagement_rate >= 10:
            return 'High Potential'
        elif engagement_rate >= 7:
            return 'Good Potential'
        elif engagement_rate >= 5:
            return 'Moderate Potential'
        elif engagement_rate >= 3:
            return 'Limited Potential'
        else:
            return 'Low Potential'

    def _fallback_default_prediction(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to basic engagement prediction."""
        content_type = parameters['content_type']
        platforms = parameters['platforms']

        # Basic fallback predictions
        base_predictions = {
            'full_episode': {'views': 3000, 'likes': 200, 'comments': 30, 'shares': 50},
            'short_clip': {'views': 8000, 'likes': 500, 'comments': 80, 'shares': 150}
        }

        predictions = {}
        for platform in platforms:
            metrics = base_predictions.get(content_type,
                {'views': 2000, 'likes': 150, 'comments': 20, 'shares': 40})

            engagement_rate = (metrics['likes'] + metrics['comments'] + metrics['shares']) / max(1, metrics['views']) * 100

            predictions[platform] = {
                'estimated_views': metrics['views'],
                'estimated_likes': metrics['likes'],
                'estimated_comments': metrics['comments'],
                'estimated_shares': metrics['shares'],
                'estimated_engagement_rate': round(engagement_rate, 2),
                'potential_reach': int(metrics['views'] * 1.5),
                'performance_level': self._get_performance_level(engagement_rate)
            }

        return ToolResult(
            success=True,
            data={
                'content_type': content_type,
                'platforms_analyzed': platforms,
                'predictions': predictions,
                'overall_potential': self._calculate_overall_potential(predictions),
                'warnings': ['Used basic prediction model due to processing limitations']
            },
            execution_id=execution_id
        )


class TopicExtractionTool(RobustTool):
    """Tool for advanced topic extraction and categorization."""

    def __init__(self):
        super().__init__(
            name="extract_topics",
            description="Extract key topics, themes, and entities from content"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for topic extraction."""
        return {
            'type': 'object',
            'required': ['text'],
            'properties': {
                'text': {
                    'type': 'string',
                    'description': 'Text content to analyze for topics'
                },
                'content_type': {
                    'type': 'string',
                    'enum': ['transcript', 'description', 'social_post', 'article'],
                    'default': 'transcript',
                    'description': 'Type of content being analyzed'
                },
                'min_topic_length': {
                    'type': 'integer',
                    'default': 2,
                    'minimum': 1,
                    'description': 'Minimum number of words per topic'
                },
                'max_topics': {
                    'type': 'integer',
                    'default': 10,
                    'minimum': 1,
                    'maximum': 20,
                    'description': 'Maximum number of topics to extract'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'basic_topic_extraction',
                'condition': lambda e, p, eid: True,
                'action': self._fallback_basic_topics,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Extract topics using NLP techniques."""
        text = parameters['text']
        content_type = parameters.get('content_type', 'transcript')
        min_length = parameters.get('min_topic_length', 2)
        max_topics = parameters.get('max_topics', 10)

        # Simple topic extraction approach
        topics = self._extract_topics_simple(text, min_length, max_topics)

        # Categorize topics
        categorized = self._categorize_topics(topics)

        return {
            'text_length': len(text),
            'content_type': content_type,
            'extracted_topics': topics,
            'topic_count': len(topics),
            'categorized_topics': categorized,
            'primary_topic': topics[0] if topics else None,
            'topic_density': len(topics) / max(1, len(text.split()) / 100)  # Topics per 100 words
        }

    def _extract_topics_simple(self, text: str, min_length: int, max_topics: int) -> List[str]:
        """Simple topic extraction using keyword frequency."""
        # Remove common words and extract meaningful phrases
        stop_words = {'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were'}

        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]

        # Simple n-gram extraction
        phrases = []
        for i in range(len(filtered_words) - min_length + 1):
            phrase = ' '.join(filtered_words[i:i+min_length])
            if len(phrase.split()) >= min_length:
                phrases.append(phrase)

        # Get most frequent phrases
        phrase_counts = Counter(phrases)
        topics = [phrase for phrase, count in phrase_counts.most_common(max_topics)]

        return topics

    def _categorize_topics(self, topics: List[str]) -> Dict[str, List[str]]:
        """Categorize topics into broad categories."""
        categories: Dict[str, List[str]] = {
            'technology': [],
            'business': [],
            'entertainment': [],
            'sports': [],
            'politics': [],
            'health': [],
            'science': [],
            'education': [],
            'lifestyle': [],
            'other': []
        }

        tech_keywords = {'tech', 'software', 'hardware', 'ai', 'machine', 'learning', 'program', 'code', 'computer'}
        business_keywords = {'business', 'company', 'startup', 'market', 'invest', 'money', 'finance', 'economy'}
        entertainment_keywords = {'movie', 'film', 'tv', 'show', 'actor', 'celebrity', 'music', 'hollywood'}

        for topic in topics:
            topic_words = set(topic.split())

            if topic_words & tech_keywords:
                categories['technology'].append(topic)
            elif topic_words & business_keywords:
                categories['business'].append(topic)
            elif topic_words & entertainment_keywords:
                categories['entertainment'].append(topic)
            else:
                categories['other'].append(topic)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _fallback_basic_topics(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to basic topic extraction."""
        text = parameters['text']
        content_type = parameters.get('content_type', 'transcript')
        max_topics = parameters.get('max_topics', 5)

        # Very basic topic extraction - just get most frequent words
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        stop_words = {'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were'}
        filtered_words = [word for word in words if word not in stop_words]

        word_counts = Counter(filtered_words)
        topics = [word for word, count in word_counts.most_common(max_topics)]

        return ToolResult(
            success=True,
            data={
                'text_length': len(text),
                'content_type': content_type,
                'extracted_topics': topics,
                'topic_count': len(topics),
                'primary_topic': topics[0] if topics else None,
                'warnings': ['Used basic topic extraction due to processing limitations']
            },
            execution_id=execution_id
        )


class SentimentAnalysisTool(RobustTool):
    """Tool for detailed sentiment and emotional analysis."""

    def __init__(self):
        super().__init__(
            name="sentiment_analysis",
            description="Analyze sentiment and emotional tone of content"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for sentiment analysis."""
        return {
            'type': 'object',
            'required': ['text'],
            'properties': {
                'text': {
                    'type': 'string',
                    'description': 'Text content to analyze for sentiment'
                },
                'analysis_level': {
                    'type': 'string',
                    'enum': ['overall', 'segmented', 'detailed'],
                    'default': 'overall',
                    'description': 'Level of sentiment analysis detail'
                },
                'segment_length': {
                    'type': 'integer',
                    'default': 500,
                    'minimum': 100,
                    'description': 'Length of segments for segmented analysis (characters)'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'basic_sentiment',
                'condition': lambda e, p, eid: True,
                'action': self._fallback_basic_sentiment,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Analyze sentiment using NLP techniques."""
        text = parameters['text']
        analysis_level = parameters.get('analysis_level', 'overall')
        segment_length = parameters.get('segment_length', 500)

        if analysis_level == 'segmented':
            return self._analyze_segmented(text, segment_length)
        else:
            return self._analyze_overall(text)

    def _analyze_overall(self, text: str) -> Dict[str, Any]:
        """Perform overall sentiment analysis."""
        # Simple sentiment analysis
        positive_words = {'great', 'excellent', 'awesome', 'fantastic', 'wonderful', 'amazing', 'love', 'best'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'poor'}

        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)

        total_sentiment_words = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / max(1, total_sentiment_words) if total_sentiment_words > 0 else 0

        # Emotion detection
        emotions = self._detect_emotions(text)

        return {
            'sentiment_score': round(sentiment_score, 3),
            'sentiment': self._get_sentiment_label(sentiment_score),
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'emotion_analysis': emotions,
            'overall_tone': self._get_overall_tone(sentiment_score, emotions)
        }

    def _analyze_segmented(self, text: str, segment_length: int) -> Dict[str, Any]:
        """Perform segmented sentiment analysis."""
        segments = []
        start = 0

        while start < len(text):
            end = min(start + segment_length, len(text))
            segment = text[start:end]

            # Analyze each segment
            segment_analysis = self._analyze_overall(segment)
            segment_analysis['segment_start'] = start
            segment_analysis['segment_end'] = end
            segment_analysis['segment_text'] = segment[:100] + '...' if len(segment) > 100 else segment

            segments.append(segment_analysis)
            start = end

        # Calculate overall from segments
        total_positive = sum(s['positive_indicators'] for s in segments)
        total_negative = sum(s['negative_indicators'] for s in segments)
        overall_score = (total_positive - total_negative) / max(1, total_positive + total_negative)

        return {
            'segment_count': len(segments),
            'segments': segments,
            'overall_sentiment_score': round(overall_score, 3),
            'overall_sentiment': self._get_sentiment_label(overall_score),
            'sentiment_trend': self._analyze_trend(segments)
        }

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect basic emotions in text."""
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'laugh'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'irritated'],
            'sadness': ['sad', 'unhappy', 'depressed', 'gloomy', 'melancholy'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished'],
            'fear': ['afraid', 'scared', 'fearful', 'anxious', 'nervous']
        }

        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in emotion_keywords.items():
            count = sum(text_lower.count(word) for word in keywords)
            emotion_scores[emotion] = round(count / max(1, len(text.split()) / 100), 2)  # Per 100 words

        return emotion_scores

    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label."""
        if score > 0.2:
            return 'Positive'
        elif score > -0.2:
            return 'Neutral'
        elif score > -0.5:
            return 'Slightly Negative'
        else:
            return 'Negative'

    def _get_overall_tone(self, sentiment_score: float, emotions: Dict[str, float]) -> str:
        """Determine overall tone."""
        if sentiment_score > 0.3:
            return 'Enthusiastic'
        elif sentiment_score > 0.1:
            return 'Positive'
        elif sentiment_score > -0.1:
            return 'Neutral'
        elif sentiment_score > -0.3:
            return 'Critical'
        else:
            return 'Negative'

        # Adjust based on emotions
        if emotions.get('joy', 0) > 2.0:
            return 'Excited'
        elif emotions.get('anger', 0) > 1.5:
            return 'Confrontational'

    def _analyze_trend(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trend across segments."""
        scores = [s['sentiment_score'] for s in segments]

        if len(scores) < 2:
            return {'trend': 'stable', 'change': 0}

        start_avg = sum(scores[:len(scores)//2]) / max(1, len(scores)//2)
        end_avg = sum(scores[len(scores)//2:]) / max(1, len(scores) - len(scores)//2)
        change = end_avg - start_avg

        if change > 0.1:
            trend = 'improving'
        elif change < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'start_sentiment': round(start_avg, 3),
            'end_sentiment': round(end_avg, 3),
            'change': round(change, 3),
            'percentage_change': round(change / start_avg * 100, 1) if start_avg != 0 else 0
        }


class ContentOptimizationTool(RobustTool):
    """Tool for generating content optimization recommendations."""

    def __init__(self):
        super().__init__(
            name="optimize_content",
            description="Generate optimization recommendations for better engagement"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for content optimization."""
        return {
            'type': 'object',
            'required': ['content_analysis'],
            'properties': {
                'content_analysis': {
                    'type': 'object',
                    'description': 'Analysis results from content analyst tools'
                },
                'target_platform': {
                    'type': 'string',
                    'enum': ['youtube', 'tiktok', 'instagram', 'twitter', 'linkedin', 'podcast'],
                    'description': 'Primary target platform'
                },
                'content_type': {
                    'type': 'string',
                    'enum': ['full_episode', 'short_clip', 'behind_scenes', 'promo'],
                    'description': 'Type of content being optimized'
                },
                'optimization_goals': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'enum': ['engagement', 'reach', 'conversion', 'retention', 'discovery']
                    },
                    'default': ['engagement', 'reach'],
                    'description': 'Primary optimization goals'
                }
            }
        }

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Generate optimization recommendations."""
        analysis = parameters['content_analysis']
        target_platform = parameters.get('target_platform', 'youtube')
        content_type = parameters.get('content_type', 'full_episode')
        goals = parameters.get('optimization_goals', ['engagement', 'reach'])

        recommendations = []

        # Analyze current metrics
        current_metrics = analysis.get('metrics', {})
        engagement_metrics = current_metrics.get('engagement', {})
        quality_metrics = current_metrics.get('quality', {})
        sentiment_metrics = current_metrics.get('sentiment', {})

        # Generate platform-specific recommendations
        if target_platform in ['tiktok', 'instagram'] and content_type == 'short_clip':
            recommendations.extend(self._optimize_short_form(engagement_metrics, quality_metrics))
        elif target_platform == 'youtube' and content_type == 'full_episode':
            recommendations.extend(self._optimize_youtube_episode(engagement_metrics, quality_metrics, sentiment_metrics))
        elif target_platform in ['twitter', 'linkedin']:
            recommendations.extend(self._optimize_social_text(analysis, goals))

        # Add general recommendations
        recommendations.extend(self._general_optimizations(analysis, goals))

        # Prioritize recommendations
        prioritized = self._prioritize_recommendations(recommendations, goals)

        return {
            'content_type': content_type,
            'target_platform': target_platform,
            'optimization_goals': goals,
            'recommendations': prioritized,
            'implementation_priority': self._get_implementation_plan(prioritized),
            'estimated_impact': self._estimate_impact(prioritized, analysis)
        }

    def _optimize_short_form(self, engagement: Dict[str, Any], quality: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate short-form content optimization recommendations."""
        recommendations = []

        # Engagement recommendations
        if engagement.get('engagement_score', 0) < 60:
            recommendations.append({
                'type': 'engagement',
                'recommendation': 'Increase laughter moments and energetic delivery',
                'current_score': engagement.get('engagement_score', 0),
                'target_score': min(80, engagement.get('engagement_score', 0) + 20),
                'impact': 'high',
                'effort': 'medium'
            })

        # Pacing recommendations
        if quality.get('pacing_score', 100) < 80:
            recommendations.append({
                'type': 'pacing',
                'recommendation': 'Increase speech rate to 140-160 words per minute for short-form content',
                'current_pacing': quality.get('pacing_score', 0),
                'target_pacing': 140,
                'impact': 'medium',
                'effort': 'low'
            })

        # Hook recommendations
        recommendations.append({
            'type': 'structure',
            'recommendation': 'Create attention-grabbing hook in first 3 seconds',
            'impact': 'very_high',
            'effort': 'medium',
            'details': 'Use surprising statement, question, or visual impact'
        })

        # Caption recommendations
        recommendations.append({
            'type': 'accessibility',
            'recommendation': 'Add bold, readable captions covering 60% of screen height',
            'impact': 'high',
            'effort': 'low'
        })

        return recommendations

    def _optimize_youtube_episode(self, engagement: Dict[str, Any], quality: Dict[str, Any],
                                  sentiment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate YouTube episode optimization recommendations."""
        recommendations = []

        # Engagement recommendations
        if engagement.get('laughter_moments', 0) < 5:
            recommendations.append({
                'type': 'content',
                'recommendation': 'Increase humorous moments and audience interaction',
                'current': engagement.get('laughter_moments', 0),
                'target': 8,
                'impact': 'high',
                'effort': 'medium'
            })

        # Quality recommendations
        if quality.get('filler_word_percentage', 0) > 2.0:
            recommendations.append({
                'type': 'delivery',
                'recommendation': 'Reduce filler words through editing or re-recording',
                'current': quality.get('filler_word_percentage', 0),
                'target': 1.0,
                'impact': 'medium',
                'effort': 'high'
            })

        # Structure recommendations
        recommendations.append({
            'type': 'structure',
            'recommendation': 'Add chapter markers every 5-10 minutes for better navigation',
            'impact': 'medium',
            'effort': 'low'
        })

        # SEO recommendations
        recommendations.append({
            'type': 'discovery',
            'recommendation': 'Optimize title and description with target keywords',
            'impact': 'high',
            'effort': 'low',
            'details': 'Use tools like Google Keyword Planner for research'
        })

        return recommendations

    def _optimize_social_text(self, analysis: Dict[str, Any], goals: List[str]) -> List[Dict[str, Any]]:
        """Generate social media text optimization recommendations."""
        recommendations = []

        text_length = len(analysis.get('transcript_text', ''))

        # Length recommendations
        if 'twitter' in goals and text_length > 200:
            recommendations.append({
                'type': 'structure',
                'recommendation': 'Condense message to 100-150 characters for optimal Twitter engagement',
                'current_length': text_length,
                'target_length': 120,
                'impact': 'high',
                'effort': 'medium'
            })

        # Hashtag recommendations
        recommendations.append({
            'type': 'discovery',
            'recommendation': 'Use 2-3 relevant hashtags for Twitter, 15-30 for Instagram',
            'impact': 'medium',
            'effort': 'low'
        })

        # CTA recommendations
        recommendations.append({
            'type': 'conversion',
            'recommendation': 'Include clear call-to-action (e.g., "Listen now", "Watch full episode")',
            'impact': 'high',
            'effort': 'low'
        })

        return recommendations

    def _general_optimizations(self, analysis: Dict[str, Any], goals: List[str]) -> List[Dict[str, Any]]:
        """Generate general optimization recommendations."""
        recommendations = []

        # Sentiment-based recommendations
        sentiment_score = analysis.get('metrics', {}).get('sentiment', {}).get('sentiment_score', 0)
        if sentiment_score < -0.1 and 'engagement' in goals:
            recommendations.append({
                'type': 'tone',
                'recommendation': 'Increase positive language and enthusiastic delivery',
                'current_sentiment': sentiment_score,
                'target_sentiment': 0.2,
                'impact': 'medium',
                'effort': 'medium'
            })

        # Topic focus recommendations
        topics = analysis.get('metrics', {}).get('topics', {}).get('detected_topics', [])
        if len(topics) > 3:
            recommendations.append({
                'type': 'focus',
                'recommendation': 'Focus on 1-2 primary topics for clearer messaging',
                'current_topics': len(topics),
                'target_topics': 2,
                'impact': 'medium',
                'effort': 'high'
            })

        # Brand consistency
        recommendations.append({
            'type': 'branding',
            'recommendation': 'Ensure consistent use of brand colors, fonts, and logo placement',
            'impact': 'medium',
            'effort': 'low'
        })

        return recommendations

    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]],
                                    goals: List[str]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on goals and impact."""
        # Score each recommendation based on goals
        for rec in recommendations:
            score = 0

            # Boost score for relevant goals
            if rec['type'] == 'engagement' and 'engagement' in goals:
                score += 2
            elif rec['type'] == 'discovery' and 'reach' in goals:
                score += 2
            elif rec['type'] == 'conversion' and 'conversion' in goals:
                score += 2
            elif rec['type'] == 'structure' and 'retention' in goals:
                score += 2

            # Impact scoring
            impact_scores = {'very_high': 3, 'high': 2, 'medium': 1, 'low': 0}
            score += impact_scores.get(rec.get('impact', 'medium'), 1)

            rec['priority_score'] = score

        # Sort by priority score (descending)
        return sorted(recommendations, key=lambda x: x['priority_score'], reverse=True)

    def _get_implementation_plan(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create implementation plan for recommendations."""
        high_priority = [r for r in recommendations if r.get('priority_score', 0) >= 3]
        medium_priority = [r for r in recommendations if 2 <= r.get('priority_score', 0) < 3]
        low_priority = [r for r in recommendations if r.get('priority_score', 0) < 2]

        return {
            'total_recommendations': len(recommendations),
            'high_priority': {
                'count': len(high_priority),
                'recommendations': high_priority,
                'estimated_time': '1-2 days'
            },
            'medium_priority': {
                'count': len(medium_priority),
                'recommendations': medium_priority,
                'estimated_time': '3-5 days'
            },
            'low_priority': {
                'count': len(low_priority),
                'recommendations': low_priority,
                'estimated_time': '1-2 weeks'
            },
            'suggested_timeline': 'Implement high priority first, then medium, with low priority as ongoing improvements'
        }

    def _estimate_impact(self, recommendations: List[Dict[str, Any]],
                         analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate potential impact of recommendations."""
        impact_scores = {
            'very_high': 0.25,
            'high': 0.15,
            'medium': 0.08,
            'low': 0.03
        }

        total_impact = sum(impact_scores.get(r.get('impact', 'medium'), 0) for r in recommendations)

        # Get current engagement score
        current_score = analysis.get('metrics', {}).get('engagement', {}).get('engagement_score', 50)

        estimated_new_score = min(100, current_score + total_impact * 100)

        return {
            'current_engagement_score': current_score,
            'estimated_new_score': round(estimated_new_score, 1),
            'potential_improvement': round(estimated_new_score - current_score, 1),
            'impact_level': self._get_impact_level(total_impact)
        }

    def _get_impact_level(self, impact_score: float) -> str:
        """Get impact level description."""
        if impact_score >= 0.4:
            return 'Transformative'
        elif impact_score >= 0.25:
            return 'Significant'
        elif impact_score >= 0.15:
            return 'Moderate'
        elif impact_score >= 0.08:
            return 'Minor'
        else:
            return 'Incremental'


class MetadataGenerationTool(RobustTool):
    """Tool for generating SEO-optimized metadata."""

    def __init__(self):
        super().__init__(
            name="generate_metadata",
            description="Create SEO-optimized metadata and descriptions"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for metadata generation."""
        return {
            'type': 'object',
            'required': ['episode_title', 'content_analysis'],
            'properties': {
                'episode_title': {
                    'type': 'string',
                    'description': 'Episode title'
                },
                'content_analysis': {
                    'type': 'object',
                    'description': 'Content analysis results'
                },
                'guest_names': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Names of guests'
                },
                'episode_number': {
                    'type': 'integer',
                    'description': 'Episode number'
                },
                'season_number': {
                    'type': 'integer',
                    'description': 'Season number'
                },
                'target_keywords': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Target keywords for SEO'
                },
                'platform': {
                    'type': 'string',
                    'enum': ['youtube', 'podcast', 'website', 'social'],
                    'default': 'youtube',
                    'description': 'Primary target platform'
                }
            }
        }

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Generate optimized metadata."""
        episode_title = parameters['episode_title']
        analysis = parameters['content_analysis']
        guest_names = parameters.get('guest_names', [])
        episode_number = parameters.get('episode_number')
        season_number = parameters.get('season_number')
        target_keywords = parameters.get('target_keywords', [])
        platform = parameters.get('platform', 'youtube')

        # Extract topics and sentiment
        topics = analysis.get('metrics', {}).get('topics', {}).get('detected_topics', [])
        sentiment = analysis.get('metrics', {}).get('sentiment', {}).get('sentiment', 'Neutral')
        engagement_score = analysis.get('metrics', {}).get('engagement', {}).get('engagement_score', 50)

        # Generate metadata based on platform
        if platform == 'youtube':
            metadata = self._generate_youtube_metadata(
                episode_title, topics, guest_names, episode_number,
                season_number, target_keywords, sentiment, engagement_score
            )
        elif platform == 'podcast':
            metadata = self._generate_podcast_metadata(
                episode_title, topics, guest_names, episode_number,
                season_number, target_keywords
            )
        else:  # website/social
            metadata = self._generate_general_metadata(
                episode_title, topics, guest_names, target_keywords, sentiment
            )

        return {
            'episode_title': episode_title,
            'platform': platform,
            'generated_metadata': metadata,
            'seo_score': self._calculate_seo_score(metadata, target_keywords),
            'optimization_tips': self._get_metadata_tips(metadata, platform)
        }

    def _generate_youtube_metadata(self, title: str, topics: List[str], guests: List[str],
                                   episode_num: Optional[int], season_num: Optional[int],
                                   keywords: List[str], sentiment: str, engagement: float) -> Dict[str, Any]:
        """Generate YouTube-optimized metadata."""
        # Create SEO-optimized title
        seo_title = self._create_seo_title(title, topics, guests)

        # Generate description
        description = self._create_youtube_description(
            title, topics, guests, episode_num, season_num, sentiment, engagement
        )

        # Generate tags
        tags = self._generate_tags(topics, guests, keywords, 'youtube')

        # Create chapter markers if we have engagement data
        chapters = []
        if engagement > 70:
            chapters = [
                {
                    'time': '00:00',
                    'title': 'Introduction'
                },
                {
                    'time': '05:00',
                    'title': f'Deep dive into {topics[0] if topics else "main topic"}'
                },
                {
                    'time': '20:00',
                    'title': 'Key insights and takeaways'
                }
            ]

        return {
            'title': seo_title,
            'description': description,
            'tags': tags,
            'chapters': chapters,
            'category': self._get_youtube_category(topics),
            'visibility': 'public',
            'made_for_kids': False,
            'allow_embedding': True,
            'license': 'creativeCommons'
        }

    def _generate_podcast_metadata(self, title: str, topics: List[str], guests: List[str],
                                   episode_num: Optional[int], season_num: Optional[int],
                                   keywords: List[str]) -> Dict[str, Any]:
        """Generate podcast-optimized metadata."""
        # Create podcast title
        podcast_title = title
        if episode_num:
            podcast_title = f"#{episode_num} - {title}"
        if season_num:
            podcast_title = f"Season {season_num}, #{episode_num} - {title}"

        # Generate subtitle/description
        subtitle = self._create_podcast_subtitle(title, topics, guests)
        description = self._create_podcast_description(title, topics, guests, episode_num, season_num)

        # Generate tags and keywords
        tags = self._generate_tags(topics, guests, keywords, 'podcast')

        return {
            'title': podcast_title,
            'subtitle': subtitle,
            'description': description,
            'author': '[PODCAST_NAME]',
            'explicit': False,
            'keywords': ', '.join(tags),
            'episode_type': 'full',
            'episode_number': episode_num,
            'season_number': season_num,
            'block': 'no',
            'copyright': f'© {datetime.now().year} [PODCAST_NAME]'
        }

    def _generate_general_metadata(self, title: str, topics: List[str], guests: List[str],
                                   keywords: List[str], sentiment: str) -> Dict[str, Any]:
        """Generate general metadata for website/social."""
        # Create meta title and description
        meta_title = self._create_meta_title(title, topics, guests)
        meta_description = self._create_meta_description(title, topics, guests, sentiment)

        # Generate open graph tags
        og_tags = {
            'og:title': meta_title,
            'og:description': meta_description,
            'og:type': 'website',
            'og:url': '[EPISODE_URL]',
            'og:image': '[EPISODE_IMAGE_URL]',
            'og:site_name': '[PODCAST_NAME]'
        }

        # Generate Twitter cards
        twitter_tags = {
            'twitter:card': 'summary_large_image',
            'twitter:title': meta_title,
            'twitter:description': meta_description,
            'twitter:image': '[EPISODE_IMAGE_URL]',
            'twitter:site': '@[TWITTER_HANDLE]',
            'twitter:creator': '@[TWITTER_HANDLE]'
        }

        return {
            'meta_title': meta_title,
            'meta_description': meta_description,
            'keywords': ', '.join(self._generate_tags(topics, guests, keywords, 'general')),
            'open_graph': og_tags,
            'twitter_cards': twitter_tags,
            'canonical_url': '[EPISODE_URL]',
            'robots': 'index, follow'
        }

    def _create_seo_title(self, title: str, topics: List[str], guests: List[str]) -> str:
        """Create SEO-optimized title."""
        base_title = title

        # Add guest names if present
        if guests:
            base_title = f"{title} with {', '.join(guests)}"

        # Add topic keywords if they improve SEO
        if topics and len(base_title) < 60:
            primary_topic = topics[0]
            if primary_topic not in base_title.lower():
                base_title = f"{base_title} | {primary_topic.title()}"

        # Ensure title is within YouTube's 100 character limit
        return base_title[:97] + '...' if len(base_title) > 100 else base_title

    def _create_youtube_description(self, title: str, topics: List[str], guests: List[str],
                                    episode_num: Optional[int], season_num: Optional[int],
                                    sentiment: str, engagement: float) -> str:
        """Create YouTube description."""
        lines = []

        # Episode info
        if season_num and episode_num:
            lines.append(f"🎙️ [PODCAST_NAME] - Season {season_num}, Episode {episode_num}")
        elif episode_num:
            lines.append(f"🎙️ [PODCAST_NAME] - Episode {episode_num}")
        else:
            lines.append(f"🎙️ [PODCAST_NAME] - {title}")

        lines.append("")  # Blank line

        # Description based on sentiment and engagement
        if engagement > 80:
            lines.append("🔥 This is one of our most engaging episodes! Don't miss the incredible conversation about:")
        elif engagement > 60:
            lines.append("💬 Join us for a fascinating discussion covering:")
        else:
            lines.append("📚 In this episode, we explore:")

        # List topics
        for topic in topics[:5]:  # Top 5 topics
            lines.append(f"• {topic.title()}")

        lines.append("")  # Blank line

        # Guest info
        if guests:
            lines.append(f"👥 Featuring: {', '.join(guests)}")
            lines.append("")

        # Call to action
        lines.append("🔔 Subscribe for more amazing content!")
        lines.append("👍 Like this video if you enjoyed it!")
        lines.append("💬 Comment below with your thoughts!")

        lines.append("")  # Blank line

        # Additional info
        lines.append("#podcast #interview #conversation")
        if topics:
            lines.append(f"#{topics[0].replace(' ', '')}")

        return '\n'.join(lines)

    def _create_podcast_subtitle(self, title: str, topics: List[str], guests: List[str]) -> str:
        """Create podcast subtitle."""
        if guests:
            return f"A conversation with {', '.join(guests)} about {topics[0] if topics else 'important topics'}"
        else:
            return f"Exploring {topics[0] if topics else 'fascinating subjects'} in depth"

    def _create_podcast_description(self, title: str, topics: List[str], guests: List[str],
                                    episode_num: Optional[int], season_num: Optional[int]) -> str:
        """Create podcast episode description."""
        lines = []

        if season_num and episode_num:
            lines.append(f"Season {season_num}, Episode {episode_num}: {title}")
        elif episode_num:
            lines.append(f"Episode {episode_num}: {title}")
        else:
            lines.append(title)

        lines.append("")

        if guests:
            lines.append(f"In this episode, we're joined by {', '.join(guests)} to discuss:")
        else:
            lines.append("In this episode, we explore:")

        for topic in topics[:3]:  # Top 3 topics
            lines.append(f"• {topic.title()}")

        lines.append("")
        lines.append("Don't forget to subscribe, rate, and review!")

        return '\n'.join(lines)

    def _create_meta_title(self, title: str, topics: List[str], guests: List[str]) -> str:
        """Create meta title for SEO."""
        base = title

        if guests:
            base = f"{title} with {', '.join(guests)}"

        if topics and len(base) < 60:
            base = f"{base} | {topics[0].title()}"

        return base[:57] + '...' if len(base) > 60 else base

    def _create_meta_description(self, title: str, topics: List[str], guests: List[str],
                                sentiment: str) -> str:
        """Create meta description for SEO."""
        desc = []

        if sentiment == 'Positive':
            desc.append("Join us for an exciting episode of [PODCAST_NAME]")
        else:
            desc.append("Listen to the latest episode of [PODCAST_NAME]")

        if guests:
            desc.append(f"featuring {', '.join(guests)}")

        desc.append(f"as we discuss {topics[0] if topics else 'important topics'}")

        if len(topics) > 1:
            desc.append(f"and explore {', '.join(topics[1:3])}")

        desc.append("Don't miss this insightful conversation!")

        description = ' '.join(desc)
        return description[:157] + '...' if len(description) > 160 else description

    def _generate_tags(self, topics: List[str], guests: List[str], keywords: List[str],
                      platform: str) -> List[str]:
        """Generate platform-appropriate tags."""
        tags = []

        # Add podcast name
        tags.append('[PODCAST_NAME]')

        # Add topics
        for topic in topics[:5]:
            tags.append(topic.title())

        # Add guest names
        for guest in guests:
            tags.append(guest)

        # Add keywords
        for keyword in keywords:
            if keyword not in tags:
                tags.append(keyword)

        # Add platform-specific tags
        if platform == 'youtube':
            tags.extend(['podcast', 'interview', 'talk show', 'conversation'])
        elif platform == 'podcast':
            tags.extend(['podcast', 'audio', 'interview', 'discussion'])

        # Remove duplicates and limit count
        unique_tags = list(dict.fromkeys(tags))

        if platform == 'youtube':
            return unique_tags[:50]  # YouTube limit
        elif platform == 'podcast':
            return unique_tags[:20]  # Reasonable limit for podcasts
        else:
            return unique_tags[:10]  # For general use

    def _get_youtube_category(self, topics: List[str]) -> str:
        """Determine YouTube category based on topics."""
        topic_str = ' '.join(topics).lower()

        if any(word in topic_str for word in ['tech', 'software', 'computer', 'ai']):
            return 'Science & Technology'
        elif any(word in topic_str for word in ['business', 'money', 'invest', 'market']):
            return 'Business'
        elif any(word in topic_str for word in ['movie', 'tv', 'celebrity', 'hollywood']):
            return 'Entertainment'
        elif any(word in topic_str for word in ['sport', 'game', 'team', 'player']):
            return 'Sports'
        else:
            return 'Education'  # Default category

    def _calculate_seo_score(self, metadata: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Calculate SEO score for generated metadata."""
        score = 70  # Base score

        # Check title length
        title = metadata.get('title', metadata.get('meta_title', ''))
        if 30 <= len(title) <= 60:
            score += 5

        # Check description length
        description = metadata.get('description', metadata.get('meta_description', ''))
        if 100 <= len(description) <= 160:
            score += 5

        # Check keyword usage
        text_content = f"{title} {description}".lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_content)
        if keyword_matches >= len(keywords) * 0.7:
            score += 10

        # Check for call to action
        cta_phrases = ['subscribe', 'like', 'comment', 'share', 'listen', 'watch']
        if any(phrase in text_content for phrase in cta_phrases):
            score += 5

        # Platform-specific checks
        if 'tags' in metadata and len(metadata['tags']) >= 5:
            score += 5

        # Determine score level
        if score >= 90:
            level = 'Excellent'
        elif score >= 80:
            level = 'Good'
        elif score >= 70:
            level = 'Fair'
        elif score >= 60:
            level = 'Poor'
        else:
            level = 'Needs Improvement'

        return {
            'seo_score': score,
            'score_level': level,
            'strengths': self._get_seo_strengths(metadata, keywords),
            'improvements': self._get_seo_improvements(metadata, keywords)
        }

    def _get_seo_strengths(self, metadata: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Identify SEO strengths."""
        strengths = []

        title = metadata.get('title', metadata.get('meta_title', ''))
        description = metadata.get('description', metadata.get('meta_description', ''))

        if 30 <= len(title) <= 60:
            strengths.append('Optimal title length')

        if 100 <= len(description) <= 160:
            strengths.append('Good description length')

        text_content = f"{title} {description}".lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_content)
        if keyword_matches >= len(keywords) * 0.7:
            strengths.append('Effective keyword usage')

        if 'tags' in metadata and len(metadata['tags']) >= 5:
            strengths.append('Comprehensive tagging')

        cta_phrases = ['subscribe', 'like', 'comment', 'share', 'listen', 'watch']
        if any(phrase in text_content for phrase in cta_phrases):
            strengths.append('Clear call-to-action')

        return strengths

    def _get_seo_improvements(self, metadata: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Identify SEO improvement opportunities."""
        improvements = []

        title = metadata.get('title', metadata.get('meta_title', ''))
        description = metadata.get('description', metadata.get('meta_description', ''))

        if len(title) < 30:
            improvements.append('Title could be more descriptive')
        elif len(title) > 60:
            improvements.append('Title is too long for optimal SEO')

        if len(description) < 100:
            improvements.append('Description could be more detailed')
        elif len(description) > 160:
            improvements.append('Description is too long for optimal display')

        text_content = f"{title} {description}".lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_content)
        if keyword_matches < len(keywords) * 0.5:
            improvements.append('Could incorporate more target keywords')

        if 'tags' in metadata and len(metadata['tags']) < 5:
            improvements.append('Could benefit from additional relevant tags')

        cta_phrases = ['subscribe', 'like', 'comment', 'share', 'listen', 'watch']
        if not any(phrase in text_content for phrase in cta_phrases):
            improvements.append('Consider adding a clear call-to-action')

        return improvements

    def _get_metadata_tips(self, metadata: Dict[str, Any], platform: str) -> List[str]:
        """Get platform-specific metadata tips."""
        tips = []

        if platform == 'youtube':
            tips.extend([
                'Use the first 48 characters of your title to capture attention',
                'Include timestamps in your description for better navigation',
                'Use a mix of broad and specific tags for better discoverability',
                'Add chapter markers to improve viewer experience and SEO'
            ])
        elif platform == 'podcast':
            tips.extend([
                'Include episode numbers in your title for better organization',
                'Use detailed show notes in the description',
                'Mention any special guests prominently',
                'Include links to resources mentioned in the episode'
            ])
        else:  # website/social
            tips.extend([
                'Keep meta titles under 60 characters for optimal display',
                'Meta descriptions should be compelling and under 160 characters',
                'Use Open Graph tags to control how content appears when shared',
                'Include relevant keywords naturally in your metadata'
            ])

        return tips

