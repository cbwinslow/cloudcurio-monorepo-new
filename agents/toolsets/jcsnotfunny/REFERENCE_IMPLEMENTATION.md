# Robust Toolset Reference Implementation

## Overview

This document provides concrete, production-ready implementations of the robust toolset design principles. These examples demonstrate how to build tools that are reliable, informative, and decisive.

## Core Tool Base Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import traceback
import time
from datetime import datetime
import uuid
import logging
from enum import Enum

class ToolStatus(Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ToolResult:
    """Standardized tool execution result"""

    def __init__(self, status: ToolStatus, data: Dict = None,
                 error: Exception = None, warnings: List[str] = None):
        self.status = status
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.timestamp = datetime.now().isoformat()
        self.metrics = {}

    def add_metric(self, name: str, value: Any, unit: str = ""):
        """Add performance metric"""
        self.metrics[name] = {'value': value, 'unit': unit}

    def add_warning(self, warning: str):
        """Add warning message"""
        self.warnings.append(warning)

    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status in [ToolStatus.SUCCESS, ToolStatus.PARTIAL_SUCCESS]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = {
            'status': self.status.value,
            'data': self.data,
            'warnings': self.warnings,
            'metrics': self.metrics,
            'timestamp': self.timestamp
        }

        if self.error:
            result['error'] = {
                'type': self.error.__class__.__name__,
                'message': str(self.error),
                'stack_trace': traceback.format_exc()
            }

        return result

class RobustTool(ABC):
    """Base class for all robust tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.execution_id = None
        self.logger = self._setup_logger()
        self.retry_policy = self._default_retry_policy()
        self.fallback_strategies = self._define_fallback_strategies()

    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger(f"tool.{self.name}")
        logger.setLevel(logging.INFO)

        # Add multiple handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(f"logs/{self.name}.log")

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def _default_retry_policy(self) -> Dict:
        """Default retry policy configuration"""
        return {
            'max_attempts': 3,
            'backoff_strategy': 'exponential',
            'retryable_errors': ['TimeoutError', 'ConnectionError', 'ResourceTemporaryUnavailable'],
            'initial_delay': 1.0,
            'max_delay': 30.0
        }

    def _define_fallback_strategies(self) -> List[Dict]:
        """Define tool-specific fallback strategies"""
        return []

    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        return f"{self.name}-{uuid.uuid4().hex[:8]}-{int(time.time())}"

    def _log_execution_start(self, parameters: Dict):
        """Log tool execution start"""
        self.execution_id = self._generate_execution_id()

        log_data = {
            'execution_id': self.execution_id,
            'tool': self.name,
            'status': 'started',
            'parameters': self._sanitize_parameters(parameters),
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Execution started: {self.execution_id}")
        self.logger.debug(f"Parameters: {log_data['parameters']}")

    def _log_progress(self, percentage: float, message: str = ""):
        """Log execution progress"""
        log_data = {
            'execution_id': self.execution_id,
            'progress': percentage,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Progress: {percentage:.1f}% - {message}")

    def _log_execution_end(self, result: ToolResult):
        """Log tool execution completion"""
        log_data = {
            'execution_id': self.execution_id,
            'status': result.status.value,
            'duration': result.metrics.get('execution_time', 'unknown'),
            'warnings': len(result.warnings),
            'timestamp': datetime.now().isoformat()
        }

        if result.is_successful():
            self.logger.info(f"Execution completed successfully: {self.execution_id}")
        else:
            self.logger.error(f"Execution failed: {self.execution_id}")

        self.logger.debug(f"Execution metrics: {result.metrics}")

    def _sanitize_parameters(self, parameters: Dict) -> Dict:
        """Sanitize parameters for logging"""
        sanitized = {}

        for key, value in parameters.items():
            if key.endswith('_password') or key.endswith('_token') or key.endswith('_secret'):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_parameters(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_parameters(item) if isinstance(item, dict) else '***LIST***'
                                 for item in value]
            else:
                sanitized[key] = f"<{value.__class__.__name__}>"

        return sanitized

    def _execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        attempt = 0
        last_error = None

        while attempt < self.retry_policy['max_attempts']:
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                self.logger.debug(f"Attempt {attempt + 1} succeeded in {duration:.2f}s")
                return result

            except Exception as e:
                last_error = e
                attempt += 1

                error_type = e.__class__.__name__

                # Check if error is retryable
                if error_type not in self.retry_policy['retryable_errors']:
                    self.logger.warning(f"Non-retryable error: {error_type}")
                    break

                # Calculate delay based on backoff strategy
                if self.retry_policy['backoff_strategy'] == 'exponential':
                    delay = min(
                        self.retry_policy['initial_delay'] * (2 ** (attempt - 1)),
                        self.retry_policy['max_delay']
                    )
                elif self.retry_policy['backoff_strategy'] == 'linear':
                    delay = min(
                        self.retry_policy['initial_delay'] * attempt,
                        self.retry_policy['max_delay']
                    )
                else:
                    delay = self.retry_policy['initial_delay']

                self.logger.warning(
                    f"Attempt {attempt} failed: {error_type} - {str(e)}. "
                    f"Retrying in {delay:.1f} seconds..."
                )

                time.sleep(delay)

        # If all retries failed
        self.logger.error(f"All {self.retry_policy['max_attempts']} attempts failed")
        raise RetryExhaustedError(
            f"Tool {self.name} failed after {self.retry_policy['max_attempts']} attempts",
            original_error=last_error
        ) from last_error

    def _apply_fallback_strategies(self, error: Exception, parameters: Dict) -> Optional[ToolResult]:
        """Apply fallback strategies when primary execution fails"""
        for strategy in self.fallback_strategies:
            try:
                # Check if strategy applies to this error
                if not strategy['condition'](error):
                    continue

                self.logger.info(f"Applying fallback strategy: {strategy['name']}")

                # Execute fallback action
                fallback_result = strategy['action'](error, parameters)

                if fallback_result and fallback_result.is_successful():
                    self.logger.info(f"Fallback strategy succeeded: {strategy['name']}")
                    return fallback_result
                else:
                    self.logger.warning(f"Fallback strategy failed: {strategy['name']}")

            except Exception as fallback_error:
                self.logger.error(
                    f"Fallback strategy error: {strategy['name']} - {str(fallback_error)}"
                )
                continue

        return None

    def _validate_parameters(self, parameters: Dict) -> Dict:
        """Validate input parameters"""
        validation_schema = self._get_validation_schema()

        if not validation_schema:
            return parameters

        # Check required parameters
        for required_param in validation_schema.get('required', []):
            if required_param not in parameters:
                raise ValidationError(
                    f"Missing required parameter: {required_param}"
                )

        # Validate parameter types and constraints
        for param_name, param_config in validation_schema.get('properties', {}).items():
            if param_name in parameters:
                self._validate_parameter(
                    param_name,
                    parameters[param_name],
                    param_config
                )

        # Apply default values
        for param_name, param_config in validation_schema.get('properties', {}).items():
            if param_name not in parameters and 'default' in param_config:
                parameters[param_name] = param_config['default']
                self.logger.debug(f"Applied default value for {param_name}")

        return parameters

    def _validate_parameter(self, name: str, value: Any, config: Dict):
        """Validate individual parameter"""
        # Type validation
        expected_type = config.get('type')
        if expected_type and not self._check_type(value, expected_type):
            raise ValidationError(
                f"Parameter '{name}' must be of type {expected_type}, got {type(value).__name__}"
            )

        # Constraint validation
        if 'constraints' in config:
            self._validate_constraints(name, value, config['constraints'])

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            'string': str,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'integer': int,
            'float': float
        }

        expected_types = type_mapping.get(expected_type, expected_type)

        if isinstance(expected_types, tuple):
            return isinstance(value, expected_types)
        else:
            return isinstance(value, expected_types)

    def _validate_constraints(self, name: str, value: Any, constraints: Dict):
        """Validate parameter constraints"""
        # Minimum/Maximum validation
        if 'min' in constraints and value < constraints['min']:
            raise ValidationError(
                f"Parameter '{name}' must be >= {constraints['min']}, got {value}"
            )

        if 'max' in constraints and value > constraints['max']:
            raise ValidationError(
                f"Parameter '{name}' must be <= {constraints['max']}, got {value}"
            )

        # Pattern validation
        if 'pattern' in constraints and isinstance(value, str):
            import re
            if not re.match(constraints['pattern'], value):
                raise ValidationError(
                    f"Parameter '{name}' must match pattern {constraints['pattern']}"
                )

        # Allowed values validation
        if 'allowed_values' in constraints:
            if value not in constraints['allowed_values']:
                raise ValidationError(
                    f"Parameter '{name}' must be one of {constraints['allowed_values']}, got {value}"
                )

    def _get_validation_schema(self) -> Optional[Dict]:
        """Get parameter validation schema (to be implemented by subclasses)"""
        return None

    def _perform_quality_assurance(self, result: Any) -> List[str]:
        """Perform quality assurance checks on tool output"""
        return []

    @abstractmethod
    def _execute_core_logic(self, parameters: Dict) -> Any:
        """Core tool execution logic (to be implemented by subclasses)"""
        pass

    def execute(self, parameters: Dict) -> ToolResult:
        """Execute tool with comprehensive safety measures"""
        result = ToolResult(ToolStatus.PENDING)

        try:
            # Start execution logging
            self._log_execution_start(parameters)
            result.add_metric('execution_start', datetime.now().isoformat())

            # Validate parameters
            validated_params = self._validate_parameters(parameters)

            # Execute core logic with retry
            start_time = time.time()
            core_result = self._execute_with_retry(
                self._execute_core_logic,
                validated_params
            )
            execution_time = time.time() - start_time

            # Perform quality assurance
            qa_warnings = self._perform_quality_assurance(core_result)
            for warning in qa_warnings:
                result.add_warning(warning)

            # Set success result
            result.status = ToolStatus.SUCCESS
            result.data = core_result
            result.add_metric('execution_time', execution_time, 'seconds')
            result.add_metric('execution_end', datetime.now().isoformat())

            return result

        except Exception as e:
            # Attempt fallback strategies
            fallback_result = self._apply_fallback_strategies(e, parameters)

            if fallback_result:
                # Partial success with fallback
                result.status = ToolStatus.PARTIAL_SUCCESS
                result.data = fallback_result.data
                result.add_metric('fallback_used', fallback_result.data.get('fallback_strategy'))

                # Merge warnings
                for warning in fallback_result.warnings:
                    result.add_warning(warning)

                return result
            else:
                # Complete failure
                result.status = ToolStatus.FAILED
                result.error = e
                result.add_metric('execution_time', time.time() - start_time, 'seconds')

                return result
        finally:
            # Log execution end
            self._log_execution_end(result)

class RetryExhaustedError(Exception):
    """Exception raised when all retry attempts are exhausted"""
    pass

class ValidationError(Exception):
    """Exception raised when parameter validation fails"""
    pass
```

## Concrete Tool Implementations

### 1. Robust Video Analysis Tool

```python
class VideoAnalysisTool(RobustTool):
    """
    Comprehensive video analysis with robust error handling
    """

    def __init__(self):
        super().__init__(
            name="video_analysis",
            description="Analyze video footage for speaker detection, engagement scoring, and technical quality"
        )

    def _get_validation_schema(self) -> Dict:
        return {
            'required': ['video_path', 'analysis_type'],
            'properties': {
                'video_path': {
                    'type': 'string',
                    'constraints': {
                        'pattern': r'\.(mp4|mov|avi)$'
                    }
                },
                'analysis_type': {
                    'type': 'string',
                    'constraints': {
                        'allowed_values': ['speaker_detection', 'engagement_scoring',
                                         'optimal_cut_points', 'technical_quality', 'all']
                    }
                },
                'confidence_threshold': {
                    'type': 'number',
                    'constraints': {
                        'min': 0.1,
                        'max': 1.0
                    },
                    'default': 0.75
                },
                'output_format': {
                    'type': 'string',
                    'constraints': {
                        'allowed_values': ['json', 'xml', 'csv']
                    },
                    'default': 'json'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict]:
        return [
            {
                'name': 'file_repair_attempt',
                'condition': lambda e: isinstance(e, FileCorruptError),
                'action': self._attempt_file_repair
            },
            {
                'name': 'reduce_quality',
                'condition': lambda e: isinstance(e, MemoryError),
                'action': self._reduce_quality_and_retry
            },
            {
                'name': 'partial_analysis',
                'condition': lambda e: isinstance(e, ProcessingTimeout),
                'action': self._perform_partial_analysis
            }
        ]

    def _attempt_file_repair(self, error: Exception, parameters: Dict) -> ToolResult:
        """Attempt to repair corrupt video file"""
        try:
            self.logger.info("Attempting file repair...")

            # Use ffmpeg to attempt repair
            import subprocess
            repaired_path = parameters['video_path'] + ".repaired"

            cmd = [
                'ffmpeg', '-err_detect', 'ignore_err',
                '-i', parameters['video_path'],
                '-c', 'copy',
                repaired_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info("File repair successful")

                # Retry with repaired file
                parameters['video_path'] = repaired_path
                core_result = self._execute_core_logic(parameters)

                result = ToolResult(ToolStatus.PARTIAL_SUCCESS, core_result)
                result.add_warning("Analysis performed on repaired video file")
                result.data['repaired_file'] = repaired_path

                return result
            else:
                self.logger.warning("File repair failed")
                return None

        except Exception as e:
            self.logger.error(f"File repair error: {str(e)}")
            return None

    def _reduce_quality_and_retry(self, error: Exception, parameters: Dict) -> ToolResult:
        """Reduce video quality to conserve memory"""
        try:
            self.logger.info("Reducing video quality for memory conservation")

            # Create lower quality version
            import subprocess
            low_quality_path = parameters['video_path'] + ".lowres"

            cmd = [
                'ffmpeg', '-i', parameters['video_path'],
                '-vf', 'scale=640:-1',
                '-crf', '28',
                low_quality_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                parameters['video_path'] = low_quality_path
                core_result = self._execute_core_logic(parameters)

                result = ToolResult(ToolStatus.PARTIAL_SUCCESS, core_result)
                result.add_warning("Analysis performed on reduced quality video")
                result.data['quality_reduction'] = 'applied'

                return result
            else:
                return None

        except Exception as e:
            self.logger.error(f"Quality reduction failed: {str(e)}")
            return None

    def _perform_partial_analysis(self, error: Exception, parameters: Dict) -> ToolResult:
        """Perform partial analysis when full analysis times out"""
        try:
            self.logger.info("Performing partial analysis due to timeout")

            # Analyze only first 5 minutes
            parameters['analysis_duration'] = 300  # 5 minutes in seconds

            core_result = self._execute_core_logic(parameters)

            result = ToolResult(ToolStatus.PARTIAL_SUCCESS, core_result)
            result.add_warning("Partial analysis - only first 5 minutes processed")
            result.data['partial_analysis'] = True
            result.data['analyzed_duration'] = 300

            return result

        except Exception as e:
            self.logger.error(f"Partial analysis failed: {str(e)}")
            return None

    def _execute_core_logic(self, parameters: Dict) -> Dict:
        """Core video analysis implementation"""
        import subprocess
        import json
        import os

        analysis_results = {
            'video_path': parameters['video_path'],
            'analysis_type': parameters['analysis_type'],
            'timestamp': datetime.now().isoformat()
        }

        # Step 1: Get video technical information
        self._log_progress(10, "Analyzing technical properties")

        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams',
                parameters['video_path']
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                analysis_results['technical_info'] = json.loads(result.stdout)
            else:
                raise VideoAnalysisError("Failed to get technical information")

        except Exception as e:
            self.logger.warning(f"Technical analysis failed: {str(e)}")
            analysis_results['technical_info'] = {'error': str(e)}

        # Step 2: Perform requested analysis types
        if parameters['analysis_type'] in ['speaker_detection', 'all']:
            self._log_progress(30, "Detecting speakers")
            analysis_results['speakers'] = self._detect_speakers(parameters)

        if parameters['analysis_type'] in ['engagement_scoring', 'all']:
            self._log_progress(60, "Scoring engagement")
            analysis_results['engagement'] = self._score_engagement(parameters)

        if parameters['analysis_type'] in ['optimal_cut_points', 'all']:
            self._log_progress(80, "Finding optimal cut points")
            analysis_results['cut_points'] = self._find_cut_points(parameters)

        # Step 3: Quality assurance
        self._log_progress(90, "Performing quality checks")
        analysis_results['quality_metrics'] = self._calculate_quality_metrics(analysis_results)

        return analysis_results

    def _detect_speakers(self, parameters: Dict) -> List[Dict]:
        """Detect speakers in video using AI"""
        # This would integrate with actual speaker detection AI
        # For this example, we'll simulate the process

        speakers = []

        # Simulate detecting 2-3 speakers
        import random
        speaker_count = random.randint(2, 3)

        for i in range(speaker_count):
            speakers.append({
                'speaker_id': f"speaker_{i+1}",
                'first_detected': f"{random.randint(10, 120)}s",
                'last_detected': f"{random.randint(180, 600)}s",
                'total_duration': f"{random.randint(60, 300)}s",
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'dominant': i == 0  # First speaker is usually dominant
            })

        return speakers

    def _score_engagement(self, parameters: Dict) -> Dict:
        """Score video engagement potential"""
        # Simulate engagement scoring
        import random

        return {
            'overall_score': round(random.uniform(65, 95), 1),
            'visual_engagement': round(random.uniform(70, 90), 1),
            'audio_clarity': round(random.uniform(75, 95), 1),
            'pacing_score': round(random.uniform(60, 85), 1),
            'recommended_platforms': random.sample(
                ['youtube', 'tiktok', 'instagram', 'facebook'],
                k=random.randint(2, 3)
            )
        }

    def _find_cut_points(self, parameters: Dict) -> List[Dict]:
        """Find optimal cut points for editing"""
        # Simulate finding cut points
        import random

        cut_points = []
        current_time = 30  # Start at 30 seconds

        while current_time < 600:  # Up to 10 minutes
            cut_points.append({
                'time': f"{current_time}s",
                'type': random.choice(['speaker_change', 'topic_change', 'natural_pause']),
                'confidence': round(random.uniform(0.7, 0.9), 2),
                'importance': round(random.uniform(0.5, 1.0), 2)
            })

            # Next cut point in 45-120 seconds
            current_time += random.randint(45, 120)

        return cut_points

    def _calculate_quality_metrics(self, analysis_results: Dict) -> Dict:
        """Calculate overall quality metrics"""
        metrics = {
            'completeness': 1.0,
            'confidence_score': 0.85,
            'data_quality': 'high'
        }

        # Adjust based on what analysis was performed
        if 'technical_info' in analysis_results and 'error' in analysis_results['technical_info']:
            metrics['completeness'] = 0.7
            metrics['confidence_score'] = 0.6
            metrics['data_quality'] = 'medium'

        return metrics

    def _perform_quality_assurance(self, result: Dict) -> List[str]:
        """Perform quality assurance checks"""
        warnings = []

        # Check if technical analysis failed
        if 'technical_info' in result and 'error' in result['technical_info']:
            warnings.append("Technical analysis incomplete - some metrics may be missing")

        # Check speaker detection confidence
        if 'speakers' in result:
            avg_confidence = sum(s['confidence'] for s in result['speakers']) / len(result['speakers'])
            if avg_confidence < 0.75:
                warnings.append(f"Low speaker detection confidence: {avg_confidence:.2f}")

        # Check engagement score
        if 'engagement' in result and result['engagement']['overall_score'] < 70:
            warnings.append(f"Low engagement score: {result['engagement']['overall_score']}")

        return warnings

class VideoAnalysisError(Exception):
    """Custom error for video analysis issues"""
    pass

class FileCorruptError(Exception):
    """Error for corrupt video files"""
    pass
```

### 2. Reliable Social Media Scheduler

```python
class SocialMediaScheduler(RobustTool):
    """
    Robust social media scheduling with platform-specific handling
    """

    def __init__(self):
        super().__init__(
            name="schedule_post",
            description="Schedule posts across multiple social media platforms with comprehensive error handling"
        )

        # Platform handlers
        self.platform_handlers = {
            'twitter': TwitterPlatformHandler(),
            'instagram': InstagramPlatformHandler(),
            'tiktok': TikTokPlatformHandler(),
            'youtube': YouTubePlatformHandler(),
            'linkedin': LinkedInPlatformHandler()
        }

    def _get_validation_schema(self) -> Dict:
        return {
            'required': ['content', 'platforms'],
            'properties': {
                'content': {
                    'type': 'object',
                    'properties': {
                        'text': {'type': 'string', 'required': True},
                        'media': {'type': 'array'},
                        'hashtags': {'type': 'array'},
                        'links': {'type': 'array'}
                    }
                },
                'platforms': {
                    'type': 'array',
                    'constraints': {
                        'min_length': 1,
                        'allowed_values': ['twitter', 'instagram', 'tiktok', 'youtube', 'linkedin', 'facebook']
                    }
                },
                'publish_time': {
                    'type': 'string',
                    'constraints': {
                        'pattern': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
                    }
                },
                'timezone': {
                    'type': 'string',
                    'default': 'UTC'
                },
                'optimization_strategy': {
                    'type': 'string',
                    'constraints': {
                        'allowed_values': ['engagement', 'reach', 'conversion', 'balanced']
                    },
                    'default': 'balanced'
                }
            }
        }

    def _define_fallback_strategies(self) -> List[Dict]:
        return [
            {
                'name': 'rate_limit_handling',
                'condition': lambda e: self._is_rate_limit_error(e),
                'action': self._handle_rate_limit_error
            },
            {
                'name': 'authentication_refresh',
                'condition': lambda e: self._is_authentication_error(e),
                'action': self._refresh_authentication_and_retry
            },
            {
                'name': 'content_adaptation',
                'condition': lambda e: self._is_content_validation_error(e),
                'action': self._adapt_content_and_retry
            },
            {
                'name': 'platform_fallback',
                'condition': lambda e: self._is_platform_unavailable_error(e),
                'action': self._use_alternative_platforms
            }
        ]

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is related to rate limiting"""
        error_message = str(error).lower()
        return ('rate limit' in error_message or
                'too many requests' in error_message or
                '429' in error_message)

    def _is_authentication_error(self, error: Exception) -> bool:
        """Check if error is related to authentication"""
        error_message = str(error).lower()
        return ('authentication' in error_message or
                'unauthorized' in error_message or
                '401' in error_message or
                'token expired' in error_message)

    def _is_content_validation_error(self, error: Exception) -> bool:
        """Check if error is related to content validation"""
        error_message = str(error).lower()
        return ('validation' in error_message or
                'invalid content' in error_message or
                'policy violation' in error_message)

    def _is_platform_unavailable_error(self, error: Exception) -> bool:
        """Check if error indicates platform unavailability"""
        error_message = str(error).lower()
        return ('service unavailable' in error_message or
                '503' in error_message or
                'maintenance' in error_message)

    def _handle_rate_limit_error(self, error: Exception, parameters: Dict) -> ToolResult:
        """Handle rate limit errors with intelligent retry"""
        try:
            self.logger.info("Handling rate limit error")

            # Extract retry-after information if available
            retry_after = self._extract_retry_after(error)

            if retry_after:
                self.logger.info(f"Waiting for rate limit reset: {retry_after} seconds")
                time.sleep(retry_after)

                # Retry the operation
                return self._execute_core_logic(parameters)
            else:
                # Use exponential backoff if no specific retry-after
                max_wait = 300  # 5 minutes
                wait_time = min(2 ** len(parameters.get('platforms', [1])), max_wait)

                self.logger.info(f"Rate limit encountered, waiting {wait_time} seconds")
                time.sleep(wait_time)

                return self._execute_core_logic(parameters)

        except Exception as e:
            self.logger.error(f"Rate limit handling failed: {str(e)}")
            return None

    def _extract_retry_after(self, error: Exception) -> Optional[int]:
        """Extract retry-after information from error"""
        error_message = str(error)

        # Look for common retry-after patterns
        import re

        # Pattern: "Retry after 60 seconds"
        match = re.search(r'Retry after (\d+) seconds', error_message)
        if match:
            return int(match.group(1))

        # Pattern: "Please wait 120s"
        match = re.search(r'Please wait (\d+)s', error_message)
        if match:
            return int(match.group(1))

        # Pattern: HTTP header style
        if hasattr(error, 'headers') and 'Retry-After' in error.headers:
            return int(error.headers['Retry-After'])

        return None

    def _refresh_authentication_and_retry(self, error: Exception, parameters: Dict) -> ToolResult:
        """Refresh authentication tokens and retry"""
        try:
            self.logger.info("Refreshing authentication tokens")

            # Refresh tokens for all platforms
            for platform in parameters['platforms']:
                handler = self.platform_handlers.get(platform)
                if handler:
                    handler.refresh_authentication()

            # Retry the operation
            return self._execute_core_logic(parameters)

        except Exception as e:
            self.logger.error(f"Authentication refresh failed: {str(e)}")
            return None

    def _adapt_content_and_retry(self, error: Exception, parameters: Dict) -> ToolResult:
        """Adapt content to meet platform requirements"""
        try:
            self.logger.info("Adapting content to meet platform requirements")

            # Analyze validation errors
            validation_errors = self._extract_validation_errors(error)

            # Apply content adaptations
            adapted_content = self._apply_content_adaptations(
                parameters['content'],
                validation_errors
            )

            # Update parameters with adapted content
            parameters['content'] = adapted_content
            parameters['content_adapted'] = True

            # Retry with adapted content
            return self._execute_core_logic(parameters)

        except Exception as e:
            self.logger.error(f"Content adaptation failed: {str(e)}")
            return None

    def _extract_validation_errors(self, error: Exception) -> List[Dict]:
        """Extract specific validation errors from exception"""
        error_message = str(error)
        errors = []

        # This would be more sophisticated in a real implementation
        # For now, we'll simulate extracting some common issues

        if 'too long' in error_message.lower():
            errors.append({
                'type': 'content_length',
                'message': 'Content exceeds maximum length',
                'suggestion': 'Shorten text content'
            })

        if 'invalid media format' in error_message.lower():
            errors.append({
                'type': 'media_format',
                'message': 'Media format not supported',
                'suggestion': 'Convert to supported format'
            })

        if 'inappropriate content' in error_message.lower():
            errors.append({
                'type': 'content_policy',
                'message': 'Content violates platform policies',
                'suggestion': 'Review and modify content'
            })

        return errors

    def _apply_content_adaptations(self, content: Dict, errors: List[Dict]) -> Dict:
        """Apply adaptations to content based on validation errors"""
        adapted_content = content.copy()
        adaptations_applied = []

        for error in errors:
            if error['type'] == 'content_length' and 'text' in adapted_content:
                # Truncate text to reasonable length
                max_length = 280  # Twitter's limit as a safe default
                if len(adapted_content['text']) > max_length:
                    adapted_content['text'] = adapted_content['text'][:max_length-3] + '...'
                    adaptations_applied.append('text_truncation')

            elif error['type'] == 'media_format' and 'media' in adapted_content:
                # Remove problematic media (in real implementation, we'd convert)
                adapted_content['media'] = []
                adaptations_applied.append('media_removal')

            elif error['type'] == 'content_policy':
                # Add disclaimer (in real implementation, we'd be more sophisticated)
                if 'text' in adapted_content:
                    adapted_content['text'] += "\n\n[Content adapted for platform compliance]"
                    adaptations_applied.append('policy_compliance')

        self.logger.info(f"Applied content adaptations: {', '.join(adaptations_applied)}")

        return adapted_content

    def _use_alternative_platforms(self, error: Exception, parameters: Dict) -> ToolResult:
        """Use alternative platforms when primary platforms are unavailable"""
        try:
            self.logger.info("Using alternative platforms due to unavailability")

            # Identify available platforms
            available_platforms = []
            unavailable_platforms = []

            for platform in parameters['platforms']:
                handler = self.platform_handlers.get(platform)
                if handler and handler.is_available():
                    available_platforms.append(platform)
                else:
                    unavailable_platforms.append(platform)

            if not available_platforms:
                self.logger.warning("No alternative platforms available")
                return None

            # Update parameters to use only available platforms
            original_platforms = parameters['platforms']
            parameters['platforms'] = available_platforms
            parameters['platform_fallback'] = True

            # Execute with available platforms
            result = self._execute_core_logic(parameters)

            # Add warnings about unavailable platforms
            for platform in unavailable_platforms:
                result.add_warning(f"Platform {platform} unavailable - post not scheduled")

            return result

        except Exception as e:
            self.logger.error(f"Alternative platform handling failed: {str(e)}")
            return None

    def _execute_core_logic(self, parameters: Dict) -> ToolResult:
        """Core scheduling logic"""
        result = ToolResult(ToolStatus.PENDING)
        platform_results = {}\n
        # Process each platform
        for i, platform in enumerate(parameters['platforms']):
            progress = (i + 1) / len(parameters['platforms']) * 100
            self._log_progress(progress, f"Processing {platform}")

            try:
                # Get platform handler
                handler = self.platform_handlers.get(platform)
                if not handler:
                    raise PlatformNotSupportedError(f"Platform {platform} is not supported")

                # Adapt content for platform
                platform_content = handler.adapt_content(parameters['content'])

                # Validate content
                validation_result = handler.validate_content(platform_content)
                if not validation_result['valid']:
                    raise ContentValidationError(
                        f"Content validation failed for {platform}",
                        validation_result['errors']
                    )

                # Schedule post
                schedule_result = handler.schedule_post(
                    platform_content,
                    parameters.get('publish_time'),
                    parameters.get('timezone')
                )

                platform_results[platform] = {
                    'status': 'success',
                    'post_id': schedule_result.get('post_id'),
                    'scheduled_time': schedule_result.get('scheduled_time'),
                    'validation_warnings': validation_result.get('warnings', [])
                }

            except Exception as e:
                platform_results[platform] = {
                    'status': 'failed',
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }

                # Log platform-specific error
                self.logger.error(f"Failed to schedule on {platform}: {str(e)}")

        # Determine overall status
        successful_platforms = [p for p, r in platform_results.items() if r['status'] == 'success']
        failed_platforms = [p for p, r in platform_results.items() if r['status'] == 'failed']

        if successful_platforms and not failed_platforms:
            result.status = ToolStatus.SUCCESS
        elif successful_platforms and failed_platforms:
            result.status = ToolStatus.PARTIAL_SUCCESS
        else:
            result.status = ToolStatus.FAILED

        result.data = {
            'platform_results': platform_results,
            'successful_platforms': successful_platforms,
            'failed_platforms': failed_platforms,
            'total_platforms': len(parameters['platforms'])
        }

        return result

    def _perform_quality_assurance(self, result: ToolResult) -> List[str]:
        """Perform quality assurance on scheduling results"""
        warnings = []

        if result.status == ToolStatus.PARTIAL_SUCCESS:
            platform_results = result.data.get('platform_results', {})

            for platform, platform_result in platform_results.items():
                if platform_result['status'] == 'failed':
                    warnings.append(f"Post failed on {platform}: {platform_result['error']}")
                elif platform_result.get('validation_warnings'):
                    for warning in platform_result['validation_warnings']:
                        warnings.append(f"{platform} - {warning}")

        # Check if content was adapted
        if getattr(self, '_content_adapted', False):
            warnings.append("Content was adapted to meet platform requirements")

        return warnings

# Platform Handler Base Class
class PlatformHandler(ABC):
    """Base class for platform-specific handlers"""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.auth_token = None
        self.api_client = None

    def is_available(self) -> bool:
        """Check if platform API is available"""
        try:
            # Simple availability check
            return self._check_api_health()
        except Exception:
            return False

    def _check_api_health(self) -> bool:
        """Check API health (to be implemented by subclasses)"""
        return True

    def refresh_authentication(self):
        """Refresh authentication tokens"""
        # To be implemented by subclasses
        pass

    def adapt_content(self, content: Dict) -> Dict:
        """Adapt content for specific platform"""
        # To be implemented by subclasses
        return content

    def validate_content(self, content: Dict) -> Dict:
        """Validate content meets platform requirements"""
        # To be implemented by subclasses
        return {'valid': True, 'warnings': []}

    def schedule_post(self, content: Dict, publish_time: str = None, timezone: str = 'UTC') -> Dict:
        """Schedule post on platform"""
        # To be implemented by subclasses
        pass

# Example Twitter Handler
class TwitterPlatformHandler(PlatformHandler):
    """Twitter-specific platform handler"""

    def __init__(self):
        super().__init__('twitter')
        self.max_text_length = 280
        self.supported_media_types = ['image', 'video', 'gif']

    def adapt_content(self, content: Dict) -> Dict:
        """Adapt content for Twitter"""
        adapted = content.copy()

        # Ensure text fits Twitter's character limit
        if 'text' in adapted and len(adapted['text']) > self.max_text_length:
            adapted['text'] = adapted['text'][:self.max_text_length-3] + '...'

        # Twitter-specific formatting
        if 'hashtags' in adapted:
            adapted['text'] = adapted['text'] + ' ' + ' '.join(adapted['hashtags'])

        return adapted

    def validate_content(self, content: Dict) -> Dict:
        """Validate content for Twitter"""
        errors = []
        warnings = []

        # Check text length
        if 'text' in content:
            text_length = len(content['text'])
            if text_length > self.max_text_length:
                errors.append(f"Text too long: {text_length}/{self.max_text_length}")
            elif text_length > self.max_text_length * 0.9:
                warnings.append(f"Text approaching limit: {text_length}/{self.max_text_length}")

        # Check media
        if 'media' in content:
            for media in content['media']:
                if media.get('type') not in self.supported_media_types:
                    errors.append(f"Unsupported media type: {media.get('type')}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def schedule_post(self, content: Dict, publish_time: str = None, timezone: str = 'UTC') -> Dict:
        """Schedule post on Twitter"""
        # This would integrate with actual Twitter API
        # For this example, we'll simulate the process

        import random
        import time

        # Simulate API call
        time.sleep(1)  # Simulate network delay

        if random.random() < 0.95:  # 95% success rate
            return {
                'post_id': f"twitter_{random.randint(1000000, 9999999)}",
                'scheduled_time': publish_time or datetime.now().isoformat(),
                'status': 'scheduled'
            }
        else:
            # Simulate occasional failure
            raise TwitterAPIError("Twitter API temporarily unavailable")

class TwitterAPIError(Exception):
    """Twitter API specific error"""
    pass

class PlatformNotSupportedError(Exception):
    """Error for unsupported platforms"""
    pass

class ContentValidationError(Exception):
    """Error for content validation failures"""
    pass
```

## Integration Example

### 1. Agent Integration

```python
class VideoEditorAgent:
    """
    Video editor agent with robust tool integration
    """

    def __init__(self):
        self.tools = {
            'video_analysis': VideoAnalysisTool(),
            'auto_cut': AutoCutTool(),  # Would be implemented similarly
            'create_short': ShortFormCreator(),  # Would be implemented similarly
            'add_overlays': OverlayTool()  # Would be implemented similarly
        }
        self.workflow_executor = WorkflowExecutor()

    def analyze_video(self, video_path: str, analysis_type: str = 'all') -> ToolResult:
        """Analyze video with comprehensive error handling"""
        try:
            tool = self.tools['video_analysis']
            parameters = {
                'video_path': video_path,
                'analysis_type': analysis_type,
                'confidence_threshold': 0.8
            }

            result = tool.execute(parameters)

            if result.is_successful():
                self._log_successful_analysis(result)
            else:
                self._handle_analysis_failure(result)

            return result

        except Exception as e:
            error_result = ToolResult(ToolStatus.FAILED, error=e)
            error_result.add_warning("Unexpected error in video analysis")
            return error_result

    def _log_successful_analysis(self, result: ToolResult):
        """Log successful analysis"""
        analysis_data = result.data

        # Extract key metrics
        speakers = len(analysis_data.get('speakers', []))
        engagement_score = analysis_data.get('engagement', {}).get('overall_score', 'N/A')
        cut_points = len(analysis_data.get('cut_points', []))

        log_message = (
            f"Video analysis completed successfully. "
            f"Detected {speakers} speakers, "
            f"Engagement score: {engagement_score}, "
            f"Found {cut_points} optimal cut points"
        )

        print(log_message)
        # In real implementation, this would use proper logging

    def _handle_analysis_failure(self, result: ToolResult):
        """Handle analysis failure with appropriate actions"""
        if result.status == ToolStatus.PARTIAL_SUCCESS:
            print(f"Partial analysis success: {result.warnings}")
        else:
            print(f"Video analysis failed: {str(result.error)}")

        # Additional error handling logic would go here
        # Such as notifying operators, triggering fallback workflows, etc.

    def execute_workflow(self, workflow_name: str, parameters: Dict) -> Dict:
        """Execute a complete workflow"""
        try:
            workflow = self._get_workflow_definition(workflow_name)
            results = {}

            for step in workflow['steps']:
                tool_name = step['tool']
                step_parameters = self._prepare_step_parameters(step, parameters, results)

                # Execute tool
                tool_result = self._execute_tool(tool_name, step_parameters)

                # Store results
                results[tool_name] = tool_result

                # Check if workflow should continue
                if not self._should_continue_workflow(step, tool_result):
                    break

            return {
                'status': 'completed',
                'workflow': workflow_name,
                'results': results
            }

        except Exception as e:
            return {
                'status': 'failed',
                'workflow': workflow_name,
                'error': str(e),
                'partial_results': results
            }

    def _execute_tool(self, tool_name: str, parameters: Dict) -> ToolResult:
        """Execute a tool with comprehensive monitoring"""
        if tool_name not in self.tools:
            raise ToolNotFoundError(f"Tool {tool_name} not available")

        tool = self.tools[tool_name]

        # Add execution monitoring
        start_time = time.time()

        try:
            result = tool.execute(parameters)

            # Log execution metrics
            execution_time = time.time() - start_time

            if result.is_successful():
                print(f"Tool {tool_name} executed successfully in {execution_time:.2f}s")
            else:
                print(f"Tool {tool_name} failed after {execution_time:.2f}s: {str(result.error)}")

            return result

        except Exception as e:
            error_result = ToolResult(ToolStatus.FAILED, error=e)
            error_result.add_warning(f"Unexpected error executing {tool_name}")
            return error_result

class ToolNotFoundError(Exception):
    """Error for missing tools"""
    pass
```

### 2. Cross-Agent Collaboration

```python
class ProductionOrchestrator:
    """
    Orchestrates collaboration between multiple agents
    """

    def __init__(self):
        self.agents = {
            'video_editor': VideoEditorAgent(),
            'audio_engineer': AudioEngineerAgent(),
            'social_media_manager': SocialMediaManagerAgent(),
            'content_distributor': ContentDistributorAgent()
        }

        self.collaboration_protocols = {
            'episode_production': self._execute_episode_production,
            'short_form_creation': self._execute_short_form_creation,
            'tour_promotion': self._execute_tour_promotion
        }

    def execute_protocol(self, protocol_name: str, parameters: Dict) -> Dict:
        """Execute a collaboration protocol"""
        try:
            if protocol_name not in self.collaboration_protocols:
                raise UnknownProtocolError(f"Protocol {protocol_name} not found")

            protocol = self.collaboration_protocols[protocol_name]

            # Execute protocol with monitoring
            start_time = time.time()
            result = protocol(parameters)
            execution_time = time.time() - start_time

            result['execution_time'] = execution_time
            result['status'] = 'completed'

            return result

        except Exception as e:
            return {
                'status': 'failed',
                'protocol': protocol_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _execute_episode_production(self, parameters: Dict) -> Dict:
        """Execute complete episode production workflow"""
        results = {}

        # Phase 1: Video Processing
        try:
            video_params = {
                'video_files': parameters.get('video_files', []),
                'analysis_type': 'all',
                'editing_style': parameters.get('editing_style', 'dynamic')
            }

            video_result = self.agents['video_editor'].execute_workflow(
                'episode_edit',
                video_params
            )

            results['video_processing'] = video_result

        except Exception as e:
            results['video_processing'] = {
                'status': 'failed',
                'error': str(e)
            }

            # Decide whether to continue or abort
            if parameters.get('require_video', True):
                raise EpisodeProductionError("Video processing failed and is required")

        # Phase 2: Audio Processing
        try:
            audio_params = {
                'audio_files': parameters.get('audio_files', []),
                'sponsor_info': parameters.get('sponsors', []),
                'noise_reduction': parameters.get('noise_reduction', 'medium')
            }

            audio_result = self.agents['audio_engineer'].execute_workflow(
                'episode_audio',
                audio_params
            )

            results['audio_processing'] = audio_result

        except Exception as e:
            results['audio_processing'] = {
                'status': 'failed',
                'error': str(e)
            }

            # Audio is typically required
            raise EpisodeProductionError("Audio processing failed")

        # Phase 3: Content Packaging
        try:
            package_params = {
                'video_results': results['video_processing']['results'],
                'audio_results': results['audio_processing']['results'],
                'metadata': parameters.get('metadata', {}),
                'publish_strategy': parameters.get('publish_strategy', 'immediate')
            }

            package_result = self.agents['content_distributor'].execute_workflow(
                'package_episode',
                package_params
            )

            results['content_packaging'] = package_result

        except Exception as e:
            results['content_packaging'] = {
                'status': 'failed',
                'error': str(e)
            }

            raise EpisodeProductionError("Content packaging failed")

        # Phase 4: Social Promotion
        try:
            promo_params = {
                'episode_data': package_result['results'],
                'platforms': parameters.get('promotion_platforms', ['twitter', 'instagram']),
                'promotion_strategy': parameters.get('promotion_strategy', 'balanced')
            }

            promo_result = self.agents['social_media_manager'].execute_workflow(
                'promote_episode',
                promo_params
            )

            results['social_promotion'] = promo_result

        except Exception as e:
            results['social_promotion'] = {
                'status': 'failed',
                'error': str(e)
            }

            # Social promotion failure is not critical
            print(f"Social promotion failed but production can continue: {str(e)}")

        # Generate final report
        final_report = self._generate_production_report(results, parameters)

        return {
            'episode_production': final_report,
            'phase_results': results
        }

    def _generate_production_report(self, results: Dict, parameters: Dict) -> Dict:
        """Generate comprehensive production report"""
        report = {
            'production_id': f"prod_{uuid.uuid4().hex[:8]}",
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'phases': {}
        }

        # Analyze each phase
        for phase_name, phase_result in results.items():
            phase_status = phase_result.get('status', 'unknown')

            report['phases'][phase_name] = {
                'status': phase_status,
                'warnings': phase_result.get('warnings', []),
                'metrics': phase_result.get('metrics', {})
            }

            if phase_status != 'completed':
                report['status'] = 'partial_completion'

        # Calculate overall metrics
        report['metrics'] = {
            'total_execution_time': sum(
                phase.get('metrics', {}).get('execution_time', 0)
                for phase in results.values()
            ),
            'successful_phases': sum(
                1 for phase in results.values() if phase.get('status') == 'completed'
            ),
            'total_phases': len(results)
        }

        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(results)

        return report

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check video processing
        video_result = results.get('video_processing', {})
        if video_result.get('status') != 'completed':
            recommendations.append(
                "Review video processing workflow - consider alternative tools or manual intervention"
            )
        elif video_result.get('warnings'):
            recommendations.append(
                f"Video processing completed with warnings: {', '.join(video_result['warnings'])}"
            )

        # Check audio processing
        audio_result = results.get('audio_processing', {})
        if audio_result.get('status') != 'completed':
            recommendations.append(
                "Audio processing failed - this is critical and requires immediate attention"
            )

        # Check social promotion
        promo_result = results.get('social_promotion', {})
        if promo_result.get('status') != 'completed':
            recommendations.append(
                "Social promotion failed - consider manual posting or alternative promotion methods"
            )

        return recommendations

class UnknownProtocolError(Exception):
    """Error for unknown collaboration protocols"""
    pass

class EpisodeProductionError(Exception):
    """Error for episode production failures"""
    pass
```

## Testing Framework

```python
class ToolTestFramework:
    """
    Comprehensive testing framework for robust tools
    """

    def __init__(self):
        self.test_cases = []
        self.performance_metrics = {}

    def add_test_case(self, name: str, tool: RobustTool, parameters: Dict,
                     expected_status: ToolStatus = ToolStatus.SUCCESS,
                     validate_result: callable = None,
                     tags: List[str] = None):
        """Add a test case"""

        self.test_cases.append({
            'name': name,
            'tool': tool,
            'parameters': parameters,
            'expected_status': expected_status,
            'validate_result': validate_result,
            'tags': tags or []
        })

    def run_all_tests(self) -> Dict:
        """Execute all test cases"""
        results = []

        for test_case in self.test_cases:
            test_result = self._run_single_test(test_case)
            results.append(test_result)

            # Update performance metrics
            if test_result['status'] == 'passed':
                self._update_performance_metrics(test_result)

        return {
            'total_tests': len(self.test_cases),
            'passed': sum(1 for r in results if r['status'] == 'passed'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'performance': self.performance_metrics,
            'detailed_results': results
        }

    def _run_single_test(self, test_case: Dict) -> Dict:
        """Execute a single test case"""
        try:
            start_time = time.time()

            # Execute tool
            result = test_case['tool'].execute(test_case['parameters'])

            execution_time = time.time() - start_time

            # Validate status
            if result.status != test_case['expected_status']:
                return {
                    'name': test_case['name'],
                    'status': 'failed',
                    'expected_status': test_case['expected_status'].value,
                    'actual_status': result.status.value,
                    'execution_time': execution_time,
                    'error': f"Status mismatch: expected {test_case['expected_status'].value}, got {result.status.value}",
                    'tags': test_case['tags']
                }

            # Validate result content if validator provided
            if test_case['validate_result']:
                validation_result = test_case['validate_result'](result)
                if not validation_result['valid']:
                    return {
                        'name': test_case['name'],
                        'status': 'failed',
                        'expected_status': test_case['expected_status'].value,
                        'actual_status': result.status.value,
                        'execution_time': execution_time,
                        'error': f"Result validation failed: {validation_result['message']}",
                        'tags': test_case['tags']
                    }

            # Test passed
            return {
                'name': test_case['name'],
                'status': 'passed',
                'expected_status': test_case['expected_status'].value,
                'actual_status': result.status.value,
                'execution_time': execution_time,
                'warnings': result.warnings,
                'tags': test_case['tags']
            }

        except Exception as e:
            # Test failed with exception
            return {
                'name': test_case['name'],
                'status': 'failed',
                'expected_status': test_case['expected_status'].value,
                'execution_time': time.time() - start_time,
                'error': str(e),
                'error_type': e.__class__.__name__,
                'stack_trace': traceback.format_exc(),
                'tags': test_case['tags']
            }

    def _update_performance_metrics(self, test_result: Dict):
        """Update performance metrics from test results"""
        tool_name = test_result['name'].split('_')[0]  # Simple extraction

        if tool_name not in self.performance_metrics:
            self.performance_metrics[tool_name] = {
                'executions': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'warnings': 0
            }

        metrics = self.performance_metrics[tool_name]

        metrics['executions'] += 1
        metrics['total_time'] += test_result['execution_time']
        metrics['min_time'] = min(metrics['min_time'], test_result['execution_time'])
        metrics['max_time'] = max(metrics['max_time'], test_result['execution_time'])
        metrics['warnings'] += len(test_result.get('warnings', []))

        # Calculate averages
        metrics['avg_time'] = metrics['total_time'] / metrics['executions']
        metrics['avg_warnings'] = metrics['warnings'] / metrics['executions']

# Example Usage
def test_video_analysis_tool():
    """Test the video analysis tool"""

    # Create test framework
    test_framework = ToolTestFramework()

    # Create tool instance
    video_tool = VideoAnalysisTool()

    # Add test cases
    test_framework.add_test_case(
        name="video_analysis_basic",
        tool=video_tool,
        parameters={
            'video_path': 'test_videos/sample.mp4',
            'analysis_type': 'speaker_detection'
        },
        expected_status=ToolStatus.SUCCESS,
        tags=['basic', 'speaker_detection']
    )

    test_framework.add_test_case(
        name="video_analysis_comprehensive",
        tool=video_tool,
        parameters={
            'video_path': 'test_videos/episode.mp4',
            'analysis_type': 'all',
            'confidence_threshold': 0.8
        },
        expected_status=ToolStatus.SUCCESS,
        validate_result=lambda r: {
            'valid': 'speakers' in r.data and 'engagement' in r.data,
            'message': 'Missing expected analysis data'
        },
        tags=['comprehensive', 'full_analysis']
    )

    test_framework.add_test_case(
        name="video_analysis_invalid_file",
        tool=video_tool,
        parameters={
            'video_path': 'test_videos/nonexistent.mp4',
            'analysis_type': 'technical_quality'
        },
        expected_status=ToolStatus.FAILED,
        tags=['error_handling', 'file_not_found']
    )

    # Run tests
    test_results = test_framework.run_all_tests()

    # Print summary
    print(f"\n=== Video Analysis Tool Tests ===")
    print(f"Total: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")

    # Print performance metrics
    if 'video_analysis' in test_results['performance']:
        perf = test_results['performance']['video_analysis']
        print(f"\nPerformance Metrics:")
        print(f"  Average Time: {perf['avg_time']:.3f}s")
        print(f"  Min Time: {perf['min_time']:.3f}s")
        print(f"  Max Time: {perf['max_time']:.3f}s")
        print(f"  Avg Warnings: {perf['avg_warnings']:.1f}")

    # Print detailed results for failed tests
    for test_result in test_results['detailed_results']:
        if test_result['status'] == 'failed':
            print(f"\nFailed Test: {test_result['name']}")
            print(f"  Error: {test_result['error']}")
            if 'stack_trace' in test_result:
                print(f"  Stack Trace: {test_result['stack_trace']}")

    return test_results

if __name__ == "__main__":
    # Run example tests
    test_video_analysis_tool()
```

## Deployment and Monitoring

### 1. Deployment Checklist

```python
class ToolDeploymentManager:
    """
    Manage tool deployment with comprehensive checks
    """

    def __init__(self):
        self.deployment_checks = [
            self._check_dependencies,
            self._check_configuration,
            self._check_permissions,
            self._check_resource_availability,
            self._run_integration_tests,
            self._verify_backward_compatibility
        ]

    def deploy_tool(self, tool: RobustTool, environment: str = 'production') -> Dict:
        """Deploy tool with comprehensive validation"""

        deployment_report = {
            'tool': tool.name,
            'environment': environment,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'status': 'pending'
        }

        try:
            # Run all deployment checks
            for check in self.deployment_checks:
                check_name = check.__name__[6:]  # Remove '_check_' prefix

                try:
                    check_result = check(tool, environment)
                    deployment_report['checks'][check_name] = {
                        'status': 'passed',
                        'details': check_result
                    }

                except Exception as e:
                    deployment_report['checks'][check_name] = {
                        'status': 'failed',
                        'error': str(e),
                        'details': traceback.format_exc()
                    }

            # Check if all checks passed
            failed_checks = [
                name for name, check in deployment_report['checks'].items()
                if check['status'] == 'failed'
            ]

            if failed_checks:
                deployment_report['status'] = 'failed'
                deployment_report['failed_checks'] = failed_checks
                return deployment_report

            # Proceed with deployment
            deployment_result = self._perform_deployment(tool, environment)

            deployment_report['status'] = 'completed'
            deployment_report['deployment_result'] = deployment_result

            return deployment_report

        except Exception as e:
            deployment_report['status'] = 'error'
            deployment_report['error'] = str(e)
            deployment_report['stack_trace'] = traceback.format_exc()
            return deployment_report

    def _check_dependencies(self, tool: RobustTool, environment: str) -> Dict:
        """Check tool dependencies"""
        # This would check actual dependencies
        # For this example, we'll simulate the process

        return {
            'dependencies_checked': ['ffmpeg', 'opencv', 'numpy'],
            'missing_dependencies': [],
            'status': 'all_dependencies_satisfied'
        }

    def _check_configuration(self, tool: RobustTool, environment: str) -> Dict:
        """Check tool configuration"""
        # This would validate configuration files

        return {
            'configuration_files': ['config.json', 'settings.yml'],
            'validation_result': 'valid',
            'warnings': []
        }

    def _perform_deployment(self, tool: RobustTool, environment: str) -> Dict:
        """Perform actual deployment"""
        # This would handle the actual deployment process
        # For this example, we'll simulate success

        return {
            'deployment_method': 'containerized',
            'target_environment': environment,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
```

### 2. Monitoring Dashboard Integration

```python
class ToolMonitoringDashboard:
    """
    Integration with monitoring dashboard
    """

    def __init__(self):
        self.metrics_store = {}  # Would connect to actual metrics database
        self.alert_rules = []

    def record_execution(self, tool_result: ToolResult):
        """Record tool execution metrics"""

        tool_name = tool_result.data.get('tool_name', 'unknown')

        if tool_name not in self.metrics_store:
            self.metrics_store[tool_name] = {
                'executions': [],
                'success_rate': 0,
                'error_distribution': {},
                'performance': {}
            }

        # Store execution data
        execution_record = {
            'timestamp': tool_result.timestamp,
            'status': tool_result.status.value,
            'execution_time': tool_result.metrics.get('execution_time'),
            'warnings': len(tool_result.warnings),
            'metrics': tool_result.metrics
        }

        self.metrics_store[tool_name]['executions'].append(execution_record)

        # Update statistics
        self._update_statistics(tool_name)

        # Check alert rules
        self._check_alert_rules(tool_name, execution_record)

    def _update_statistics(self, tool_name: str):
        """Update statistical metrics"""

        executions = self.metrics_store[tool_name]['executions']

        if not executions:
            return

        # Calculate success rate
        successful = sum(1 for e in executions if e['status'] in ['success', 'partial_success'])
        self.metrics_store[tool_name]['success_rate'] = successful / len(executions)

        # Update error distribution
        error_distribution = {}
        for execution in executions:
            if execution['status'] == 'failed':
                error_type = execution.get('error_type', 'unknown')
                error_distribution[error_type] = error_distribution.get(error_type, 0) + 1

        self.metrics_store[tool_name]['error_distribution'] = error_distribution

        # Update performance metrics
        execution_times = [e['execution_time'] for e in executions if e['execution_time']]

        if execution_times:
            self.metrics_store[tool_name]['performance'] = {
                'average': sum(execution_times) / len(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'median': self._calculate_median(execution_times)
            }

    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median value"""
        if not values:
            return 0

        sorted_values = sorted(values)
        length = len(sorted_values)

        if length % 2 == 1:
            return sorted_values[length // 2]
        else:
            return (sorted_values[length // 2 - 1] + sorted_values[length // 2]) / 2

    def _check_alert_rules(self, tool_name: str, execution_record: Dict):
        """Check if any alert rules are triggered"""

        # Example alert rules
        alert_rules = [
            {
                'name': 'high_error_rate',
                'condition': lambda stats: stats['success_rate'] < 0.95,
                'severity': 'warning',
                'message': lambda tool: f"High error rate for {tool}: {stats['success_rate']:.1%}"
            },
            {
                'name': 'performance_degradation',
                'condition': lambda stats: stats['performance']['average'] > stats.get('baseline_performance', 0) * 1.5,
                'severity': 'warning',
                'message': lambda tool: f"Performance degradation detected for {tool}"
            },
            {
                'name': 'critical_failure',
                'condition': lambda record: record['status'] == 'failed' and
                                           'timeout' in record.get('error', '').lower(),
                'severity': 'critical',
                'message': lambda tool: f"Critical timeout failure for {tool}"
            }
        ]

        tool_stats = self.metrics_store[tool_name]

        for rule in alert_rules:
            if rule['condition'](tool_stats):
                alert = {
                    'tool': tool_name,
                    'rule': rule['name'],
                    'severity': rule['severity'],
                    'message': rule['message'](tool_name),
                    'timestamp': datetime.now().isoformat(),
                    'execution_record': execution_record
                }

                self._trigger_alert(alert)

    def _trigger_alert(self, alert: Dict):
        """Trigger alert notification"""

        # This would integrate with actual alerting systems
        # For this example, we'll just log it

        print(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")

        # In real implementation, this might:
        # - Send email notifications
        # - Post to Slack/Teams
        # - Create tickets in issue tracking
        # - Trigger automated remediation

    def get_dashboard_data(self) -> Dict:
        """Get data for monitoring dashboard"""

        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'tools': {}
        }

        for tool_name, tool_stats in self.metrics_store.items():
            dashboard_data['tools'][tool_name] = {
                'success_rate': tool_stats['success_rate'],
                'execution_count': len(tool_stats['executions']),
                'performance': tool_stats['performance'],
                'error_distribution': tool_stats['error_distribution'],
                'last_execution': tool_stats['executions'][-1] if tool_stats['executions'] else None
            }

        return dashboard_data
```

## Conclusion

This reference implementation demonstrates how to build robust, production-ready toolsets that:

1. **Handle errors gracefully** with comprehensive fallback strategies
2. **Provide informative feedback** through detailed logging and reporting
3. **Make decisive actions** based on clear validation and quality checks
4. **Adapt to different scenarios** with configurable behavior
5. **Maintain high reliability** through resource monitoring and safety checks
6. **Support continuous improvement** with performance monitoring and feedback loops

The implementation follows best practices for:

- **Separation of concerns** with clear separation between core logic and safety mechanisms
- **Comprehensive error handling** with multiple fallback strategies
- **Detailed monitoring** with performance metrics and quality assurance
- **Platform independence** with abstract base classes and interface definitions
- **Testability** with comprehensive testing frameworks
- **Maintainability** with clear documentation and structured code organization

These patterns can be adapted to build any of the toolsets needed for the podcast production agents, ensuring they work reliably in real-world scenarios.
