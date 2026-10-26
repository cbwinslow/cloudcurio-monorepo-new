#!/usr/bin/env python3
"""Tool Template.

Template for creating new tools in CloudCurio.
Replace TOOL_NAME with your tool name.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TOOLNAMEConfig(BaseModel):
    """Configuration for TOOL_NAME tool."""

    # Add your configuration parameters here
    timeout: int = Field(default=30, gt=0, description="Operation timeout in seconds")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    # param1: str = Field(description="Description of param1")
    # param2: bool = Field(default=True, description="Description of param2")


class TOOLNAMETool:
    """TOOL_NAME tool for [brief description].

    Detailed description of what this tool does and when to use it.

    Example:
        >>> config = TOOLNAMEConfig(timeout=60)
        >>> tool = TOOLNAMETool(config)
        >>> result = tool.execute(param="value")
        >>> print(result["output"])
    """

    name: str = "TOOL_NAME"
    description: str = "Brief description for agent use"
    category: str = "custom"  # llm, web, file, data, system, integration, custom

    def __init__(self, config: TOOLNAMEConfig | None = None) -> None:
        """Initialize tool with configuration.

        Args:
            config: Tool configuration, uses defaults if None
        """
        self.config = config or TOOLNAMEConfig()
        logger.info(f"Initialized {self.name} tool")

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute tool operation.

        Args:
            **kwargs: Tool-specific parameters
                param1: Description of param1
                param2: Description of param2

        Returns:
            Dictionary with execution result:
                status: "success" or "error"
                output: Tool output data
                error: Error message if status is "error"
                metadata: Additional metadata

        Raises:
            ValueError: If required parameters are missing
            RuntimeError: If execution fails

        Example:
            >>> result = tool.execute(param1="value")
            >>> if result["status"] == "success":
            ...     print(result["output"])
        """
        try:
            # Validate inputs
            self._validate_inputs(kwargs)

            # Execute main logic
            output = self._process(**kwargs)

            return {
                "status": "success",
                "output": output,
                "metadata": {"tool": self.name, "category": self.category},
            }

        except ValueError as e:
            logger.error(f"Validation error in {self.name}: {e}")
            return {"status": "error", "error": f"Validation error: {e!s}", "output": None}

        except Exception as e:
            logger.error(f"Execution error in {self.name}: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "output": None}

    def _validate_inputs(self, kwargs: dict[str, Any]) -> None:
        """Validate input parameters.

        Args:
            kwargs: Parameters to validate

        Raises:
            ValueError: If validation fails
        """
        # Add your validation logic here
        # Example:
        # if "required_param" not in kwargs:
        #     raise ValueError("required_param is required")

    def _process(self, **kwargs: Any) -> Any:
        """Internal processing logic.

        Args:
            **kwargs: Processing parameters

        Returns:
            Processed output
        """
        # Implement your tool logic here
        # Example:
        # result = some_operation(kwargs.get("param1"))
        # return result

        return {"message": "Tool executed successfully", "data": kwargs}


def TOOL_NAME_tool(config: dict[str, Any] | None = None) -> TOOLNAMETool:
    """Factory function for TOOL_NAME tool.

    Args:
        config: Configuration dictionary

    Returns:
        Initialized tool instance

    Example:
        >>> tool = TOOL_NAME_tool({"timeout": 60})
        >>> result = tool.execute(param="value")
    """
    cfg = TOOLNAMEConfig(**config) if config else TOOLNAMEConfig()
    return TOOLNAMETool(cfg)


__all__ = [
    "TOOLNAMEConfig",
    "TOOLNAMETool",
    "TOOL_NAME_tool",
]
