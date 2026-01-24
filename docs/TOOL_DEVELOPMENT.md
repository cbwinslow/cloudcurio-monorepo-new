# Tool Development Guide

Complete guide to creating custom tools for CloudCurio agents.

## Table of Contents

- [Overview](#overview)
- [Tool Architecture](#tool-architecture)
- [Creating Tools](#creating-tools)
- [Tool Types](#tool-types)
- [Best Practices](#best-practices)
- [Testing Tools](#testing-tools)
- [Tool Registry](#tool-registry)
- [Advanced Patterns](#advanced-patterns)

## Overview

Tools extend agent capabilities by providing reusable functions for specific tasks. CloudCurio supports multiple tool types that can be seamlessly integrated into agents.

### Tool Characteristics

**Good tools are:**
- **Single-purpose**: Do one thing well
- **Composable**: Can be combined with other tools
- **Testable**: Easy to unit test
- **Documented**: Clear inputs and outputs
- **Reliable**: Handle errors gracefully
- **Performant**: Execute efficiently

### Tool Types Supported

- **Python Tools**: Native Python functions
- **Shell Tools**: System commands and scripts
- **MCP Tools**: Model Context Protocol integrations
- **HTTP Tools**: REST API endpoints

## Tool Architecture

### Base Tool Pattern

All tools follow a standardized interface:

```python
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Standardized tool result format."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool:
    """Base class for all tools."""
    
    # Tool metadata
    name: str = "base_tool"
    description: str = "Base tool class"
    version: str = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize tool with optional configuration."""
        self.config = config or {}
    
    def execute(self, input_data: Any) -> ToolResult:
        """
        Execute the tool with given input.
        
        Args:
            input_data: Input for the tool
            
        Returns:
            ToolResult with execution status and data
        """
        try:
            result = self._execute_impl(input_data)
            return ToolResult(
                success=True,
                data=result,
                metadata=self._get_metadata()
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def _execute_impl(self, input_data: Any) -> Any:
        """Implement tool-specific logic. Override in subclasses."""
        raise NotImplementedError
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "tool_name": self.name,
            "version": self.version
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data. Override for custom validation."""
        return True
```

### Tool Lifecycle

```
Initialize → Validate Input → Execute → Return Result → Cleanup
     ↓            ↓              ↓           ↓            ↓
  Config      Check Valid    Core Logic   Format      Release
   Load       Parameters      Process     Output     Resources
```

## Creating Tools

### Step 1: Define Tool Class

Create a new Python module in `agents/tools/python/`:

```python
"""Custom data processor tool."""

from typing import Any, Dict, List
from pathlib import Path
import json
import logging

from agents.tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class DataProcessorTool(BaseTool):
    """Tool for processing structured data."""
    
    name = "data_processor"
    description = "Process and transform structured data"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data processor."""
        super().__init__(config)
        self.output_format = self.config.get("output_format", "json")
        self.max_records = self.config.get("max_records", 1000)
    
    def _execute_impl(self, input_data: Any) -> Dict[str, Any]:
        """
        Process data based on configuration.
        
        Args:
            input_data: Dictionary with 'data' and 'operation' keys
            
        Returns:
            Processed data dictionary
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input format")
        
        data = input_data.get("data", [])
        operation = input_data.get("operation", "transform")
        
        if operation == "filter":
            result = self._filter_data(data, input_data.get("criteria", {}))
        elif operation == "transform":
            result = self._transform_data(data, input_data.get("mapping", {}))
        elif operation == "aggregate":
            result = self._aggregate_data(data, input_data.get("group_by"))
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            "processed_data": result,
            "record_count": len(result) if isinstance(result, list) else 1,
            "operation": operation
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input has required structure."""
        if not isinstance(input_data, dict):
            return False
        
        if "data" not in input_data:
            return False
        
        return True
    
    def _filter_data(
        self, 
        data: List[Dict], 
        criteria: Dict[str, Any]
    ) -> List[Dict]:
        """Filter data based on criteria."""
        filtered = []
        for record in data[:self.max_records]:
            if self._matches_criteria(record, criteria):
                filtered.append(record)
        return filtered
    
    def _transform_data(
        self,
        data: List[Dict],
        mapping: Dict[str, str]
    ) -> List[Dict]:
        """Transform data using field mapping."""
        transformed = []
        for record in data[:self.max_records]:
            new_record = {}
            for old_key, new_key in mapping.items():
                if old_key in record:
                    new_record[new_key] = record[old_key]
            transformed.append(new_record)
        return transformed
    
    def _aggregate_data(
        self,
        data: List[Dict],
        group_by: str
    ) -> Dict[str, List[Dict]]:
        """Aggregate data by field."""
        aggregated = {}
        for record in data[:self.max_records]:
            key = record.get(group_by, "unknown")
            if key not in aggregated:
                aggregated[key] = []
            aggregated[key].append(record)
        return aggregated
    
    def _matches_criteria(
        self,
        record: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """Check if record matches filter criteria."""
        for key, value in criteria.items():
            if key not in record or record[key] != value:
                return False
        return True


# Convenience function for agent YAML entrypoint
def process_data(input_data: str) -> Dict[str, Any]:
    """
    Tool entrypoint function.
    
    Args:
        input_data: JSON string with data and operation
        
    Returns:
        Dictionary with processing results
    """
    try:
        parsed_input = json.loads(input_data) if isinstance(input_data, str) else input_data
        tool = DataProcessorTool()
        result = tool.execute(parsed_input)
        
        if result.success:
            return result.data
        else:
            return {"error": result.error}
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return {"error": str(e)}
```

### Step 2: Add Tool Configuration

Tools can be configured via agent specs or config files:

```yaml
# In agent spec
tools:
  - id: data_processor
    type: python
    entrypoint: agents/tools/python/data_processor.py:process_data
    config:
      output_format: json
      max_records: 500
```

### Step 3: Register Tool

Add to `agents/tools/__init__.py`:

```python
from .data_processor import DataProcessorTool

__all__ = [
    "DataProcessorTool",
    # ... other tools
]
```

### Step 4: Test Tool

Create `tests/test_data_processor_tool.py`:

```python
import pytest
from agents.tools.python.data_processor import DataProcessorTool


def test_filter_operation():
    """Test data filtering."""
    tool = DataProcessorTool()
    
    input_data = {
        "data": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30}
        ],
        "operation": "filter",
        "criteria": {"age": 30}
    }
    
    result = tool.execute(input_data)
    
    assert result.success
    assert len(result.data["processed_data"]) == 2
    assert all(r["age"] == 30 for r in result.data["processed_data"])


def test_transform_operation():
    """Test data transformation."""
    tool = DataProcessorTool()
    
    input_data = {
        "data": [
            {"first_name": "Alice", "last_name": "Smith"}
        ],
        "operation": "transform",
        "mapping": {
            "first_name": "given_name",
            "last_name": "family_name"
        }
    }
    
    result = tool.execute(input_data)
    
    assert result.success
    assert "given_name" in result.data["processed_data"][0]
    assert "family_name" in result.data["processed_data"][0]


def test_invalid_input():
    """Test error handling for invalid input."""
    tool = DataProcessorTool()
    
    result = tool.execute("invalid")
    
    assert not result.success
    assert result.error is not None
```

## Tool Types

### Python Tools

Native Python functions provide maximum flexibility:

```python
"""Simple calculator tool."""

def calculate(expression: str) -> dict:
    """
    Evaluate mathematical expression.
    
    Args:
        expression: Math expression string
        
    Returns:
        Result dictionary
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return {
            "success": True,
            "result": result,
            "expression": expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

**Usage in agent spec:**

```yaml
tools:
  - id: calculator
    type: python
    entrypoint: agents/tools/python/calculator.py:calculate
```

### Shell Tools

Execute system commands:

```bash
#!/bin/bash
# agents/tools/shell/git_status.sh

# Get git repository status
git status --porcelain
```

**Usage in agent spec:**

```yaml
tools:
  - id: git_status
    type: shell
    entrypoint: agents/tools/shell/git_status.sh
```

**Best practices for shell tools:**
- Always validate inputs
- Set timeouts
- Handle errors explicitly
- Use full paths to commands
- Avoid user input in commands (security)

### MCP Tools

Model Context Protocol tools provide standardized integrations:

```yaml
tools:
  - id: web_search
    type: mcp
    entrypoint: automation:search_web
    config:
      max_results: 10
      
  - id: media_processor
    type: mcp
    entrypoint: media:process_video
```

### HTTP Tools

Call REST APIs:

```yaml
tools:
  - id: weather_api
    type: http
    entrypoint: https://api.weather.com/v3/wx/conditions/current
    config:
      method: GET
      headers:
        Authorization: "Bearer ${WEATHER_API_KEY}"
      params:
        format: json
```

**HTTP Tool Wrapper:**

```python
"""HTTP tool wrapper."""

import requests
from typing import Dict, Any, Optional


class HTTPTool(BaseTool):
    """Tool for HTTP API calls."""
    
    def __init__(self, endpoint: str, config: Optional[Dict] = None):
        super().__init__(config)
        self.endpoint = endpoint
        self.method = self.config.get("method", "GET")
        self.headers = self.config.get("headers", {})
        self.timeout = self.config.get("timeout", 30)
    
    def _execute_impl(self, input_data: Any) -> Dict[str, Any]:
        """Make HTTP request."""
        params = input_data.get("params", {})
        data = input_data.get("data")
        
        response = requests.request(
            method=self.method,
            url=self.endpoint,
            headers=self.headers,
            params=params,
            json=data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "headers": dict(response.headers)
        }
```

## Best Practices

### 1. Input Validation

Always validate inputs before processing:

```python
def validate_input(self, input_data: Any) -> bool:
    """Validate input structure and types."""
    if not isinstance(input_data, dict):
        return False
    
    required_fields = ["operation", "data"]
    if not all(field in input_data for field in required_fields):
        return False
    
    # Type checking
    if not isinstance(input_data["data"], (list, dict)):
        return False
    
    return True
```

### 2. Error Handling

Implement comprehensive error handling:

```python
def execute(self, input_data: Any) -> ToolResult:
    """Execute with proper error handling."""
    try:
        # Validate first
        if not self.validate_input(input_data):
            raise ValueError("Invalid input format")
        
        # Execute
        result = self._execute_impl(input_data)
        
        return ToolResult(
            success=True,
            data=result
        )
    except ValueError as e:
        # User error - invalid input
        logger.warning(f"Invalid input: {e}")
        return ToolResult(
            success=False,
            data=None,
            error=f"Invalid input: {str(e)}"
        )
    except TimeoutError as e:
        # Timeout error
        logger.error(f"Operation timed out: {e}")
        return ToolResult(
            success=False,
            data=None,
            error="Operation timed out"
        )
    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error: {e}")
        return ToolResult(
            success=False,
            data=None,
            error="Internal tool error"
        )
```

### 3. Resource Management

Properly manage resources:

```python
class DatabaseTool(BaseTool):
    """Tool with resource management."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.connection = None
    
    def _execute_impl(self, input_data: Any) -> Any:
        """Execute with connection management."""
        try:
            self.connection = self._connect()
            result = self._query(input_data)
            return result
        finally:
            self._cleanup()
    
    def _connect(self):
        """Establish database connection."""
        # Connection logic
        pass
    
    def _query(self, input_data: Any):
        """Execute query."""
        # Query logic
        pass
    
    def _cleanup(self):
        """Clean up resources."""
        if self.connection:
            self.connection.close()
            self.connection = None
```

### 4. Performance Optimization

Optimize tool performance:

```python
from functools import lru_cache
import time


class CachedTool(BaseTool):
    """Tool with caching support."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        self._cache = {}
    
    @lru_cache(maxsize=100)
    def _cached_operation(self, key: str) -> Any:
        """Cached expensive operation."""
        # Expensive computation
        return self._compute(key)
    
    def _execute_impl(self, input_data: Any) -> Any:
        """Execute with caching."""
        cache_key = self._get_cache_key(input_data)
        
        # Check cache
        if cache_key in self._cache:
            cached_value, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_value
        
        # Compute
        result = self._cached_operation(cache_key)
        
        # Store in cache
        self._cache[cache_key] = (result, time.time())
        
        return result
```

### 5. Logging

Implement proper logging:

```python
import logging

logger = logging.getLogger(__name__)


class LoggingTool(BaseTool):
    """Tool with comprehensive logging."""
    
    def execute(self, input_data: Any) -> ToolResult:
        """Execute with logging."""
        logger.info(f"Executing {self.name} v{self.version}")
        logger.debug(f"Input: {input_data}")
        
        start_time = time.time()
        
        try:
            result = self._execute_impl(input_data)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Tool executed successfully in {execution_time:.2f}s"
            )
            logger.debug(f"Result: {result}")
            
            return ToolResult(
                success=True,
                data=result,
                metadata={
                    "execution_time": execution_time,
                    "tool": self.name
                }
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Tool failed after {execution_time:.2f}s: {e}",
                exc_info=True
            )
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
```

### 6. Configuration

Support flexible configuration:

```python
class ConfigurableTool(BaseTool):
    """Tool with extensive configuration."""
    
    DEFAULT_CONFIG = {
        "timeout": 30,
        "retries": 3,
        "batch_size": 100,
        "enable_cache": True
    }
    
    def __init__(self, config: Optional[Dict] = None):
        # Merge with defaults
        merged_config = {**self.DEFAULT_CONFIG, **(config or {})}
        super().__init__(merged_config)
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values."""
        if self.config["timeout"] <= 0:
            raise ValueError("timeout must be positive")
        
        if self.config["retries"] < 0:
            raise ValueError("retries must be non-negative")
        
        if self.config["batch_size"] <= 0:
            raise ValueError("batch_size must be positive")
```

## Testing Tools

### Unit Tests

Create comprehensive unit tests:

```python
import pytest
from unittest.mock import Mock, patch
from agents.tools.python.my_tool import MyTool


class TestMyTool:
    """Test suite for MyTool."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.tool = MyTool(config={"timeout": 10})
    
    def test_successful_execution(self):
        """Test successful tool execution."""
        input_data = {"operation": "test", "data": [1, 2, 3]}
        result = self.tool.execute(input_data)
        
        assert result.success
        assert result.data is not None
        assert result.error is None
    
    def test_invalid_input(self):
        """Test error handling for invalid input."""
        result = self.tool.execute("invalid")
        
        assert not result.success
        assert result.error is not None
    
    def test_timeout_handling(self):
        """Test timeout error handling."""
        with patch.object(self.tool, '_execute_impl', 
                         side_effect=TimeoutError()):
            result = self.tool.execute({"test": "data"})
            
            assert not result.success
            assert "timeout" in result.error.lower()
    
    def test_configuration(self):
        """Test configuration handling."""
        tool = MyTool(config={"custom_param": "value"})
        assert tool.config["custom_param"] == "value"
    
    def test_caching(self):
        """Test caching behavior."""
        input_data = {"key": "test"}
        
        # First call
        result1 = self.tool.execute(input_data)
        
        # Second call (should be cached)
        result2 = self.tool.execute(input_data)
        
        assert result1.data == result2.data
```

### Integration Tests

Test tools with real dependencies:

```python
import pytest
from agents.tools.python.api_client import APIClientTool


@pytest.mark.integration
class TestAPIClientIntegration:
    """Integration tests for API client tool."""
    
    def test_real_api_call(self):
        """Test with real API."""
        tool = APIClientTool(config={
            "endpoint": "https://api.github.com/users/github"
        })
        
        result = tool.execute({"method": "GET"})
        
        assert result.success
        assert "login" in result.data
    
    @pytest.mark.slow
    def test_timeout_handling(self):
        """Test timeout with slow endpoint."""
        tool = APIClientTool(config={
            "endpoint": "https://httpbin.org/delay/10",
            "timeout": 1
        })
        
        result = tool.execute({"method": "GET"})
        
        assert not result.success
```

## Tool Registry

### Registering Tools

Create centralized tool registry:

```python
"""Tool registry for agent discovery."""

from typing import Dict, Type, Optional
from .base import BaseTool

# Import all tools
from .data_processor import DataProcessorTool
from .api_client import APIClientTool
from .file_handler import FileHandlerTool


class ToolRegistry:
    """Central registry for all tools."""
    
    _registry: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> None:
        """Register a tool class."""
        tool_name = tool_class.name
        cls._registry[tool_name] = tool_class
    
    @classmethod
    def get(cls, tool_name: str) -> Optional[Type[BaseTool]]:
        """Get tool class by name."""
        return cls._registry.get(tool_name)
    
    @classmethod
    def list_tools(cls) -> list[str]:
        """List all registered tool names."""
        return list(cls._registry.keys())
    
    @classmethod
    def get_tool_info(cls, tool_name: str) -> Optional[Dict]:
        """Get tool metadata."""
        tool_class = cls.get(tool_name)
        if tool_class:
            return {
                "name": tool_class.name,
                "description": tool_class.description,
                "version": tool_class.version
            }
        return None


# Register tools
ToolRegistry.register(DataProcessorTool)
ToolRegistry.register(APIClientTool)
ToolRegistry.register(FileHandlerTool)


# Convenience functions
def get_tool(tool_name: str, config: Optional[Dict] = None) -> Optional[BaseTool]:
    """Get tool instance by name."""
    tool_class = ToolRegistry.get(tool_name)
    if tool_class:
        return tool_class(config)
    return None


def list_available_tools() -> list[str]:
    """List all available tools."""
    return ToolRegistry.list_tools()
```

### Using the Registry

```python
from agents.tools import get_tool, list_available_tools

# List all tools
tools = list_available_tools()
print(f"Available tools: {tools}")

# Get a tool
processor = get_tool("data_processor", config={"max_records": 100})
if processor:
    result = processor.execute({"data": [], "operation": "filter"})
```

## Advanced Patterns

### Async Tools

Support asynchronous operations:

```python
import asyncio
from typing import Any


class AsyncTool(BaseTool):
    """Tool with async support."""
    
    async def execute_async(self, input_data: Any) -> ToolResult:
        """Execute tool asynchronously."""
        try:
            result = await self._execute_async_impl(input_data)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
    
    async def _execute_async_impl(self, input_data: Any) -> Any:
        """Async implementation."""
        # Async operations
        await asyncio.sleep(1)
        return {"status": "completed"}
    
    def execute(self, input_data: Any) -> ToolResult:
        """Sync wrapper for async execution."""
        return asyncio.run(self.execute_async(input_data))
```

### Composable Tools

Create tools that compose other tools:

```python
class CompositeTool(BaseTool):
    """Tool that composes multiple tools."""
    
    def __init__(self, tools: list[BaseTool], config: Optional[Dict] = None):
        super().__init__(config)
        self.tools = tools
    
    def _execute_impl(self, input_data: Any) -> Any:
        """Execute tools in sequence."""
        result = input_data
        
        for tool in self.tools:
            tool_result = tool.execute(result)
            if not tool_result.success:
                raise RuntimeError(f"Tool {tool.name} failed: {tool_result.error}")
            result = tool_result.data
        
        return result
```

### Retry Logic

Add automatic retry with backoff:

```python
import time
from functools import wraps


def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator for retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor ** attempt
                        time.sleep(sleep_time)
            
            raise last_exception
        return wrapper
    return decorator


class RetryableTool(BaseTool):
    """Tool with automatic retry."""
    
    @retry_on_failure(max_retries=3, backoff_factor=2)
    def _execute_impl(self, input_data: Any) -> Any:
        """Execute with retry logic."""
        # Implementation that might fail transiently
        return self._unreliable_operation(input_data)
```

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [API Reference](API.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
