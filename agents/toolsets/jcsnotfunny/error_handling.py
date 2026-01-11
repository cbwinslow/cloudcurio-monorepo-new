"""
Error Handling Module - Comprehensive error management for podcast production tools.

This module defines custom exceptions and error handling utilities that provide
robust, informative, and actionable error management across all tools.
"""

from typing import Any, Dict, Optional, List
import traceback
import logging


class ToolError(Exception):
    """
    Base exception class for all tool-related errors.

    Provides comprehensive error information including:
    - Error type and message
    - Contextual information
    - Recovery suggestions
    - Stack trace
    """

    def __init__(self,
                 message: str,
                 error_type: str = "generic",
                 context: Optional[Dict[str, Any]] = None,
                 recovery_suggestions: Optional[List[str]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize a ToolError.

        Args:
            message: Error message describing what went wrong
            error_type: Type/category of error (e.g., 'config', 'validation', 'execution')
            context: Additional context about the error
            recovery_suggestions: List of suggestions for recovery
            original_exception: Original exception that caused this error
        """
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.original_exception = original_exception

        # Generate detailed error information
        self.error_info = self._generate_error_info()

        super().__init__(self._format_error_message())

    def _generate_error_info(self) -> Dict[str, Any]:
        """Generate comprehensive error information dictionary."""
        error_info = {
            'message': self.message,
            'type': self.error_type,
            'context': self.context,
            'recovery_suggestions': self.recovery_suggestions,
            'timestamp': self._get_current_timestamp()
        }

        if self.original_exception:
            error_info['original_error'] = {
                'type': type(self.original_exception).__name__,
                'message': str(self.original_exception),
                'stack_trace': self._get_stack_trace()
            }

        return error_info

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_stack_trace(self) -> str:
        """Get stack trace from original exception."""
        if self.original_exception:
            return ''.join(traceback.format_tb(self.original_exception.__traceback__))
        return "No stack trace available"

    def _format_error_message(self) -> str:
        """Format a comprehensive error message."""
        lines = [
            f"=== {self.error_type.upper()} ERROR ===",
            f"Message: {self.message}",
            f"Timestamp: {self.error_info['timestamp']}"
        ]

        if self.context:
            lines.append("Context:")
            for key, value in self.context.items():
                lines.append(f"  {key}: {value}")

        if self.recovery_suggestions:
            lines.append("Recovery Suggestions:")
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        if self.original_exception:
            lines.append(f"Original Error: {type(self.original_exception).__name__}")
            lines.append(f"Original Message: {str(self.original_exception)}")

        return '\n'.join(lines)

    def get_error_info(self) -> Dict[str, Any]:
        """Get comprehensive error information."""
        return self.error_info.copy()

    def log_error(self, logger: Optional[logging.Logger] = None) -> None:
        """Log the error using provided logger or print to console."""
        error_message = self._format_error_message()

        if logger:
            logger.error(error_message)
        else:
            print(f"ERROR: {error_message}")

    def __str__(self) -> str:
        """String representation of the error."""
        return self._format_error_message()

    def __repr__(self) -> str:
        """Detailed representation of the error."""
        return f"ToolError(message='{self.message}', type='{self.error_type}')"


class ToolConfigError(ToolError):
    """
    Exception for configuration-related errors.

    Used when tool configuration is invalid or missing required parameters.
    """

    def __init__(self,
                 message: str,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize a configuration error.

        Args:
            message: Error message describing the configuration issue
            context: Additional context about the configuration error
            original_exception: Original exception that caused this error
        """
        recovery_suggestions = [
            "Check tool configuration file for syntax errors",
            "Verify all required parameters are present",
            "Validate configuration values against expected types",
            "Consult tool documentation for configuration requirements"
        ]

        super().__init__(
            message=message,
            error_type="configuration",
            context=context,
            recovery_suggestions=recovery_suggestions,
            original_exception=original_exception
        )


class ToolValidationError(ToolError):
    """
    Exception for input validation errors.

    Used when tool input fails validation checks.
    """

    def __init__(self,
                 message: str,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize a validation error.

        Args:
            message: Error message describing the validation failure
            context: Additional context about the validation error
            original_exception: Original exception that caused this error
        """
        recovery_suggestions = [
            "Check input parameters against tool requirements",
            "Validate data types and formats",
            "Ensure required fields are provided",
            "Consult tool documentation for input specifications"
        ]

        super().__init__(
            message=message,
            error_type="validation",
            context=context,
            recovery_suggestions=recovery_suggestions,
            original_exception=original_exception
        )


class ToolExecutionError(ToolError):
    """
    Exception for tool execution failures.

    Used when tool execution fails during processing.
    """

    def __init__(self,
                 message: str,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize an execution error.

        Args:
            message: Error message describing the execution failure
            context: Additional context about the execution error
            original_exception: Original exception that caused this error
        """
        recovery_suggestions = [
            "Check system resources and availability",
            "Verify input data integrity",
            "Review tool logs for detailed error information",
            "Consider retrying the operation with adjusted parameters"
        ]

        super().__init__(
            message=message,
            error_type="execution",
            context=context,
            recovery_suggestions=recovery_suggestions,
            original_exception=original_exception
        )


class ToolTimeoutError(ToolError):
    """
    Exception for tool timeout situations.

    Used when tool execution exceeds maximum allowed time.
    """

    def __init__(self,
                 message: str,
                 timeout: float,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize a timeout error.

        Args:
            message: Error message describing the timeout
            timeout: Timeout duration that was exceeded
            context: Additional context about the timeout
            original_exception: Original exception that caused this error
        """
        recovery_suggestions = [
            f"Increase timeout threshold (current: {timeout}s)",
            "Optimize tool performance",
            "Reduce input data size",
            "Check for system resource constraints"
        ]

        context = context or {}
        context['timeout_seconds'] = timeout

        super().__init__(
            message=message,
            error_type="timeout",
            context=context,
            recovery_suggestions=recovery_suggestions,
            original_exception=original_exception
        )


class ToolDependencyError(ToolError):
    """
    Exception for missing or incompatible dependencies.

    Used when required dependencies are not available.
    """

    def __init__(self,
                 message: str,
                 missing_dependencies: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize a dependency error.

        Args:
            message: Error message describing the dependency issue
            missing_dependencies: List of missing dependencies
            context: Additional context about the dependency error
            original_exception: Original exception that caused this error
        """
        recovery_suggestions = [
            "Install missing dependencies using package manager",
            "Check dependency versions for compatibility",
            "Verify system requirements",
            "Consult tool documentation for dependency information"
        ]

        context = context or {}
        if missing_dependencies:
            context['missing_dependencies'] = missing_dependencies

        super().__init__(
            message=message,
            error_type="dependency",
            context=context,
            recovery_suggestions=recovery_suggestions,
            original_exception=original_exception
        )


# Domain-specific errors (used by higher-level toolsets)
class VideoAnalysisError(ToolError):
    """Error raised for video analysis specific failures."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, original_exception: Optional[Exception] = None):
        recovery_suggestions = [
            "Verify the input video file path and accessibility",
            "Check the installed video processing dependencies",
            "Ensure sufficient system resources for analysis",
        ]
        super().__init__(message=message, error_type="video_analysis", context=context, recovery_suggestions=recovery_suggestions, original_exception=original_exception)


class AudioProcessingError(ToolError):
    """Error raised for audio processing failures."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, original_exception: Optional[Exception] = None):
        recovery_suggestions = [
            "Verify the input audio file format and codecs",
            "Confirm required audio tooling (ffmpeg, sox) is installed",
            "Reduce processing quality to fit resource constraints"
        ]
        super().__init__(message=message, error_type="audio_processing", context=context, recovery_suggestions=recovery_suggestions, original_exception=original_exception)


class SchedulingError(ToolError):
    """Error raised for general scheduling failures."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, original_exception: Optional[Exception] = None):
        recovery_suggestions = [
            "Check scheduling service availability",
            "Verify platform API credentials and scopes",
            "Retry the scheduling operation after a short delay"
        ]
        super().__init__(message=message, error_type="scheduling", context=context, recovery_suggestions=recovery_suggestions, original_exception=original_exception)


class SchedulingConflictError(SchedulingError):
    """Raised when a scheduling conflict occurs (overlapping times)."""

    def __init__(self, message: str, conflicting_items: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        if conflicting_items:
            ctx['conflicts'] = conflicting_items
        recovery_suggestions = [
            "Adjust scheduled times to avoid conflicts",
            "Check the timezone settings for scheduled items"
        ]
        super().__init__(message=message, context=ctx, original_exception=None)


class SchedulingValidationError(SchedulingError):
    """Raised for validation errors related to scheduling input."""

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        if field:
            ctx['field'] = field
            ctx['invalid_value'] = value
        super().__init__(message=message, context=ctx, original_exception=None)


class ErrorHandler:
    """
    Centralized error handling utility.

    Provides consistent error handling across all tools with logging,
    recovery attempts, and error reporting.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the error handler.

        Args:
            logger: Logger instance for error logging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_history: List[Dict[str, Any]] = []

    def handle_error(self,
                    error: Exception,
                    context: Optional[Dict[str, Any]] = None,
                    max_retry_attempts: int = 3,
                    retry_delay: float = 1.0) -> None:
        """
        Handle an error with retry logic and comprehensive reporting.

        Args:
            error: The exception to handle
            context: Additional context about the error
            max_retry_attempts: Maximum number of retry attempts
            retry_delay: Delay between retry attempts in seconds

        Raises:
            ToolError: If all retry attempts fail
        """
        # Convert to ToolError if not already
        tool_error = self._convert_to_tool_error(error, context)

        # Log the error
        tool_error.log_error(self.logger)

        # Add to error history
        self._add_to_error_history(tool_error)

        # Attempt recovery with retries
        self._attempt_recovery(tool_error, max_retry_attempts, retry_delay)

        # If we get here, recovery failed
        raise tool_error

    def _convert_to_tool_error(self,
                              error: Exception,
                              context: Optional[Dict[str, Any]] = None) -> ToolError:
        """Convert any exception to a ToolError."""
        if isinstance(error, ToolError):
            return error

        return ToolError(
            message=str(error),
            error_type="unexpected",
            context=context,
            original_exception=error
        )

    def _add_to_error_history(self, error: ToolError) -> None:
        """Add error to history for tracking and analysis."""
        self.error_history.append({
            'timestamp': error.error_info['timestamp'],
            'type': error.error_type,
            'message': error.message,
            'context': error.context
        })

        # Keep history size manageable
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

    def _attempt_recovery(self,
                         error: ToolError,
                         max_retry_attempts: int,
                         retry_delay: float) -> None:
        """Attempt to recover from the error."""
        for attempt in range(max_retry_attempts):
            try:
                self.logger.info(f"Recovery attempt {attempt + 1}/{max_retry_attempts}")

                # Apply recovery strategy based on error type
                self._apply_recovery_strategy(error, attempt)

                self.logger.info("Error recovery successful")
                return

            except Exception as recovery_error:
                self.logger.warning(f"Recovery attempt {attempt + 1} failed: {str(recovery_error)}")

                if attempt < max_retry_attempts - 1:
                    time.sleep(retry_delay)

                continue

    def _apply_recovery_strategy(self, error: ToolError, attempt: int) -> None:
        """Apply error-specific recovery strategy."""
        recovery_strategies = {
            'configuration': self._recover_from_config_error,
            'validation': self._recover_from_validation_error,
            'execution': self._recover_from_execution_error,
            'timeout': self._recover_from_timeout_error,
            'dependency': self._recover_from_dependency_error
        }

        strategy = recovery_strategies.get(error.error_type, self._default_recovery)
        strategy(error, attempt)

    def _recover_from_config_error(self, error: ToolError, attempt: int) -> None:
        """Recovery strategy for configuration errors."""
        self.logger.info(f"Attempting config error recovery (attempt {attempt + 1})")
        # Implement specific recovery logic for config errors

    def _recover_from_validation_error(self, error: ToolError, attempt: int) -> None:
        """Recovery strategy for validation errors."""
        self.logger.info(f"Attempting validation error recovery (attempt {attempt + 1})")
        # Implement specific recovery logic for validation errors

    def _recover_from_execution_error(self, error: ToolError, attempt: int) -> None:
        """Recovery strategy for execution errors."""
        self.logger.info(f"Attempting execution error recovery (attempt {attempt + 1})")
        # Implement specific recovery logic for execution errors

    def _recover_from_timeout_error(self, error: ToolError, attempt: int) -> None:
        """Recovery strategy for timeout errors."""
        self.logger.info(f"Attempting timeout error recovery (attempt {attempt + 1})")
        # Implement specific recovery logic for timeout errors

    def _recover_from_dependency_error(self, error: ToolError, attempt: int) -> None:
        """Recovery strategy for dependency errors."""
        self.logger.info(f"Attempting dependency error recovery (attempt {attempt + 1})")
        # Implement specific recovery logic for dependency errors

    def _default_recovery(self, error: ToolError, attempt: int) -> None:
        """Default recovery strategy for unknown error types."""
        self.logger.info(f"Attempting default error recovery (attempt {attempt + 1})")
        # Implement default recovery logic

    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get the error history."""
        return self.error_history.copy()

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history.clear()


# Import time at the end to avoid circular imports
import time
