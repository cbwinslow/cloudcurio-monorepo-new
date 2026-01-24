"""
Content Scheduling Tool - Multi-platform content scheduling for podcast production.

This tool provides content scheduling functionality including calendar management,
platform posting, conflict detection, and optimal timing recommendations.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from .base_tool import BaseTool
from .error_handling import SchedulingError, SchedulingConflictError, SchedulingValidationError


class ContentSchedulingTool(BaseTool):
    """
    Comprehensive content scheduling tool for multi-platform podcast distribution.
    
    Capabilities:
    - Content calendar management
    - Multi-platform scheduling
    - Conflict detection
    - Optimal timing recommendations
    - Schedule optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the Content Scheduling Tool.
        
        Args:
            config: Configuration dictionary containing:
                - supported_platforms: List of supported platforms
                - max_posts_per_day: Maximum posts per day (default: 10)
                - min_interval_minutes: Minimum interval between posts (default: 60)
                - working_hours_start: Working hours start (default: 9)
                - working_hours_end: Working hours end (default: 18)
                - timezone: Timezone for scheduling (default: 'UTC')
            **kwargs: Additional configuration options
        """
        # Set configuration attributes BEFORE calling super().__init__()
        # This is needed because _validate_tool_config() is called during parent initialization
        if config is None:
            config = {}
        
        self.supported_platforms = config.get('supported_platforms', [
            'twitter', 'instagram', 'tiktok', 'youtube', 'linkedin', 'facebook'
        ])
        self.max_posts_per_day = config.get('max_posts_per_day', 10)
        self.min_interval_minutes = config.get('min_interval_minutes', 60)
        self.working_hours_start = config.get('working_hours_start', 9)
        self.working_hours_end = config.get('working_hours_end', 18)
        self.timezone = config.get('timezone', 'UTC')
        
        # Initialize schedule storage
        self.schedule = {}  # date -> list of scheduled posts
        
        # Now call parent init
        super().__init__(config, **kwargs)
        
        self.logger.info(f"ContentSchedulingTool initialized with platforms: {self.supported_platforms}")
    
    def _validate_tool_config(self) -> None:
        """Validate content scheduling tool-specific configuration."""
        if self.max_posts_per_day <= 0:
            raise SchedulingError(
                "max_posts_per_day must be greater than 0",
                context={'max_posts_per_day': self.max_posts_per_day},
                recovery_suggestions=["Set max_posts_per_day to a positive value"]
            )
        
        if self.min_interval_minutes <= 0:
            raise SchedulingError(
                "min_interval_minutes must be greater than 0",
                context={'min_interval_minutes': self.min_interval_minutes},
                recovery_suggestions=["Set min_interval_minutes to a positive value"]
            )
        
        if not 0 <= self.working_hours_start < 24:
            raise SchedulingError(
                "working_hours_start must be between 0 and 23",
                context={'working_hours_start': self.working_hours_start},
                recovery_suggestions=["Set working_hours_start to a valid hour (0-23)"]
            )
        
        if not 0 <= self.working_hours_end <= 24:
            raise SchedulingError(
                "working_hours_end must be between 0 and 24",
                context={'working_hours_end': self.working_hours_end},
                recovery_suggestions=["Set working_hours_end to a valid hour (0-24)"]
            )
    
    def _validate_platform(self, platform: str) -> None:
        """Validate that platform is supported."""
        if platform not in self.supported_platforms:
            raise SchedulingValidationError(
                f"Unsupported platform: {platform}",
                context={'platform': platform, 'supported': self.supported_platforms},
                recovery_suggestions=[
                    f"Use one of: {', '.join(self.supported_platforms)}",
                    "Add platform to supported_platforms in configuration"
                ]
            )
    
    def _validate_datetime(self, dt_str: str) -> datetime:
        """Validate and parse datetime string."""
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt
        except ValueError:
            try:
                # Try common formats
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                return dt
            except ValueError:
                raise SchedulingValidationError(
                    f"Invalid datetime format: {dt_str}",
                    context={'datetime': dt_str},
                    recovery_suggestions=[
                        "Use ISO format: YYYY-MM-DDTHH:MM:SS",
                        "Use format: YYYY-MM-DD HH:MM:SS"
                    ]
                )
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute content scheduling operation.
        
        Args:
            operation: Operation to perform:
                - 'schedule': Schedule a new post
                - 'calendar': Generate content calendar
                - 'check_conflicts': Check for scheduling conflicts
                - 'optimize': Optimize posting schedule
                - 'cancel': Cancel a scheduled post
                - 'list': List scheduled posts
            **kwargs: Additional operation parameters
        
        Returns:
            Dictionary containing operation results
        
        Raises:
            SchedulingError: If scheduling operation fails
        """
        # Start performance monitoring
        self._start_performance_monitoring()
        
        try:
            self._log_operation('content_scheduling', {
                'operation': operation,
                'params': kwargs
            })
            
            # Perform operation based on type
            if operation == 'schedule':
                result = self._schedule_post(**kwargs)
            elif operation == 'calendar':
                result = self._generate_calendar(**kwargs)
            elif operation == 'check_conflicts':
                result = self._check_conflicts(**kwargs)
            elif operation == 'optimize':
                result = self._optimize_schedule(**kwargs)
            elif operation == 'cancel':
                result = self._cancel_post(**kwargs)
            elif operation == 'list':
                result = self._list_posts(**kwargs)
            else:
                raise SchedulingError(
                    f"Unknown operation: {operation}",
                    context={'operation': operation},
                    recovery_suggestions=[
                        "Use one of: 'schedule', 'calendar', 'check_conflicts', 'optimize', 'cancel', 'list'"
                    ]
                )
            
            # End performance monitoring
            self._end_performance_monitoring()
            
            # Add performance metrics to result
            result['performance'] = self.get_performance_metrics()
            
            return result
            
        except (SchedulingError, SchedulingConflictError, SchedulingValidationError):
            raise
        except Exception as e:
            self._handle_error(e)
            raise SchedulingError(
                f"Content scheduling failed: {str(e)}",
                context={'operation': operation},
                original_exception=e
            )
    
    def _schedule_post(self, **kwargs) -> Dict[str, Any]:
        """
        Schedule a new post.
        
        Args:
            **kwargs: Post parameters:
                - content: Post content text (required)
                - platforms: List of platforms to post to (required)
                - schedule_time: When to post (ISO format) (required)
                - media_paths: List of media file paths (optional)
                - tags: List of hashtags (optional)
        
        Returns:
            Dictionary with scheduling results
        """
        self.logger.info("Scheduling new post")
        
        # Validate required parameters
        content = kwargs.get('content')
        platforms = kwargs.get('platforms', [])
        schedule_time_str = kwargs.get('schedule_time')
        
        if not content:
            raise SchedulingValidationError(
                "content parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide post content text"]
            )
        
        if not platforms:
            raise SchedulingValidationError(
                "platforms parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide list of target platforms"]
            )
        
        if not schedule_time_str:
            raise SchedulingValidationError(
                "schedule_time parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide schedule time in ISO format"]
            )
        
        # Validate platforms
        for platform in platforms:
            self._validate_platform(platform)
        
        # Parse and validate schedule time
        schedule_time = self._validate_datetime(schedule_time_str)
        
        # Check if time is in the past
        if schedule_time < datetime.now():
            raise SchedulingValidationError(
                "Cannot schedule posts in the past",
                context={'schedule_time': schedule_time_str},
                recovery_suggestions=["Provide a future datetime"]
            )
        
        # Check for conflicts
        conflicts = self._find_conflicts(schedule_time, platforms)
        if conflicts:
            raise SchedulingConflictError(
                "Scheduling conflict detected",
                context={'conflicts': conflicts, 'schedule_time': schedule_time_str},
                recovery_suggestions=[
                    "Choose a different time",
                    "Use optimize operation to find optimal time"
                ]
            )
        
        # Create post entry
        post_id = self._generate_post_id()
        post_entry = {
            'post_id': post_id,
            'content': content,
            'platforms': platforms,
            'schedule_time': schedule_time.isoformat(),
            'media_paths': kwargs.get('media_paths', []),
            'tags': kwargs.get('tags', []),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        # Add to schedule
        date_key = schedule_time.strftime('%Y-%m-%d')
        if date_key not in self.schedule:
            self.schedule[date_key] = []
        self.schedule[date_key].append(post_entry)
        
        return {
            'status': 'success',
            'operation': 'schedule',
            'post_id': post_id,
            'post_entry': post_entry,
            'conflicts': [],
            'recommendation': self._get_posting_recommendations(schedule_time, platforms)
        }
    
    def _generate_calendar(self, **kwargs) -> Dict[str, Any]:
        """
        Generate content calendar for specified date range.
        
        Args:
            **kwargs: Calendar parameters:
                - start_date: Start date (YYYY-MM-DD) (required)
                - end_date: End date (YYYY-MM-DD) (required)
                - platforms: Filter by platforms (optional)
                - content_types: Types of content to include (optional)
        
        Returns:
            Dictionary with calendar data
        """
        self.logger.info("Generating content calendar")
        
        start_date_str = kwargs.get('start_date')
        end_date_str = kwargs.get('end_date')
        
        if not start_date_str or not end_date_str:
            raise SchedulingValidationError(
                "start_date and end_date are required",
                context=kwargs,
                recovery_suggestions=["Provide start_date and end_date in YYYY-MM-DD format"]
            )
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError as e:
            raise SchedulingValidationError(
                f"Invalid date format: {str(e)}",
                context={'start_date': start_date_str, 'end_date': end_date_str},
                recovery_suggestions=["Use YYYY-MM-DD format"]
            )
        
        if start_date > end_date:
            raise SchedulingValidationError(
                "start_date must be before end_date",
                context={'start_date': start_date_str, 'end_date': end_date_str},
                recovery_suggestions=["Swap start_date and end_date"]
            )
        
        # Generate calendar
        calendar_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            posts = self.schedule.get(date_key, [])
            
            # Filter by platforms if specified
            platforms_filter = kwargs.get('platforms')
            if platforms_filter:
                posts = [p for p in posts if any(plat in p['platforms'] for plat in platforms_filter)]
            
            calendar_data[date_key] = {
                'date': date_key,
                'posts': posts,
                'post_count': len(posts),
                'capacity': self.max_posts_per_day - len(posts),
                'recommended_times': self._get_optimal_times(current_date)
            }
            
            current_date += timedelta(days=1)
        
        return {
            'status': 'success',
            'operation': 'calendar',
            'start_date': start_date_str,
            'end_date': end_date_str,
            'calendar': calendar_data,
            'total_posts': sum(day['post_count'] for day in calendar_data.values())
        }
    
    def _check_conflicts(self, **kwargs) -> Dict[str, Any]:
        """
        Check for scheduling conflicts.
        
        Args:
            **kwargs: Conflict check parameters:
                - schedule_time: Time to check (ISO format) (required)
                - platforms: Platforms to check (required)
        
        Returns:
            Dictionary with conflict information
        """
        self.logger.info("Checking for conflicts")
        
        schedule_time_str = kwargs.get('schedule_time')
        platforms = kwargs.get('platforms', [])
        
        if not schedule_time_str:
            raise SchedulingValidationError(
                "schedule_time parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide schedule time to check"]
            )
        
        schedule_time = self._validate_datetime(schedule_time_str)
        
        # Find conflicts
        conflicts = self._find_conflicts(schedule_time, platforms)
        
        return {
            'status': 'success',
            'operation': 'check_conflicts',
            'schedule_time': schedule_time_str,
            'platforms': platforms,
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts,
            'alternative_times': self._suggest_alternative_times(schedule_time, platforms) if conflicts else []
        }
    
    def _optimize_schedule(self, **kwargs) -> Dict[str, Any]:
        """
        Optimize posting schedule for maximum engagement.
        
        Args:
            **kwargs: Optimization parameters:
                - date: Date to optimize (YYYY-MM-DD) (required)
                - platforms: Platforms to optimize for (optional)
        
        Returns:
            Dictionary with optimization results
        """
        self.logger.info("Optimizing schedule")
        
        date_str = kwargs.get('date')
        if not date_str:
            raise SchedulingValidationError(
                "date parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide date in YYYY-MM-DD format"]
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise SchedulingValidationError(
                f"Invalid date format: {date_str}",
                context={'date': date_str},
                recovery_suggestions=["Use YYYY-MM-DD format"]
            )
        
        # Get current posts for the date
        date_key = date.strftime('%Y-%m-%d')
        current_posts = self.schedule.get(date_key, [])
        
        # Get optimal times
        optimal_times = self._get_optimal_times(date)
        
        # Create optimization suggestions
        suggestions = []
        for i, post in enumerate(current_posts):
            if i < len(optimal_times):
                suggested_time = optimal_times[i]
                current_time = datetime.fromisoformat(post['schedule_time'])
                
                if abs((suggested_time - current_time).total_seconds()) > 3600:  # More than 1 hour difference
                    suggestions.append({
                        'post_id': post['post_id'],
                        'current_time': post['schedule_time'],
                        'suggested_time': suggested_time.isoformat(),
                        'reason': 'Better engagement expected',
                        'improvement_estimate': '15-20%'
                    })
        
        return {
            'status': 'success',
            'operation': 'optimize',
            'date': date_str,
            'current_posts': len(current_posts),
            'optimal_times': [t.isoformat() for t in optimal_times],
            'suggestions': suggestions,
            'improvement_potential': f"{len(suggestions)} posts can be optimized"
        }
    
    def _cancel_post(self, **kwargs) -> Dict[str, Any]:
        """
        Cancel a scheduled post.
        
        Args:
            **kwargs: Cancellation parameters:
                - post_id: ID of post to cancel (required)
        
        Returns:
            Dictionary with cancellation results
        """
        self.logger.info("Canceling post")
        
        post_id = kwargs.get('post_id')
        if not post_id:
            raise SchedulingValidationError(
                "post_id parameter is required",
                context=kwargs,
                recovery_suggestions=["Provide post_id to cancel"]
            )
        
        # Find and remove post
        found = False
        for date_key, posts in self.schedule.items():
            for i, post in enumerate(posts):
                if post['post_id'] == post_id:
                    posts.pop(i)
                    found = True
                    break
            if found:
                break
        
        if not found:
            raise SchedulingError(
                f"Post not found: {post_id}",
                context={'post_id': post_id},
                recovery_suggestions=["Check post_id is correct", "Post may have already been canceled"]
            )
        
        return {
            'status': 'success',
            'operation': 'cancel',
            'post_id': post_id,
            'message': 'Post successfully canceled'
        }
    
    def _list_posts(self, **kwargs) -> Dict[str, Any]:
        """
        List scheduled posts.
        
        Args:
            **kwargs: List parameters:
                - date: Filter by date (YYYY-MM-DD) (optional)
                - platform: Filter by platform (optional)
                - status: Filter by status (optional)
        
        Returns:
            Dictionary with list of posts
        """
        self.logger.info("Listing posts")
        
        date_filter = kwargs.get('date')
        platform_filter = kwargs.get('platform')
        status_filter = kwargs.get('status', 'scheduled')
        
        posts = []
        
        if date_filter:
            # List posts for specific date
            posts = self.schedule.get(date_filter, [])
        else:
            # List all posts
            for date_posts in self.schedule.values():
                posts.extend(date_posts)
        
        # Apply filters
        if platform_filter:
            posts = [p for p in posts if platform_filter in p['platforms']]
        
        if status_filter:
            posts = [p for p in posts if p.get('status') == status_filter]
        
        return {
            'status': 'success',
            'operation': 'list',
            'filters': {'date': date_filter, 'platform': platform_filter, 'status': status_filter},
            'post_count': len(posts),
            'posts': posts
        }
    
    def _generate_post_id(self) -> str:
        """Generate unique post ID."""
        import uuid
        return f"post_{uuid.uuid4().hex[:12]}"
    
    def _find_conflicts(self, schedule_time: datetime, platforms: List[str]) -> List[Dict[str, Any]]:
        """Find scheduling conflicts."""
        conflicts = []
        date_key = schedule_time.strftime('%Y-%m-%d')
        posts_on_date = self.schedule.get(date_key, [])
        
        for post in posts_on_date:
            post_time = datetime.fromisoformat(post['schedule_time'])
            time_diff = abs((post_time - schedule_time).total_seconds() / 60)  # minutes
            
            # Check if too close in time
            if time_diff < self.min_interval_minutes:
                # Check if same platform
                common_platforms = set(platforms) & set(post['platforms'])
                if common_platforms:
                    conflicts.append({
                        'post_id': post['post_id'],
                        'time': post['schedule_time'],
                        'platforms': list(common_platforms),
                        'time_diff_minutes': time_diff
                    })
        
        # Check daily limit
        if len(posts_on_date) >= self.max_posts_per_day:
            conflicts.append({
                'type': 'daily_limit',
                'current_posts': len(posts_on_date),
                'limit': self.max_posts_per_day
            })
        
        return conflicts
    
    def _suggest_alternative_times(self, schedule_time: datetime, platforms: List[str]) -> List[str]:
        """Suggest alternative posting times."""
        alternatives = []
        
        # Try +/- 1, 2, 3 hours
        for hours in [1, -1, 2, -2, 3, -3]:
            alt_time = schedule_time + timedelta(hours=hours)
            conflicts = self._find_conflicts(alt_time, platforms)
            
            if not conflicts:
                alternatives.append(alt_time.isoformat())
            
            if len(alternatives) >= 3:
                break
        
        return alternatives
    
    def _get_optimal_times(self, date: datetime) -> List[datetime]:
        """Get optimal posting times for a date."""
        # Default optimal times based on research: 9am, 12pm, 3pm, 6pm
        optimal_hours = [9, 12, 15, 18]
        optimal_times = []
        
        for hour in optimal_hours:
            optimal_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            optimal_times.append(optimal_time)
        
        return optimal_times
    
    def _get_posting_recommendations(self, schedule_time: datetime, platforms: List[str]) -> Dict[str, Any]:
        """Get posting recommendations."""
        hour = schedule_time.hour
        
        # Check if within working hours
        is_optimal = self.working_hours_start <= hour < self.working_hours_end
        
        recommendations = {
            'is_optimal_time': is_optimal,
            'engagement_estimate': 'high' if is_optimal else 'medium',
            'tips': []
        }
        
        if not is_optimal:
            recommendations['tips'].append(
                f"Consider posting during working hours ({self.working_hours_start}:00-{self.working_hours_end}:00) for better engagement"
            )
        
        # Platform-specific tips
        if 'twitter' in platforms:
            recommendations['tips'].append("Twitter: Best times are 9am, 12pm, and 3pm")
        if 'instagram' in platforms:
            recommendations['tips'].append("Instagram: Best times are 11am, 2pm, and 7pm")
        if 'linkedin' in platforms:
            recommendations['tips'].append("LinkedIn: Best times are 7am, 12pm, and 5pm (workday)")
        
        return recommendations
