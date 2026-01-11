"""
Base Tool Class - Foundation for all podcast production tools.

This class provides the core functionality that all tools inherit from,
including error handling, logging, configuration management, and performance
monitoring.
"""

import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .error_handling import ToolError, ToolConfigError, ToolValidationError


class BaseTool(ABC):
    """
    Abstract base class for all podcast production tools.

    Provides core functionality including:
    - Configuration management
    - Error handling and recovery
    - Performance monitoring
    - Logging and debugging
    - Input validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the base tool.

        Args:
            config: Configuration dictionary for the tool
            **kwargs: Additional keyword arguments for tool-specific configuration
        """
        self.tool_id = str(uuid.uuid4())
        self.tool_name = self.__class__.__name__
        self.config = config or {}
        self.kwargs = kwargs
        self.logger = self._setup_logger()
        self.performance_metrics = {}
        self.last_error = None

        # Initialize performance tracking
        self._start_time = None
        self._end_time = None

        # Validate configuration
        self._validate_config()

        # Set up error recovery
        self._setup_error_recovery()

        self.logger.info(f"Initialized {self.tool_name} with ID: {self.tool_id}")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the tool."""
        logger = logging.getLogger(f"{self.tool_name}_{self.tool_id}")
        logger.setLevel(logging.INFO)

        # Add console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def _validate_config(self) -> None:
        """Validate the tool configuration."""
        try:
            # Basic validation - can be overridden by subclasses
            if not isinstance(self.config, dict):
                raise ToolConfigError(f"Configuration must be a dictionary, got {type(self.config)}")

            # Tool-specific validation
            self._validate_tool_config()

        except Exception as e:
            error_msg = f"Configuration validation failed for {self.tool_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolConfigError(error_msg) from e

    def _validate_tool_config(self) -> None:
        """Tool-specific configuration validation. Can be overridden by subclasses."""
        pass

    def _setup_error_recovery(self) -> None:
        """Set up error recovery mechanisms."""
        # Default error recovery - can be enhanced by subclasses
        self.error_recovery_attempts = 3
        self.error_recovery_delay = 1.0  # seconds

    def _start_performance_monitoring(self) -> None:
        """Start performance monitoring."""
        self._start_time = time.time()
        self.performance_metrics = {
            'start_time': datetime.now().isoformat(),
            'execution_time': None,
            'memory_usage': None,
            'status': 'running'
        }

    def _end_performance_monitoring(self) -> None:
        """End performance monitoring and record metrics."""
        if self._start_time:
            self._end_time = time.time()
            execution_time = self._end_time - self._start_time

            self.performance_metrics.update({
                'end_time': datetime.now().isoformat(),
                'execution_time': execution_time,
                'status': 'completed'
            })

            self.logger.info(f"Performance metrics: {json.dumps(self.performance_metrics, indent=2)}")

    def _handle_error(self, error: Exception) -> None:
        """Handle errors with recovery attempts."""
        self.last_error = error
        error_msg = f"Error in {self.tool_name}: {str(error)}"
        self.logger.error(error_msg)

        # Attempt recovery
        for attempt in range(self.error_recovery_attempts):
            try:
                self.logger.info(f"Recovery attempt {attempt + 1}/{self.error_recovery_attempts}")
                time.sleep(self.error_recovery_delay)

                # Tool-specific recovery logic
                self._recover_from_error(error)

                self.logger.info("Error recovery successful")
                return

            except Exception as recovery_error:
                self.logger.warning(f"Recovery attempt {attempt + 1} failed: {str(recovery_error)}")
                continue

        # If all recovery attempts fail
        self.logger.error(f"All recovery attempts failed for {self.tool_name}")
        raise ToolError(f"Tool {self.tool_name} failed after recovery attempts: {str(error)}") from error

    def _recover_from_error(self, error: Exception) -> None:
        """Tool-specific error recovery logic. Can be overridden by subclasses."""
        # Default recovery: log the error and continue
        self.logger.warning(f"Default error recovery for {self.tool_name}: {str(error)}")

    def _validate_input(self, *args, **kwargs) -> None:
        """Validate input parameters."""
        try:
            # Basic validation - can be enhanced by subclasses
            if not args and not kwargs:
                raise ToolValidationError(f"No input provided to {self.tool_name}")

            # Tool-specific validation
            self._validate_tool_input(*args, **kwargs)

        except Exception as e:
            error_msg = f"Input validation failed for {self.tool_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolValidationError(error_msg) from e

    def _validate_tool_input(self, *args, **kwargs) -> None:
        """Tool-specific input validation. Can be overridden by subclasses."""
        pass

    def _log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log tool operations with details."""
        log_message = f"Operation: {operation}"
        if details:
            log_message += f" | Details: {json.dumps(details, indent=2)}"

        self.logger.info(log_message)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the tool."""
        return self.performance_metrics.copy()

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the tool."""
        return {
            'tool_name': self.tool_name,
            'tool_id': self.tool_id,
            'status': 'ready' if not self.last_error else 'error',
            'last_error': str(self.last_error) if self.last_error else None,
            'performance': self.performance_metrics
        }

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the tool's main functionality.

        This method must be implemented by all subclasses.

        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            Result of the tool execution

        Raises:
            ToolError: If tool execution fails
        """
        pass

    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.tool_name}(id={self.tool_id[:8]})"

    def __repr__(self) -> str:
        """Detailed representation of the tool."""
        return f"{self.__class__.__name__}(id={self.tool_id}, config={self.config})"


class ToolFactory:
    """
    Factory class for creating tool instances.

    Provides a centralized way to instantiate tools with proper configuration
    and error handling.
    """

    @staticmethod
    def create_tool(tool_class, config: Optional[Dict[str, Any]] = None, **kwargs) -> BaseTool:
        """
        Create a tool instance.

        Args:
            tool_class: The tool class to instantiate
            config: Configuration dictionary for the tool
            **kwargs: Additional keyword arguments

        Returns:
            Instance of the requested tool

        Raises:
            ToolError: If tool creation fails
        """
        try:
            if not issubclass(tool_class, BaseTool):
                raise ToolError(f"Tool class {tool_class} must inherit from BaseTool")

            tool_instance = tool_class(config=config, **kwargs)
            return tool_instance

        except Exception as e:
            raise ToolError(f"Failed to create tool {tool_class.__name__}: {str(e)}") from e
