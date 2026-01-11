"""Robust Tool Base Class - Foundation for all production tools.

This module implements the RobustTool base class that provides:
- Comprehensive error handling with multiple fallback strategies
- Input validation with clear error messages
- Resource management and monitoring
- Quality assurance and built-in validation
- Comprehensive logging and progress tracking
- Graceful degradation when possible
"""

from __future__ import annotations

import json
import logging
import time
import psutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timezone
from pathlib import Path
import threading


@dataclass
class ToolResult:
    """Standardized result object for all tools."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    execution_id: str = ""
    quality_score: float = 0.0
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'execution_time': self.execution_time,
            'execution_id': self.execution_id,
            'quality_score': self.quality_score,
            'warnings': self.warnings,
            'metadata': self.metadata
        }

    def __contains__(self, key: object) -> bool:
        """Allow 'in' checks to inspect underlying data (for tests)."""
        try:
            return key in self.data
        except Exception:
            return False

    def __getitem__(self, key: str) -> Any:
        """Allow mapping-like access to ToolResult.data for convenience."""
        if isinstance(self.data, dict):
            return self.data.get(key)
        raise TypeError("ToolResult data is not subscriptable")


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    retryable_errors: List[str] = field(default_factory=lambda: ['ConnectionError', 'TimeoutError', 'RateLimitError'])


@dataclass
class ResourceLimits:
    """Resource usage limits for tools."""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    max_execution_time: float = 300.0  # 5 minutes
    max_disk_usage_percent: float = 90.0


class ToolError(Exception):
    """Base exception for tool-related errors."""
    def __init__(self, message: str, tool_name: str = "", execution_id: str = "", recoverable: bool = True):
        super().__init__(message)
        self.tool_name = tool_name
        self.execution_id = execution_id
        self.recoverable = recoverable


class ValidationError(ToolError):
    """Raised when input validation fails."""
    pass


class ResourceError(ToolError):
    """Raised when resource limits are exceeded."""
    pass


class RobustTool(ABC):
    """Base class for all robust production tools.

    Provides comprehensive error handling, validation, monitoring, and fallback strategies.
    """

    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the robust tool.

        Args:
            name: Unique tool name
            description: Human-readable description
            config: Optional configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config or {}

        # Setup logging
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.name}")
        self.logger.setLevel(logging.INFO)

        # Initialize components
        self.retry_policy = self._load_retry_policy()
        self.resource_limits = self._load_resource_limits()
        self.fallback_strategies = self._define_fallback_strategies()
        self.validation_schema = self._define_validation_schema()

        # Execution tracking
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.average_execution_time = 0.0

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.resource_usage_history: List[Dict[str, Any]] = []

    def _load_retry_policy(self) -> RetryPolicy:
        """Load retry policy from config."""
        retry_config = self.config.get('retry_policy', {})
        return RetryPolicy(
            max_attempts=retry_config.get('max_attempts', 3),
            backoff_factor=retry_config.get('backoff_factor', 2.0),
            initial_delay=retry_config.get('initial_delay', 1.0),
            max_delay=retry_config.get('max_delay', 60.0),
            retryable_errors=retry_config.get('retryable_errors', ['ConnectionError', 'TimeoutError', 'RateLimitError'])
        )

    def _load_resource_limits(self) -> ResourceLimits:
        """Load resource limits from config."""
        limits_config = self.config.get('resource_limits', {})
        return ResourceLimits(
            max_cpu_percent=limits_config.get('max_cpu_percent', 80.0),
            max_memory_percent=limits_config.get('max_memory_percent', 80.0),
            max_execution_time=limits_config.get('max_execution_time', 300.0),
            max_disk_usage_percent=limits_config.get('max_disk_usage_percent', 90.0)
        )

    @abstractmethod
    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies for this tool.

        Returns:
            List of fallback strategy dictionaries with keys:
            - name: Strategy name
            - condition: Callable that returns True if strategy applies
            - action: Callable that implements the fallback
            - priority: Priority order (lower numbers = higher priority)
        """
        pass

    @abstractmethod
    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define input validation schema.

        Returns:
            JSON Schema-like dictionary for parameter validation
        """
        pass

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with comprehensive safety measures.

        Args:
            parameters: Tool parameters dictionary

        Returns:
            ToolResult with execution outcome
        """
        execution_id = f"{self.name}_{int(time.time() * 1000)}_{self.execution_count}"
        start_time = time.time()

        self.execution_count += 1
        self.logger.info(f"Starting execution {execution_id}")

        try:
            # Start resource monitoring
            self._start_monitoring()

            # Validate parameters
            validated_params = self._validate_parameters(parameters)

            # Check resource availability
            self._check_resource_availability()

            # Execute with retry logic
            result_data = self._execute_with_retry(self._execute_core, validated_params, execution_id)

            # Perform quality assurance
            quality_score, qa_warnings = self._perform_quality_assurance(result_data)

            # Success
            execution_time = time.time() - start_time
            self.success_count += 1
            self._update_execution_stats(execution_time)

            result = ToolResult(
                success=True,
                data=result_data,
                execution_time=execution_time,
                execution_id=execution_id,
                quality_score=quality_score,
                warnings=qa_warnings
            )

            self.logger.info(f"Execution {execution_id} completed successfully in {execution_time:.2f}s")
            return result

        except Exception as e:
            # Re-raise obvious client-facing errors so callers/tests can catch them
            if isinstance(e, (FileNotFoundError, ValidationError)):
                raise

            execution_time = time.time() - start_time
            self.failure_count += 1
            self._update_execution_stats(execution_time)

            # Try fallback strategies
            fallback_result = self._apply_fallback_strategies(e, parameters, execution_id)
            if fallback_result:
                self.logger.warning(f"Execution {execution_id} recovered using fallback strategy")
                return fallback_result

            # Complete failure
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"Execution {execution_id} failed: {error_msg}")

            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                execution_id=execution_id
            )

        finally:
            # Stop monitoring
            self._stop_monitoring()

    @abstractmethod
    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Core execution logic - implement in subclasses.

        Args:
            parameters: Validated parameters
            execution_id: Unique execution identifier

        Returns:
            Tool execution result
        """
        pass

    def _validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters against schema.

        Args:
            parameters: Raw input parameters

        Returns:
            Validated and potentially transformed parameters

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Check required fields
            required = self.validation_schema.get('required', [])
            for field in required:
                if field not in parameters:
                    raise ValidationError(f"Missing required parameter: {field}", self.name)

            # Validate types and constraints
            properties = self.validation_schema.get('properties', {})
            validated = {}

            for param_name, param_value in parameters.items():
                if param_name in properties:
                    param_schema = properties[param_name]
                    validated[param_name] = self._validate_parameter(param_name, param_value, param_schema)
                else:
                    # Allow extra parameters
                    validated[param_name] = param_value

            # Apply defaults
            for param_name, param_schema in properties.items():
                if param_name not in validated and 'default' in param_schema:
                    validated[param_name] = param_schema['default']

            return validated

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Parameter validation failed: {str(e)}", self.name)

    def _validate_parameter(self, name: str, value: Any, schema: Dict[str, Any]) -> Any:
        """Validate a single parameter.

        Args:
            name: Parameter name
            value: Parameter value
            schema: Parameter schema

        Returns:
            Validated (potentially transformed) value

        Raises:
            ValidationError: If validation fails
        """
        expected_type = schema.get('type')

        # Type checking
        if expected_type == 'string' and not isinstance(value, str):
            raise ValidationError(f"Parameter {name} must be string, got {type(value)}")
        elif expected_type == 'number' and not isinstance(value, (int, float)):
            raise ValidationError(f"Parameter {name} must be number, got {type(value)}")
        elif expected_type == 'boolean' and not isinstance(value, bool):
            raise ValidationError(f"Parameter {name} must be boolean, got {type(value)}")
        elif expected_type == 'array' and not isinstance(value, list):
            raise ValidationError(f"Parameter {name} must be array, got {type(value)}")

        # Range constraints
        if expected_type == 'number':
            minimum = schema.get('minimum')
            maximum = schema.get('maximum')
            if minimum is not None and value < minimum:
                raise ValidationError(f"Parameter {name} must be >= {minimum}, got {value}")
            if maximum is not None and value > maximum:
                raise ValidationError(f"Parameter {name} must be <= {maximum}, got {value}")

        # String constraints
        if expected_type == 'string':
            min_length = schema.get('minLength')
            max_length = schema.get('maxLength')
            if min_length is not None and isinstance(value, str) and len(value) < min_length:
                raise ValidationError(f"Parameter {name} length must be >= {min_length}, got {len(value)}")
            if max_length is not None and isinstance(value, str) and len(value) > max_length:
                raise ValidationError(f"Parameter {name} length must be <= {max_length}, got {len(value)}")

        # Enum constraints
        enum_values = schema.get('enum')
        if enum_values and value not in enum_values:
            raise ValidationError(f"Parameter {name} must be one of {enum_values}, got {value}")

        return value

    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries fail
        """
        last_error = None

        for attempt in range(self.retry_policy.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_type = type(e).__name__

                if not self._is_retryable_error(e, error_type):
                    raise e

                if attempt < self.retry_policy.max_attempts - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {error_type}")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {self.retry_policy.max_attempts} attempts failed")
                    raise e

        if last_error is not None:
            raise last_error
        else:
            raise RuntimeError("Retry logic failed with no error information")

    def _is_retryable_error(self, error: Exception, error_type: str) -> bool:
        """Check if error is retryable.

        Args:
            error: The exception
            error_type: Exception type name

        Returns:
            True if error should be retried
        """
        return error_type in self.retry_policy.retryable_errors

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate backoff delay for retry.

        Args:
            attempt: Attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.retry_policy.initial_delay * (self.retry_policy.backoff_factor ** attempt)
        return min(delay, self.retry_policy.max_delay)

    def _apply_fallback_strategies(self, error: Exception, parameters: Dict[str, Any], execution_id: str) -> Optional[ToolResult]:
        """Apply fallback strategies for failed execution.

        Args:
            error: The original error
            parameters: Original parameters
            execution_id: Execution ID

        Returns:
            ToolResult if fallback succeeds, None otherwise
        """
        # Sort strategies by priority
        sorted_strategies = sorted(self.fallback_strategies, key=lambda s: s.get('priority', 999))

        for strategy in sorted_strategies:
            try:
                if strategy['condition'](error, parameters):
                    self.logger.info(f"Applying fallback strategy: {strategy['name']}")
                    result_data = strategy['action'](error, parameters, execution_id)

                    # Validate fallback result
                    quality_score, warnings = self._perform_quality_assurance(result_data)

                    return ToolResult(
                        success=True,
                        data=result_data,
                        execution_time=0.0,  # Fallback time not tracked separately
                        execution_id=f"{execution_id}_fallback_{strategy['name']}",
                        quality_score=quality_score,
                        warnings=warnings + [f"Used fallback strategy: {strategy['name']}"]
                    )
            except Exception as fb_error:
                self.logger.warning(f"Fallback strategy {strategy['name']} failed: {fb_error}")
                continue

        return None

    def _perform_quality_assurance(self, result: Any) -> tuple[float, List[str]]:
        """Perform quality assurance checks on result.

        Args:
            result: Tool execution result

        Returns:
            Tuple of (quality_score, warnings_list)
        """
        # Default implementation - subclasses should override
        return 1.0, []

    def _check_resource_availability(self) -> None:
        """Check if system resources are available.

        Raises:
            ResourceError: If resource limits are exceeded
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent

        if cpu_percent > self.resource_limits.max_cpu_percent:
            raise ResourceError(f"CPU usage too high: {cpu_percent}% > {self.resource_limits.max_cpu_percent}%", self.name)

        if memory_percent > self.resource_limits.max_memory_percent:
            raise ResourceError(f"Memory usage too high: {memory_percent}% > {self.resource_limits.max_memory_percent}%", self.name)

        if disk_percent > self.resource_limits.max_disk_usage_percent:
            raise ResourceError(f"Disk usage too high: {disk_percent}% > {self.resource_limits.max_disk_usage_percent}%", self.name)

    def _start_monitoring(self) -> None:
        """Start resource monitoring thread."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()

    def _stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)

    def _monitor_resources(self) -> None:
        """Monitor system resources during execution."""
        while self.monitoring_active:
            try:
                usage = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                }
                self.resource_usage_history.append(usage)
                time.sleep(1.0)
            except Exception as e:
                self.logger.warning(f"Resource monitoring error: {e}")
                break

    def _update_execution_stats(self, execution_time: float) -> None:
        """Update execution statistics.

        Args:
            execution_time: Time taken for execution
        """
        # Simple moving average
        alpha = 0.1
        self.average_execution_time = (alpha * execution_time) + ((1 - alpha) * self.average_execution_time)

    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics.

        Returns:
            Dictionary with execution statistics
        """
        total_attempts = self.success_count + self.failure_count
        success_rate = (self.success_count / total_attempts) * 100 if total_attempts > 0 else 0

        return {
            'name': self.name,
            'description': self.description,
            'total_executions': self.execution_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': success_rate,
            'average_execution_time': self.average_execution_time,
            'retry_policy': {
                'max_attempts': self.retry_policy.max_attempts,
                'backoff_factor': self.retry_policy.backoff_factor
            },
            'resource_limits': {
                'max_cpu_percent': self.resource_limits.max_cpu_percent,
                'max_memory_percent': self.resource_limits.max_memory_percent,
                'max_execution_time': self.resource_limits.max_execution_time
            }
        }

    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.average_execution_time = 0.0
        self.resource_usage_history.clear()
