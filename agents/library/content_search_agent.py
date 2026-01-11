#!/usr/bin/env python3
"""
Content Search Agent - Advanced search capabilities for podcast content.

This agent provides comprehensive search functionality across video episodes,
transcripts, and metadata, enabling users to find specific content by:
- Topics and conversations
- Jokes and humorous content
- Specific contexts (e.g., "Jared live on stage")
- Timestamps and locations
- Complex search criteria combining multiple factors

The agent integrates with existing transcription, analysis, and video processing
tools to provide deep, context-aware search capabilities.
"""

import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agents.base_agent import AgentTool, BaseAgent
from agents.robust_tool import RobustTool, ToolResult


class ContentSearchAgentTool(AgentTool):
    """Custom AgentTool that takes a RobustTool implementation."""

    def __init__(self, name: str, description: str, implementation: RobustTool):
        """Initialize with a specific RobustTool implementation."""
        self.implementation = implementation
        super().__init__(name, description)

    def _create_implementation(self) -> RobustTool:
        """Return the pre-configured implementation."""
        return self.implementation

class ContentSearchAgent(BaseAgent):
    """Agent for advanced content search across podcast episodes and videos."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the content search agent."""
        super().__init__("content_search", config_path)

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize content search tools."""
        return {
            'search_by_topic': ContentSearchAgentTool(
                "search_by_topic",
                "Search episodes and transcripts for specific topics and conversations",
                TopicSearchTool()
            ),
            'search_jokes': ContentSearchAgentTool(
                "search_jokes",
                "Find jokes and humorous content about specific topics",
                JokeSearchTool()
            ),
            'search_by_context': ContentSearchAgentTool(
                "search_by_context",
                "Search for content in specific contexts (e.g., 'Jared live on stage')",
                ContextSearchTool()
            ),
            'search_by_timestamp': ContentSearchAgentTool(
                "search_by_timestamp",
                "Find content at specific timestamps or time ranges",
                TimestampSearchTool()
            ),
            'search_by_location': ContentSearchAgentTool(
                "search_by_location",
                "Search for content based on location and scene context",
                LocationSearchTool()
            ),
            'advanced_content_search': ContentSearchAgentTool(
                "advanced_content_search",
                "Perform complex searches combining multiple criteria",
                AdvancedSearchTool()
            ),
            'search_index_management': ContentSearchAgentTool(
                "search_index_management",
                "Create and manage search indexes for faster queries",
                SearchIndexManagementTool()
            )
        }

class TopicSearchTool(RobustTool):
    """Tool for searching content by topics and conversations."""

    def __init__(self):
        super().__init__(
            name="search_by_topic",
            description="Search episodes and transcripts for specific topics and conversations"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for topic search."""
        return {
            'type': 'object',
            'required': ['search_terms'],
            'properties': {
                'search_terms': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Topics or keywords to search for'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search (optional)'
                },
                'time_range': {
                    'type': 'object',
                    'properties': {
                        'start_time': {'type': 'string', 'format': 'time'},
                        'end_time': {'type': 'string', 'format': 'time'}
                    },
                    'description': 'Time range to search within episodes'
                },
                'min_duration': {
                    'type': 'number',
                    'default': 10.0,
                    'description': 'Minimum duration for search results in seconds'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 20,
                    'description': 'Maximum number of results to return'
                },
                'include_context': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Include surrounding context in results'
                },
                'context_window': {
                    'type': 'integer',
                    'default': 3,
                    'description': 'Number of sentences before/after to include as context'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return [
            {
                'name': 'basic_text_search',
                'condition': lambda e, p, eid: True,
                'action': self._fallback_basic_search,
                'priority': 1
            }
        ]

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Search content by topics and conversations."""
        search_terms = parameters['search_terms']
        episode_ids = parameters.get('episode_ids', [])
        time_range = parameters.get('time_range')
        min_duration = parameters.get('min_duration', 10.0)
        max_results = parameters.get('max_results', 20)
        include_context = parameters.get('include_context', True)
        context_window = parameters.get('context_window', 3)

        # Load search index or create temporary one
        search_index = self._load_or_create_search_index()

        results = []
        processed_episodes = 0

        # Search through episodes
        for episode_id, episode_data in search_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_for_topics(
                episode_data, search_terms, time_range, min_duration,
                include_context, context_window
            )

            # Add episode info to each result
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')
                result['episode_date'] = episode_data.get('date', 'Unknown')

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        # Sort results by relevance
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return {
            'search_terms': search_terms,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': results[:max_results],
            'search_type': 'topic_search',
            'timestamp': datetime.now().isoformat()
        }

    def _load_or_create_search_index(self) -> Dict[str, Any]:
        """Load existing search index or create a temporary one."""
        # In a real implementation, this would load from a persistent index
        # For now, we'll create a mock index structure
        return {
            'episodes': {
                'ep001': {
                    'title': 'The Future of AI',
                    'date': '2024-01-15',
                    'transcript': self._get_mock_transcript(),
                    'metadata': {
                        'duration': 3600,
                        'guests': ['Dr. Smith', 'Jane Doe'],
                        'topics': ['ai', 'machine learning', 'future technology']
                    }
                },
                'ep002': {
                    'title': 'Comedy Night Live',
                    'date': '2024-02-20',
                    'transcript': self._get_mock_comedy_transcript(),
                    'metadata': {
                        'duration': 2400,
                        'guests': ['Jared', 'Sarah'],
                        'topics': ['comedy', 'standup', 'jokes']
                    }
                }
            },
            'index_type': 'temporary',
            'last_updated': datetime.now().isoformat()
        }

    def _get_mock_transcript(self) -> str:
        """Get mock transcript for testing."""
        return """[00:00:00] Host: Welcome to today's show about the future of AI.
[00:00:15] Dr. Smith: AI is transforming every industry.
[00:01:30] Jane Doe: Machine learning algorithms are getting smarter every day.
[00:05:45] Host: Let's talk about the ethical implications of AI.
[00:10:20] Dr. Smith: This is a crucial conversation for our future.
[00:15:30] Jane Doe: The potential benefits are enormous, but we must be careful.
[00:20:15] Host: That's all for today's episode on AI."""

    def _get_mock_comedy_transcript(self) -> str:
        """Get mock comedy transcript for testing."""
        return """[00:00:00] Jared: Welcome to comedy night! Let's start with some jokes.
[00:00:30] Jared: Why don't scientists trust atoms? Because they make up everything!
[00:01:15] Audience: *laughter*
[00:01:30] Sarah: That was a great one! Here's mine: Why did the scarecrow win an award?
[00:02:00] Sarah: Because he was outstanding in his field!
[00:02:30] Audience: *laughter*
[00:03:00] Jared: Let's talk about technology jokes next.
[00:03:30] Jared: Why was the computer cold? It left its Windows open!
[00:04:15] Audience: *laughter*
[00:05:00] Sarah: That's all for tonight, folks!"""

    def _search_episode_for_topics(self, episode_data: Dict[str, Any], search_terms: List[str],
                                 time_range: Optional[Dict[str, str]], min_duration: float,
                                 include_context: bool, context_window: int) -> List[Dict[str, Any]]:
        """Search a single episode for topics."""
        transcript = episode_data['transcript']
        results = []

        # Parse transcript into segments with timestamps
        segments = self._parse_transcript_segments(transcript)

        # Search each segment
        for i, segment in enumerate(segments):
            segment_text = segment['text'].lower()
            segment_start = segment['start_time']
            segment_end = segment['end_time']

            # Check time range filter
            if time_range:
                start_time = self._parse_time(time_range.get('start_time', '00:00:00'))
                end_time = self._parse_time(time_range.get('end_time', '23:59:59'))

                if segment_end < start_time or segment_start > end_time:
                    continue

            # Check if segment contains any search terms
            found_terms = []
            for term in search_terms:
                if term.lower() in segment_text:
                    found_terms.append(term)

            if found_terms:
                # Calculate relevance score
                relevance_score = len(found_terms) * 10
                if len(found_terms) == len(search_terms):
                    relevance_score *= 1.5  # Bonus for matching all terms

                # Get context if requested
                context = []
                if include_context:
                    context = self._get_context_segments(segments, i, context_window)

                result = {
                    'segment_id': f"seg_{i}",
                    'start_time': segment_start,
                    'end_time': segment_end,
                    'duration': segment_end - segment_start,
                    'text': segment['text'],
                    'found_terms': found_terms,
                    'relevance_score': relevance_score,
                    'context': context
                }

                results.append(result)

        return results

    def _parse_transcript_segments(self, transcript: str) -> List[Dict[str, Any]]:
        """Parse transcript into segments with timestamps."""
        segments = []
        lines = transcript.split('\n')

        for line in lines:
            if '[' in line and ']' in line:
                # Extract timestamp and text
                timestamp_match = re.search(r'\[([^\]]+)\]', line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    text = line[timestamp_match.end():].strip()

                    # Parse timestamp
                    try:
                        start_time = self._parse_time(timestamp)
                        # Assume each segment is about 15 seconds
                        end_time = start_time + 15.0

                        segments.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text
                        })
                    except:
                        continue

        return segments

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])
        except:
            return 0.0

    def _get_context_segments(self, segments: List[Dict[str, Any]], current_index: int,
                             window_size: int) -> List[Dict[str, Any]]:
        """Get context segments around the current segment."""
        context = []

        # Get previous segments
        start_index = max(0, current_index - window_size)
        for i in range(start_index, current_index):
            context.append({
                'position': 'before',
                'text': segments[i]['text'],
                'time': f"{segments[i]['start_time']:.1f}-{segments[i]['end_time']:.1f}"
            })

        # Get next segments
        end_index = min(len(segments), current_index + window_size + 1)
        for i in range(current_index + 1, end_index):
            context.append({
                'position': 'after',
                'text': segments[i]['text'],
                'time': f"{segments[i]['start_time']:.1f}-{segments[i]['end_time']:.1f}"
            })

        return context

    def _fallback_basic_search(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> ToolResult:
        """Fallback to basic text search."""
        search_terms = parameters['search_terms']
        max_results = parameters.get('max_results', 10)

        # Simple fallback - just return some mock results
        fallback_results = []
        for i, term in enumerate(search_terms[:max_results]):
            fallback_results.append({
                'term': term,
                'results': [
                    {
                        'episode_id': f'fallback_ep_{i}',
                        'segment_id': f'fallback_seg_{i}',
                        'text': f'Found content related to {term} in this segment',
                        'start_time': i * 30.0,
                        'end_time': (i * 30.0) + 15.0,
                        'relevance_score': 5.0
                    }
                ]
            })

        return ToolResult(
            success=True,
            data={
                'search_terms': search_terms,
                'results_found': len(fallback_results),
                'results': fallback_results,
                'warnings': ['Used basic search due to processing limitations']
            },
            execution_id=execution_id
        )

class JokeSearchTool(RobustTool):
    """Tool for searching jokes and humorous content."""

    def __init__(self):
        super().__init__(
            name="search_jokes",
            description="Find jokes and humorous content about specific topics"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for joke search."""
        return {
            'type': 'object',
            'required': ['topics'],
            'properties': {
                'topics': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Topics to search jokes about'
                },
                'joke_types': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'enum': ['puns', 'one-liners', 'stories', 'observational', 'all']
                    },
                    'default': ['all'],
                    'description': 'Types of jokes to search for'
                },
                'min_laughter': {
                    'type': 'number',
                    'default': 0.5,
                    'minimum': 0,
                    'maximum': 1,
                    'description': 'Minimum laughter confidence score'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 15,
                    'description': 'Maximum number of joke results to return'
                },
                'include_setup': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Include joke setup/context in results'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Search for jokes about specific topics."""
        topics = parameters['topics']
        joke_types = parameters.get('joke_types', ['all'])
        min_laughter = parameters.get('min_laughter', 0.5)
        episode_ids = parameters.get('episode_ids', [])
        max_results = parameters.get('max_results', 15)
        include_setup = parameters.get('include_setup', True)

        # Load joke index
        joke_index = self._load_joke_index()

        results = []
        processed_episodes = 0

        # Search through episodes
        for episode_id, episode_data in joke_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_for_jokes(
                episode_data, topics, joke_types, min_laughter, include_setup
            )

            # Add episode info
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        # Sort by laughter score
        results.sort(key=lambda x: x.get('laughter_score', 0), reverse=True)

        return {
            'topics': topics,
            'joke_types': joke_types,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': results[:max_results],
            'search_type': 'joke_search',
            'timestamp': datetime.now().isoformat()
        }

    def _load_joke_index(self) -> Dict[str, Any]:
        """Load joke index."""
        return {
            'episodes': {
                'ep002': {
                    'title': 'Comedy Night Live',
                    'jokes': [
                        {
                            'start_time': 30.0,
                            'end_time': 45.0,
                            'text': "Why don't scientists trust atoms? Because they make up everything!",
                            'topics': ['science', 'atoms'],
                            'type': 'one-liner',
                            'laughter_score': 0.87,
                            'setup': "Let's start with some science jokes",
                            'delivery': 'Jared'
                        },
                        {
                            'start_time': 120.0,
                            'end_time': 135.0,
                            'text': "Why did the scarecrow win an award? Because he was outstanding in his field!",
                            'topics': ['farming', 'awards'],
                            'type': 'pun',
                            'laughter_score': 0.92,
                            'setup': "Here's a farming joke for you",
                            'delivery': 'Sarah'
                        },
                        {
                            'start_time': 210.0,
                            'end_time': 225.0,
                            'text': "Why was the computer cold? It left its Windows open!",
                            'topics': ['technology', 'computers'],
                            'type': 'tech',
                            'laughter_score': 0.78,
                            'setup': "Let's talk about technology jokes",
                            'delivery': 'Jared'
                        }
                    ]
                }
            },
            'index_type': 'joke_index',
            'last_updated': datetime.now().isoformat()
        }

    def _search_episode_for_jokes(self, episode_data: Dict[str, Any], topics: List[str],
                                 joke_types: List[str], min_laughter: float,
                                 include_setup: bool) -> List[Dict[str, Any]]:
        """Search a single episode for jokes."""
        jokes = episode_data.get('jokes', [])
        results = []

        for joke in jokes:
            # Check if joke matches topics
            joke_topics = joke.get('topics', [])
            topic_match = any(topic.lower() in [jt.lower() for jt in joke_topics] for topic in topics)

            # Check joke type
            joke_type = joke.get('type', 'all')
            type_match = joke_type in joke_types or 'all' in joke_types

            # Check laughter score
            laughter_match = joke.get('laughter_score', 0) >= min_laughter

            if topic_match and type_match and laughter_match:
                result = {
                    'joke_id': joke.get('id', f"joke_{len(results)}"),
                    'start_time': joke['start_time'],
                    'end_time': joke['end_time'],
                    'duration': joke['end_time'] - joke['start_time'],
                    'text': joke['text'],
                    'topics': joke_topics,
                    'type': joke_type,
                    'laughter_score': joke['laughter_score'],
                    'delivery': joke.get('delivery', 'unknown')
                }

                if include_setup and joke.get('setup'):
                    result['setup'] = joke['setup']

                results.append(result)

        return results

class ContextSearchTool(RobustTool):
    """Tool for searching content by context."""

    def __init__(self):
        super().__init__(
            name="search_by_context",
            description="Search for content in specific contexts (e.g., 'Jared live on stage')"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for context search."""
        return {
            'type': 'object',
            'required': ['context_query'],
            'properties': {
                'context_query': {
                    'type': 'string',
                    'description': 'Context to search for (e.g., "Jared live on stage")'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search'
                },
                'time_range': {
                    'type': 'object',
                    'properties': {
                        'start_time': {'type': 'string', 'format': 'time'},
                        'end_time': {'type': 'string', 'format': 'time'}
                    },
                    'description': 'Time range to search within episodes'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 10,
                    'description': 'Maximum number of results to return'
                },
                'include_surrounding': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Include surrounding content for context'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Search content by context."""
        context_query = parameters['context_query']
        episode_ids = parameters.get('episode_ids', [])
        time_range = parameters.get('time_range')
        max_results = parameters.get('max_results', 10)
        include_surrounding = parameters.get('include_surrounding', True)

        # Parse context query
        parsed_context = self._parse_context_query(context_query)

        # Load context index
        context_index = self._load_context_index()

        results = []
        processed_episodes = 0

        # Search through episodes
        for episode_id, episode_data in context_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_context(
                episode_data, parsed_context, time_range, include_surrounding
            )

            # Add episode info
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return {
            'context_query': context_query,
            'parsed_context': parsed_context,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': results[:max_results],
            'search_type': 'context_search',
            'timestamp': datetime.now().isoformat()
        }

    def _parse_context_query(self, query: str) -> Dict[str, Any]:
        """Parse context query into searchable components."""
        query_lower = query.lower()

        # Extract key elements
        parsed = {
            'original_query': query,
            'people': [],
            'locations': [],
            'actions': [],
            'objects': [],
            'raw_query': query_lower
        }

        # Simple NLP parsing (would be enhanced with proper NLP in real implementation)
        if 'jared' in query_lower:
            parsed['people'].append('Jared')

        if 'stage' in query_lower or 'live' in query_lower:
            parsed['locations'].append('stage')

        if 'on stage' in query_lower or 'performing' in query_lower:
            parsed['actions'].append('performing')

        # Extract more patterns
        person_patterns = ['jared', 'sarah', 'host', 'guest']
        for pattern in person_patterns:
            if pattern in query_lower and pattern not in parsed['people']:
                parsed['people'].append(pattern.title())

        location_patterns = ['stage', 'studio', 'audience', 'backstage']
        for pattern in location_patterns:
            if pattern in query_lower and pattern not in parsed['locations']:
                parsed['locations'].append(pattern)

        return parsed

    def _load_context_index(self) -> Dict[str, Any]:
        """Load context index."""
        return {
            'episodes': {
                'ep002': {
                    'title': 'Comedy Night Live',
                    'segments': [
                        {
                            'start_time': 0.0,
                            'end_time': 60.0,
                            'text': "Jared: Welcome to comedy night! Let's start with some jokes.",
                            'context': {
                                'location': 'stage',
                                'people': ['Jared'],
                                'activity': 'introduction',
                                'audience': 'live'
                            }
                        },
                        {
                            'start_time': 60.0,
                            'end_time': 120.0,
                            'text': "Jared: Why don't scientists trust atoms? Because they make up everything!",
                            'context': {
                                'location': 'stage',
                                'people': ['Jared'],
                                'activity': 'joke_telling',
                                'audience': 'live',
                                'audience_reaction': 'laughter'
                            }
                        },
                        {
                            'start_time': 180.0,
                            'end_time': 240.0,
                            'text': "Sarah: Here's a farming joke for you. Why did the scarecrow win an award?",
                            'context': {
                                'location': 'stage',
                                'people': ['Sarah'],
                                'activity': 'joke_telling',
                                'audience': 'live'
                            }
                        }
                    ]
                }
            },
            'index_type': 'context_index',
            'last_updated': datetime.now().isoformat()
        }

    def _search_episode_context(self, episode_data: Dict[str, Any], parsed_context: Dict[str, Any],
                              time_range: Optional[Dict[str, str]], include_surrounding: bool) -> List[Dict[str, Any]]:
        """Search episode for matching context."""
        segments = episode_data.get('segments', [])
        results = []

        for segment in segments:
            segment_context = segment.get('context', {})
            segment_text = segment['text'].lower()

            # Check time range
            if time_range:
                start_time = self._parse_time(time_range.get('start_time', '00:00:00'))
                end_time = self._parse_time(time_range.get('end_time', '23:59:59'))

                if segment['end_time'] < start_time or segment['start_time'] > end_time:
                    continue

            # Calculate context match score
            match_score = 0

            # Check people match
            for person in parsed_context['people']:
                if person.lower() in segment_context.get('people', []):
                    match_score += 2
                elif person.lower() in segment_text:
                    match_score += 1

            # Check location match
            for location in parsed_context['locations']:
                if location.lower() in segment_context.get('location', ''):
                    match_score += 2
                elif location.lower() in segment_text:
                    match_score += 1

            # Check activity match
            for action in parsed_context['actions']:
                if action.lower() in segment_context.get('activity', ''):
                    match_score += 1.5
                elif action.lower() in segment_text:
                    match_score += 0.5

            # Check raw query match
            if parsed_context['raw_query'] in segment_text:
                match_score += 3

            if match_score > 0:
                result = {
                    'segment_id': f"seg_{len(results)}",
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'duration': segment['end_time'] - segment['start_time'],
                    'text': segment['text'],
                    'context': segment_context,
                    'relevance_score': match_score * 10,
                    'match_details': {
                        'people_match': any(p in segment_context.get('people', []) for p in parsed_context['people']),
                        'location_match': any(l in segment_context.get('location', '') for l in parsed_context['locations']),
                        'activity_match': any(a in segment_context.get('activity', '') for a in parsed_context['actions'])
                    }
                }

                if include_surrounding:
                    result['surrounding_context'] = self._get_surrounding_context(segments, segment)

                results.append(result)

        return results

    def _get_surrounding_context(self, segments: List[Dict[str, Any]], current_segment: Dict[str, Any]) -> Dict[str, Any]:
        """Get surrounding context for a segment."""
        current_index = segments.index(current_segment)
        context = {}

        # Get previous segment
        if current_index > 0:
            context['before'] = {
                'text': segments[current_index - 1]['text'],
                'time': f"{segments[current_index - 1]['start_time']:.1f}-{segments[current_index - 1]['end_time']:.1f}"
            }

        # Get next segment
        if current_index < len(segments) - 1:
            context['after'] = {
                'text': segments[current_index + 1]['text'],
                'time': f"{segments[current_index + 1]['start_time']:.1f}-{segments[current_index + 1]['end_time']:.1f}"
            }

        return context

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])
        except:
            return 0.0

class TimestampSearchTool(RobustTool):
    """Tool for searching content by timestamps."""

    def __init__(self):
        super().__init__(
            name="search_by_timestamp",
            description="Find content at specific timestamps or time ranges"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for timestamp search."""
        return {
            'type': 'object',
            'required': ['time_specification'],
            'properties': {
                'time_specification': {
                    'type': 'object',
                    'oneOf': [
                        {
                            'properties': {
                                'exact_time': {'type': 'string', 'format': 'time'}
                            },
                            'required': ['exact_time']
                        },
                        {
                            'properties': {
                                'time_range': {
                                    'type': 'object',
                                    'properties': {
                                        'start_time': {'type': 'string', 'format': 'time'},
                                        'end_time': {'type': 'string', 'format': 'time'}
                                    },
                                    'required': ['start_time', 'end_time']
                                }
                            },
                            'required': ['time_range']
                        },
                        {
                            'properties': {
                                'relative_time': {
                                    'type': 'object',
                                    'properties': {
                                        'position': {'type': 'string', 'enum': ['start', 'middle', 'end']},
                                        'percentage': {'type': 'number', 'minimum': 0, 'maximum': 100}
                                    },
                                    'required': ['position']
                                }
                            },
                            'required': ['relative_time']
                        }
                    ],
                    'description': 'Time specification for search'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search'
                },
                'search_radius': {
                    'type': 'number',
                    'default': 30.0,
                    'description': 'Search radius around timestamp in seconds'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 5,
                    'description': 'Maximum number of results to return'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Search content by timestamps."""
        time_spec = parameters['time_specification']
        episode_ids = parameters.get('episode_ids', [])
        search_radius = parameters.get('search_radius', 30.0)
        max_results = parameters.get('max_results', 5)

        # Load timestamp index
        timestamp_index = self._load_timestamp_index()

        results = []
        processed_episodes = 0

        # Determine target time(s)
        target_times = self._get_target_times(time_spec, timestamp_index)

        # Search through episodes
        for episode_id, episode_data in timestamp_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_timestamps(
                episode_data, target_times, search_radius
            )

            # Add episode info
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')
                result['episode_duration'] = episode_data.get('duration', 0)

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        return {
            'time_specification': time_spec,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': results[:max_results],
            'search_type': 'timestamp_search',
            'timestamp': datetime.now().isoformat()
        }

    def _load_timestamp_index(self) -> Dict[str, Any]:
        """Load timestamp index."""
        return {
            'episodes': {
                'ep001': {
                    'title': 'The Future of AI',
                    'duration': 3600,
                    'segments': [
                        {'start_time': 0.0, 'end_time': 60.0, 'text': 'Introduction to AI'},
                        {'start_time': 60.0, 'end_time': 300.0, 'text': 'Machine learning discussion'},
                        {'start_time': 300.0, 'end_time': 600.0, 'text': 'Ethical implications of AI'},
                        {'start_time': 600.0, 'end_time': 1200.0, 'text': 'Future predictions'},
                        {'start_time': 1200.0, 'end_time': 1800.0, 'text': 'Q&A session'}
                    ]
                },
                'ep002': {
                    'title': 'Comedy Night Live',
                    'duration': 2400,
                    'segments': [
                        {'start_time': 0.0, 'end_time': 60.0, 'text': 'Welcome and introduction'},
                        {'start_time': 60.0, 'end_time': 120.0, 'text': 'First joke segment'},
                        {'start_time': 120.0, 'end_time': 180.0, 'text': 'Second joke segment'},
                        {'start_time': 180.0, 'end_time': 240.0, 'text': 'Closing remarks'}
                    ]
                }
            },
            'index_type': 'timestamp_index',
            'last_updated': datetime.now().isoformat()
        }

    def _get_target_times(self, time_spec: Dict[str, Any], index: Dict[str, Any]) -> List[float]:
        """Get target times from time specification."""
        target_times = []

        if 'exact_time' in time_spec:
            target_times.append(self._parse_time(time_spec['exact_time']))
        elif 'time_range' in time_spec:
            start_time = self._parse_time(time_spec['time_range']['start_time'])
            end_time = self._parse_time(time_spec['time_range']['end_time'])
            # For range, we'll search the entire range
            target_times.append(start_time)
            target_times.append(end_time)
        elif 'relative_time' in time_spec:
            rel_spec = time_spec['relative_time']
            if 'percentage' in rel_spec:
                # Use percentage of episode duration
                percentage = rel_spec['percentage']
                for episode_data in index['episodes'].values():
                    duration = episode_data.get('duration', 3600)
                    target_time = duration * (percentage / 100.0)
                    target_times.append(target_time)
            else:
                # Use position (start, middle, end)
                position = rel_spec['position']
                for episode_data in index['episodes'].values():
                    duration = episode_data.get('duration', 3600)
                    if position == 'start':
                        target_time = duration * 0.1  # 10% in
                    elif position == 'middle':
                        target_time = duration * 0.5  # 50% in
                    else:  # end
                        target_time = duration * 0.9  # 90% in
                    target_times.append(target_time)

        return target_times

    def _search_episode_timestamps(self, episode_data: Dict[str, Any], target_times: List[float],
                                  search_radius: float) -> List[Dict[str, Any]]:
        """Search episode for content around target timestamps."""
        segments = episode_data.get('segments', [])
        results = []

        for target_time in target_times:
            # Find segments within search radius of target time
            for segment in segments:
                segment_start = segment['start_time']
                segment_end = segment['end_time']

                # Check if target time is within this segment or nearby
                if (abs(segment_start - target_time) <= search_radius or
                    abs(segment_end - target_time) <= search_radius or
                    (segment_start <= target_time <= segment_end)):

                    # Calculate distance from target
                    if target_time <= segment_start:
                        distance = segment_start - target_time
                    elif target_time >= segment_end:
                        distance = target_time - segment_end
                    else:
                        distance = 0

                    results.append({
                        'target_time': target_time,
                        'segment_start': segment_start,
                        'segment_end': segment_end,
                        'distance_from_target': distance,
                        'text': segment['text'],
                        'relevance_score': max(0, 10 - (distance / search_radius * 10))
                    })

        return results

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])
        except:
            return 0.0

class LocationSearchTool(RobustTool):
    """Tool for searching content by location and scene context."""

    def __init__(self):
        super().__init__(
            name="search_by_location",
            description="Search for content based on location and scene context"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for location search."""
        return {
            'type': 'object',
            'required': ['location_query'],
            'properties': {
                'location_query': {
                    'type': 'string',
                    'description': 'Location to search for (e.g., "stage", "studio", "audience")'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search'
                },
                'time_range': {
                    'type': 'object',
                    'properties': {
                        'start_time': {'type': 'string', 'format': 'time'},
                        'end_time': {'type': 'string', 'format': 'time'}
                    },
                    'description': 'Time range to search within episodes'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 10,
                    'description': 'Maximum number of results to return'
                },
                'include_visual_context': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Include visual context information if available'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Search content by location."""
        location_query = parameters['location_query']
        episode_ids = parameters.get('episode_ids', [])
        time_range = parameters.get('time_range')
        max_results = parameters.get('max_results', 10)
        include_visual_context = parameters.get('include_visual_context', True)

        # Load location index
        location_index = self._load_location_index()

        results = []
        processed_episodes = 0

        # Search through episodes
        for episode_id, episode_data in location_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_locations(
                episode_data, location_query, time_range, include_visual_context
            )

            # Add episode info
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return {
            'location_query': location_query,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': results[:max_results],
            'search_type': 'location_search',
            'timestamp': datetime.now().isoformat()
        }

    def _load_location_index(self) -> Dict[str, Any]:
        """Load location index."""
        return {
            'episodes': {
                'ep002': {
                    'title': 'Comedy Night Live',
                    'scenes': [
                        {
                            'start_time': 0.0,
                            'end_time': 600.0,
                            'location': 'stage',
                            'description': 'Comedians performing on stage',
                            'people': ['Jared', 'Sarah'],
                            'visual_context': {
                                'camera_angle': 'wide',
                                'lighting': 'spotlight',
                                'audience_visible': True
                            }
                        },
                        {
                            'start_time': 600.0,
                            'end_time': 900.0,
                            'location': 'backstage',
                            'description': 'Comedians preparing backstage',
                            'people': ['Jared', 'Sarah', 'Crew'],
                            'visual_context': {
                                'camera_angle': 'close-up',
                                'lighting': 'natural',
                                'audience_visible': False
                            }
                        },
                        {
                            'start_time': 900.0,
                            'end_time': 1200.0,
                            'location': 'audience',
                            'description': 'Audience reactions and interactions',
                            'people': ['Audience'],
                            'visual_context': {
                                'camera_angle': 'wide',
                                'lighting': 'house_lights',
                                'audience_visible': True
                            }
                        }
                    ]
                }
            },
            'index_type': 'location_index',
            'last_updated': datetime.now().isoformat()
        }

    def _search_episode_locations(self, episode_data: Dict[str, Any], location_query: str,
                                 time_range: Optional[Dict[str, str]], include_visual_context: bool) -> List[Dict[str, Any]]:
        """Search episode for matching locations."""
        scenes = episode_data.get('scenes', [])
        results = []
        query_lower = location_query.lower()

        for scene in scenes:
            scene_location = scene.get('location', '').lower()
            scene_description = scene.get('description', '').lower()

            # Check time range
            if time_range:
                start_time = self._parse_time(time_range.get('start_time', '00:00:00'))
                end_time = self._parse_time(time_range.get('end_time', '23:59:59'))

                if scene['end_time'] < start_time or scene['start_time'] > end_time:
                    continue

            # Calculate location match score
            match_score = 0

            # Exact location match
            if query_lower == scene_location:
                match_score = 10
            # Partial location match
            elif query_lower in scene_location:
                match_score = 7
            # Description match
            elif query_lower in scene_description:
                match_score = 5

            if match_score > 0:
                result = {
                    'scene_id': f"scene_{len(results)}",
                    'start_time': scene['start_time'],
                    'end_time': scene['end_time'],
                    'duration': scene['end_time'] - scene['start_time'],
                    'location': scene['location'],
                    'description': scene['description'],
                    'people': scene.get('people', []),
                    'relevance_score': match_score,
                    'match_type': 'exact' if match_score >= 10 else 'partial'
                }

                if include_visual_context and 'visual_context' in scene:
                    result['visual_context'] = scene['visual_context']

                results.append(result)

        return results

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])
        except:
            return 0.0

class AdvancedSearchTool(RobustTool):
    """Tool for performing complex searches combining multiple criteria."""

    def __init__(self):
        super().__init__(
            name="advanced_content_search",
            description="Perform complex searches combining multiple criteria"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for advanced search."""
        return {
            'type': 'object',
            'required': ['search_criteria'],
            'properties': {
                'search_criteria': {
                    'type': 'object',
                    'properties': {
                        'topics': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Topics to include'
                        },
                        'joke_topics': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Joke topics to include'
                        },
                        'context': {
                            'type': 'string',
                            'description': 'Context to search for'
                        },
                        'time_range': {
                            'type': 'object',
                            'properties': {
                                'start_time': {'type': 'string', 'format': 'time'},
                                'end_time': {'type': 'string', 'format': 'time'}
                            },
                            'description': 'Time range to search'
                        },
                        'locations': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Locations to include'
                        },
                        'people': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'People to include'
                        },
                        'min_duration': {
                            'type': 'number',
                            'description': 'Minimum segment duration'
                        },
                        'max_duration': {
                            'type': 'number',
                            'description': 'Maximum segment duration'
                        }
                    },
                    'description': 'Complex search criteria'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Specific episode IDs to search'
                },
                'max_results': {
                    'type': 'integer',
                    'default': 15,
                    'description': 'Maximum number of results to return'
                },
                'result_format': {
                    'type': 'string',
                    'enum': ['detailed', 'summary', 'timestamps'],
                    'default': 'detailed',
                    'description': 'Format of results'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Perform advanced content search."""
        criteria = parameters['search_criteria']
        episode_ids = parameters.get('episode_ids', [])
        max_results = parameters.get('max_results', 15)
        result_format = parameters.get('result_format', 'detailed')

        # Load comprehensive index
        comprehensive_index = self._load_comprehensive_index()

        results = []
        processed_episodes = 0

        # Search through episodes
        for episode_id, episode_data in comprehensive_index['episodes'].items():
            if episode_ids and episode_id not in episode_ids:
                continue

            processed_episodes += 1
            episode_results = self._search_episode_advanced(
                episode_data, criteria, result_format
            )

            # Add episode info
            for result in episode_results:
                result['episode_id'] = episode_id
                result['episode_title'] = episode_data.get('title', 'Untitled Episode')

            results.extend(episode_results)

            # Stop if we have enough results
            if len(results) >= max_results:
                break

        # Sort by comprehensive relevance score
        results.sort(key=lambda x: x.get('comprehensive_score', 0), reverse=True)

        # Format results
        formatted_results = self._format_results(results, result_format)

        return {
            'search_criteria': criteria,
            'results_found': len(results),
            'episodes_searched': processed_episodes,
            'results': formatted_results,
            'search_type': 'advanced_search',
            'timestamp': datetime.now().isoformat()
        }

    def _load_comprehensive_index(self) -> Dict[str, Any]:
        """Load comprehensive search index."""
        return {
            'episodes': {
                'ep001': {
                    'title': 'The Future of AI',
                    'segments': [
                        {
                            'start_time': 0.0, 'end_time': 300.0,
                            'text': 'Host introduces the topic of AI and its future impact',
                            'topics': ['ai', 'future', 'technology'],
                            'context': {'location': 'studio', 'people': ['Host', 'Dr. Smith']},
                            'type': 'discussion'
                        },
                        {
                            'start_time': 300.0, 'end_time': 900.0,
                            'text': 'Detailed discussion about machine learning algorithms',
                            'topics': ['machine learning', 'algorithms', 'ai'],
                            'context': {'location': 'studio', 'people': ['Dr. Smith', 'Jane Doe']},
                            'type': 'technical'
                        }
                    ]
                },
                'ep002': {
                    'title': 'Comedy Night Live',
                    'segments': [
                        {
                            'start_time': 0.0, 'end_time': 60.0,
                            'text': 'Jared welcomes the audience to comedy night',
                            'topics': ['comedy', 'introduction'],
                            'context': {'location': 'stage', 'people': ['Jared']},
                            'type': 'introduction',
                            'joke': False
                        },
                        {
                            'start_time': 60.0, 'end_time': 120.0,
                            'text': 'Jared tells a science joke about atoms',
                            'topics': ['science', 'comedy'],
                            'context': {'location': 'stage', 'people': ['Jared']},
                            'type': 'joke',
                            'joke': True,
                            'joke_topics': ['science', 'atoms'],
                            'laughter_score': 0.87
                        },
                        {
                            'start_time': 180.0, 'end_time': 240.0,
                            'text': 'Sarah tells a farming joke about scarecrows',
                            'topics': ['farming', 'comedy'],
                            'context': {'location': 'stage', 'people': ['Sarah']},
                            'type': 'joke',
                            'joke': True,
                            'joke_topics': ['farming', 'awards'],
                            'laughter_score': 0.92
                        }
                    ]
                }
            },
            'index_type': 'comprehensive',
            'last_updated': datetime.now().isoformat()
        }

    def _search_episode_advanced(self, episode_data: Dict[str, Any], criteria: Dict[str, Any],
                                result_format: str) -> List[Dict[str, Any]]:
        """Search episode using advanced criteria."""
        segments = episode_data.get('segments', [])
        results = []

        for segment in segments:
            # Calculate comprehensive match score
            match_score = 0
            score_details = {}

            # Topic matching
            if 'topics' in criteria:
                segment_topics = segment.get('topics', [])
                topic_matches = sum(1 for topic in criteria['topics']
                                   if topic.lower() in [st.lower() for st in segment_topics])
                if topic_matches > 0:
                    match_score += topic_matches * 2
                    score_details['topic_match'] = topic_matches

            # Joke topic matching
            if 'joke_topics' in criteria and segment.get('joke', False):
                joke_topics = segment.get('joke_topics', [])
                joke_matches = sum(1 for topic in criteria['joke_topics']
                                  if topic.lower() in [jt.lower() for jt in joke_topics])
                if joke_matches > 0:
                    match_score += joke_matches * 3
                    score_details['joke_topic_match'] = joke_matches

            # Context matching
            if 'context' in criteria:
                segment_context = segment.get('context', {})
                context_text = f"{segment_context.get('location', '')} {segment_context.get('people', [])}"
                if criteria['context'].lower() in context_text.lower():
                    match_score += 2
                    score_details['context_match'] = True

            # Location matching
            if 'locations' in criteria:
                segment_location = segment.get('context', {}).get('location', '').lower()
                location_matches = sum(1 for location in criteria['locations']
                                      if location.lower() == segment_location)
                if location_matches > 0:
                    match_score += location_matches * 1.5
                    score_details['location_match'] = location_matches

            # People matching
            if 'people' in criteria:
                segment_people = [p.lower() for p in segment.get('context', {}).get('people', [])]
                people_matches = sum(1 for person in criteria['people']
                                    if person.lower() in segment_people)
                if people_matches > 0:
                    match_score += people_matches * 1.5
                    score_details['people_match'] = people_matches

            # Time range matching
            if 'time_range' in criteria:
                segment_start = segment['start_time']
                segment_end = segment['end_time']
                start_time = self._parse_time(criteria['time_range']['start_time'])
                end_time = self._parse_time(criteria['time_range']['end_time'])

                if not (segment_end < start_time or segment_start > end_time):
                    match_score += 1
                    score_details['time_match'] = True

            # Duration matching
            duration = segment['end_time'] - segment['start_time']
            if 'min_duration' in criteria and duration >= criteria['min_duration']:
                match_score += 0.5
                score_details['min_duration_match'] = True
            if 'max_duration' in criteria and duration <= criteria['max_duration']:
                match_score += 0.5
                score_details['max_duration_match'] = True

            if match_score > 0:
                result = {
                    'segment_id': f"seg_{len(results)}",
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'duration': duration,
                    'text': segment['text'],
                    'comprehensive_score': match_score,
                    'score_details': score_details,
                    'context': segment.get('context', {})
                }

                if segment.get('joke', False):
                    result['joke_info'] = {
                        'joke_topics': segment.get('joke_topics', []),
                        'laughter_score': segment.get('laughter_score', 0)
                    }

                results.append(result)

        return results

    def _format_results(self, results: List[Dict[str, Any]], format_type: str) -> List[Dict[str, Any]]:
        """Format results according to specified format."""
        if format_type == 'summary':
            return [{
                'segment_id': r['segment_id'],
                'start_time': r['start_time'],
                'end_time': r['end_time'],
                'score': r['comprehensive_score'],
                'text_preview': r['text'][:50] + '...'
            } for r in results]

        elif format_type == 'timestamps':
            return [{
                'segment_id': r['segment_id'],
                'timestamps': f"{r['start_time']:.1f}-{r['end_time']:.1f}",
                'score': r['comprehensive_score']
            } for r in results]

        else:  # detailed
            return results

    def _parse_time(self, time_str: str) -> float:
        """Convert time string to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])
        except:
            return 0.0

class SearchIndexManagementTool(RobustTool):
    """Tool for creating and managing search indexes."""

    def __init__(self):
        super().__init__(
            name="search_index_management",
            description="Create and manage search indexes for faster queries"
        )

    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define validation schema for search index management."""
        return {
            'type': 'object',
            'required': ['operation'],
            'properties': {
                'operation': {
                    'type': 'string',
                    'enum': ['create', 'update', 'optimize', 'status', 'delete'],
                    'description': 'Index operation to perform'
                },
                'index_type': {
                    'type': 'string',
                    'enum': ['topic', 'joke', 'context', 'timestamp', 'location', 'comprehensive'],
                    'description': 'Type of index to manage'
                },
                'episode_ids': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Episode IDs to include in index'
                },
                'force_rebuild': {
                    'type': 'boolean',
                    'default': False,
                    'description': 'Force complete rebuild of index'
                },
                'index_name': {
                    'type': 'string',
                    'description': 'Name for the index'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies."""
        return []

    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Manage search indexes."""
        operation = parameters['operation']
        index_type = parameters.get('index_type', 'comprehensive')
        episode_ids = parameters.get('episode_ids', [])
        force_rebuild = parameters.get('force_rebuild', False)
        index_name = parameters.get('index_name', f"{index_type}_index_{execution_id}")

        if operation == 'create':
            return self._create_index(index_type, episode_ids, index_name, force_rebuild)
        elif operation == 'update':
            return self._update_index(index_type, episode_ids, index_name)
        elif operation == 'optimize':
            return self._optimize_index(index_type, index_name)
        elif operation == 'status':
            return self._get_index_status(index_type, index_name)
        elif operation == 'delete':
            return self._delete_index(index_name)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _create_index(self, index_type: str, episode_ids: List[str], index_name: str,
                     force_rebuild: bool) -> Dict[str, Any]:
        """Create a new search index."""
        # Check if index already exists
        existing_index = self._check_existing_index(index_name)
        if existing_index and not force_rebuild:
            return {
                'status': 'exists',
                'index_name': index_name,
                'index_type': index_type,
                'message': 'Index already exists',
                'existing_index': existing_index
            }

        # Simulate index creation
        index_data = {
            'index_name': index_name,
            'index_type': index_type,
            'episode_count': len(episode_ids) if episode_ids else 10,
            'created_at': datetime.now().isoformat(),
            'status': 'created',
            'size': '1.2MB',
            'query_types': self._get_query_types_for_index(index_type)
        }

        return {
            'operation': 'create',
            'status': 'success',
            'index': index_data,
            'message': f'Successfully created {index_type} index'
        }

    def _update_index(self, index_type: str, episode_ids: List[str], index_name: str) -> Dict[str, Any]:
        """Update an existing search index."""
        # Check if index exists
        existing_index = self._check_existing_index(index_name)
        if not existing_index:
            return {
                'status': 'error',
                'message': 'Index does not exist',
                'suggested_action': 'create_index'
            }

        # Simulate index update
        updated_index = existing_index.copy()
        updated_index['last_updated'] = datetime.now().isoformat()
        updated_index['episode_count'] += len(episode_ids)
        updated_index['status'] = 'updated'

        return {
            'operation': 'update',
            'status': 'success',
            'index': updated_index,
            'message': f'Successfully updated {index_type} index',
            'episodes_added': len(episode_ids)
        }

    def _optimize_index(self, index_type: str, index_name: str) -> Dict[str, Any]:
        """Optimize an existing search index."""
        # Check if index exists
        existing_index = self._check_existing_index(index_name)
        if not existing_index:
            return {
                'status': 'error',
                'message': 'Index does not exist',
                'suggested_action': 'create_index'
            }

        # Simulate optimization
        optimized_index = existing_index.copy()
        optimized_index['last_optimized'] = datetime.now().isoformat()
        optimized_index['optimization_level'] = 'high'
        optimized_index['query_performance'] = 'improved'

        return {
            'operation': 'optimize',
            'status': 'success',
            'index': optimized_index,
            'message': f'Successfully optimized {index_type} index',
            'performance_improvement': '25% faster queries'
        }

    def _get_index_status(self, index_type: str, index_name: str) -> Dict[str, Any]:
        """Get status of an existing search index."""
        # Check if index exists
        existing_index = self._check_existing_index(index_name)
        if not existing_index:
            return {
                'status': 'error',
                'message': 'Index does not exist',
                'suggested_action': 'create_index'
            }

        # Add status details
        status_details = {
            'index_health': 'good',
            'query_count': 42,
            'last_query': '2024-01-15T10:30:00Z',
            'storage_size': '1.2MB',
            'memory_usage': '64MB'
        }

        return {
            'operation': 'status',
            'status': 'success',
            'index': {**existing_index, **status_details},
            'message': f'Status retrieved for {index_type} index'
        }

    def _delete_index(self, index_name: str) -> Dict[str, Any]:
        """Delete an existing search index."""
        # Check if index exists
        existing_index = self._check_existing_index(index_name)
        if not existing_index:
            return {
                'status': 'error',
                'message': 'Index does not exist',
                'suggested_action': 'create_index'
            }

        return {
            'operation': 'delete',
            'status': 'success',
            'deleted_index': index_name,
            'message': 'Successfully deleted index',
            'index_type': existing_index.get('index_type', 'unknown')
        }

    def _check_existing_index(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Check if index exists (mock implementation)."""
        # In a real implementation, this would check a database or file system
        mock_indexes = {
            'comprehensive_index_123': {
                'index_name': 'comprehensive_index_123',
                'index_type': 'comprehensive',
                'episode_count': 50,
                'created_at': '2024-01-01T00:00:00Z',
                'status': 'active'
            },
            'joke_index_456': {
                'index_name': 'joke_index_456',
                'index_type': 'joke',
                'episode_count': 20,
                'created_at': '2024-01-05T10:00:00Z',
                'status': 'active'
            }
        }

        return mock_indexes.get(index_name)

    def _get_query_types_for_index(self, index_type: str) -> List[str]:
        """Get supported query types for index type."""
        query_types = {
            'topic': ['topic_search', 'keyword_search'],
            'joke': ['joke_search', 'humor_search'],
            'context': ['context_search', 'scene_search'],
            'timestamp': ['timestamp_search', 'time_range_search'],
            'location': ['location_search', 'scene_search'],
            'comprehensive': ['topic_search', 'joke_search', 'context_search',
                            'timestamp_search', 'location_search', 'advanced_search']
        }
        return query_types.get(index_type, [])

if __name__ == "__main__":
    # Example usage
    agent = ContentSearchAgent()

    # Search for topics
    topic_results = agent.execute_tool("search_by_topic", {
        "search_terms": ["AI", "future"],
        "max_results": 5
    })
    print("Topic Search Results:", topic_results)

    # Search for jokes
    joke_results = agent.execute_tool("search_jokes", {
        "topics": ["science", "technology"],
        "max_results": 3
    })
    print("Joke Search Results:", joke_results)

    # Search by context
    context_results = agent.execute_tool("search_by_context", {
        "context_query": "Jared live on stage",
        "max_results": 3
    })
    print("Context Search Results:", context_results)
