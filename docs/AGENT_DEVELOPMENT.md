# Agent Development Guide

Complete guide to developing agents in the CloudCurio framework.

## Table of Contents

- [Overview](#overview)
- [Agent Specification Format](#agent-specification-format)
- [Creating Your First Agent](#creating-your-first-agent)
- [Agent Architecture](#agent-architecture)
- [Tool Integration](#tool-integration)
- [Model Configuration](#model-configuration)
- [Testing & Evaluation](#testing--evaluation)
- [Best Practices](#best-practices)
- [Advanced Patterns](#advanced-patterns)

## Overview

CloudCurio agents are defined using a declarative YAML specification format that compiles to optimized JSON artifacts for execution. This approach provides:

- **Human-friendly authoring**: Write specs in readable YAML
- **Machine-optimized execution**: Run from compiled JSON
- **Framework agnostic**: Support multiple runtime adapters
- **Type safety**: Pydantic validation ensures correctness
- **Testability**: Golden test suites for reliable validation

### Agent Lifecycle

```
YAML Spec → Validation → Compilation → Runtime Execution → Evaluation
     ↓           ↓            ↓              ↓               ↓
   Author    Check Valid   JSON Artifact   Execute       Test Quality
```

## Agent Specification Format

### Schema v1 Structure

```yaml
api_version: v1              # Specification version
kind: Agent                  # Resource type
metadata:                    # Agent metadata
  name: agent_name          # Unique identifier (lowercase_snake_case)
  version: 1.0.0            # Semantic version
  tags: [domain, type]      # Classification tags
spec:                        # Agent specification
  model_policy:             # Model configuration
    preferred:              # Primary model
      provider: ollama      # Provider (ollama, openai, anthropic, etc.)
      model: qwen2.5-coder  # Model identifier
    fallbacks: []           # Fallback models (optional)
  prompts:                  # Prompt configuration
    system: path/to/prompt.md  # System prompt file
  tools: []                 # Tool references
  runtime:                  # Runtime configuration
    supported: [local]      # Supported runtimes
  eval:                     # Evaluation configuration
    suites: []              # Test suites
```

### Field Specifications

#### Metadata

**name** (required, string)
- Unique identifier for the agent
- Must be lowercase with underscores
- Should describe the agent's primary function
- Examples: `transcription_agent`, `code_reviewer`, `social_media_manager`

**version** (required, string)
- Semantic versioning: MAJOR.MINOR.PATCH
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

**tags** (optional, array of strings)
- Classification tags for discovery and organization
- Common tags: `production`, `experimental`, `media`, `analysis`, `automation`

#### Model Policy

Defines which LLM models the agent should use and fallback strategies.

```yaml
model_policy:
  preferred:
    provider: ollama           # Primary provider
    model: qwen2.5-coder      # Primary model
  fallbacks:
    - provider: openrouter     # Fallback provider
      model: qwen/qwen-2.5-coder-32b-instruct
    - provider: openai         # Second fallback
      model: gpt-4-turbo
```

**Supported Providers:**
- `ollama` - Local models via Ollama
- `openai` - OpenAI API (GPT-4, GPT-3.5)
- `anthropic` - Claude models
- `openrouter` - OpenRouter proxy service
- `google` - Google Gemini models
- `mistral` - Mistral AI models

#### Prompts

Define the system prompts that guide agent behavior.

```yaml
prompts:
  system: prompts/system/code_reviewer.md
```

**System Prompt Guidelines:**
- Store prompts in `prompts/system/` directory
- Use Markdown format for readability
- Include clear role definition
- Specify expected behaviors
- Define output formats
- Provide example interactions

**Example System Prompt Structure:**

```markdown
# Role
You are an expert code reviewer specializing in Python.

# Responsibilities
- Review code for bugs, security issues, and best practices
- Suggest improvements for readability and maintainability
- Provide constructive feedback with specific examples

# Guidelines
- Focus on high-impact issues first
- Explain the reasoning behind each suggestion
- Provide code examples when helpful

# Output Format
Return findings in JSON format:
{
  "critical": [...],
  "recommendations": [...],
  "positive_notes": [...]
}
```

#### Tools

Reference tools the agent can use to perform tasks.

```yaml
tools:
  - id: file_reader                      # Tool identifier
    type: python                         # Tool type
    entrypoint: agents/tools/python/file_reader.py:read_file
  - id: code_analyzer
    type: python
    entrypoint: agents/tools/python/analyzer.py:analyze_code
```

**Tool Types:**
- `python` - Python function tools
- `shell` - Shell command tools
- `mcp` - Model Context Protocol tools
- `http` - HTTP API tools

**Entrypoint Format:**
- Python: `path/to/module.py:function_name`
- Shell: `path/to/script.sh`
- MCP: `mcp_server_name:tool_name`
- HTTP: `https://api.example.com/endpoint`

#### Runtime

Specify which runtime adapters support this agent.

```yaml
runtime:
  supported: [local, pydanticai, langchain, crewai]
```

**Available Runtimes:**
- `local` - Built-in lightweight runtime (always supported)
- `pydanticai` - PydanticAI framework
- `langchain` - LangChain framework
- `crewai` - CrewAI multi-agent framework

#### Evaluation

Define test suites for quality assurance.

```yaml
eval:
  suites:
    - id: golden_tests
      path: agents/evals/golden/agent_name_cases.yaml
    - id: integration_tests
      path: agents/evals/integration/agent_name_integration.yaml
```

## Creating Your First Agent

### Step 1: Scaffold the Agent

```bash
./bin/cbw-capture agent my_new_agent
```

This creates:
- `agents/specs/my_new_agent.agent.yaml` - Agent specification
- `agents/evals/golden/my_new_agent_cases.yaml` - Test cases
- `prompts/system/my_new_agent.md` - System prompt template

### Step 2: Define Agent Specification

Edit `agents/specs/my_new_agent.agent.yaml`:

```yaml
api_version: v1
kind: Agent
metadata:
  name: my_new_agent
  version: 1.0.0
  tags: [custom, automation]
spec:
  model_policy:
    preferred:
      provider: ollama
      model: qwen2.5-coder
  prompts:
    system: prompts/system/my_new_agent.md
  tools:
    - id: custom_tool
      type: python
      entrypoint: agents/tools/python/my_tool.py:execute
  runtime:
    supported: [local, pydanticai]
  eval:
    suites:
      - id: my_tests
        path: agents/evals/golden/my_new_agent_cases.yaml
```

### Step 3: Write System Prompt

Edit `prompts/system/my_new_agent.md`:

```markdown
# Expert Assistant Agent

You are an expert assistant specializing in task automation.

## Your Role
Help users automate repetitive tasks efficiently and reliably.

## Capabilities
- Analyze task requirements
- Design automation workflows
- Generate executable scripts
- Validate automation results

## Guidelines
- Ask clarifying questions for ambiguous requirements
- Prioritize reliability over complexity
- Provide clear documentation for generated automation
- Handle edge cases and error scenarios

## Output Format
Provide structured responses with:
1. Task analysis
2. Proposed solution
3. Implementation steps
4. Testing recommendations
```

### Step 4: Create Tools (if needed)

Create `agents/tools/python/my_tool.py`:

```python
"""Custom tool for my_new_agent."""

from typing import Any, Dict


def execute(input_data: str) -> Dict[str, Any]:
    """
    Execute the custom tool logic.
    
    Args:
        input_data: Input string from agent
        
    Returns:
        Dictionary with execution results
    """
    # Implement tool logic
    result = process_input(input_data)
    
    return {
        "status": "success",
        "data": result,
        "metadata": {
            "timestamp": get_timestamp(),
            "version": "1.0.0"
        }
    }


def process_input(data: str) -> Any:
    """Process the input data."""
    # Your implementation here
    return data.upper()


def get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.utcnow().isoformat()
```

### Step 5: Create Test Cases

Edit `agents/evals/golden/my_new_agent_cases.yaml`:

```yaml
test_suite:
  name: my_new_agent_golden_tests
  version: 1.0.0
  
test_cases:
  - id: test_basic_functionality
    input: "Automate file backup"
    expected_output_contains:
      - "backup"
      - "automation"
      - "schedule"
    
  - id: test_error_handling
    input: "Invalid request ####"
    expected_output_contains:
      - "clarification"
      - "requirement"
    
  - id: test_output_format
    input: "Create database backup automation"
    expected_output_schema:
      required_fields:
        - task_analysis
        - proposed_solution
        - implementation_steps
```

### Step 6: Validate the Specification

```bash
./bin/cbw-agent validate agents/specs/my_new_agent.agent.yaml
```

Expected output:
```
✓ Validation passed for my_new_agent v1.0.0
  - Metadata: valid
  - Model policy: valid
  - Tools: 1 tool(s) validated
  - Prompts: system prompt found
  - Runtime: 2 runtime(s) supported
```

### Step 7: Run Evaluations

```bash
./bin/cbw-agent eval agents/specs/my_new_agent.agent.yaml
```

Expected output:
```
Running golden tests for my_new_agent...
✓ test_basic_functionality: PASSED
✓ test_error_handling: PASSED
✓ test_output_format: PASSED

Results: 3/3 tests passed (100%)
```

### Step 8: Test Locally

```bash
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
  --input "Create a Python script backup automation" \
  --runtime local
```

### Step 9: Compile for Production

```bash
./bin/cbw-agent compile agents/specs/my_new_agent.agent.yaml \
  --out dist/agents
```

This generates `dist/agents/my_new_agent.agent.json` - optimized for production execution.

## Agent Architecture

### Base Agent Pattern

All agents follow a common architectural pattern:

```
┌─────────────────────────────────────┐
│         Agent Specification         │
│  (YAML/JSON Configuration)          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│         Runtime Adapter             │
│  (local/crewai/langchain/pydantic)  │
└──────────────┬──────────────────────┘
               │
     ┌─────────┴─────────┐
     ↓                   ↓
┌─────────┐        ┌──────────┐
│  Tools  │        │  Prompts │
└─────────┘        └──────────┘
```

### Agent State Management

Agents can maintain state across interactions:

```python
class StatefulAgent:
    def __init__(self):
        self.state = {
            "conversation_history": [],
            "context": {},
            "metrics": {}
        }
    
    def update_state(self, key: str, value: Any) -> None:
        """Update agent state."""
        self.state[key] = value
    
    def get_state(self, key: str) -> Any:
        """Retrieve state value."""
        return self.state.get(key)
```

### Error Handling

Implement robust error handling in agents:

```python
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def execute_agent_task(task: str) -> Dict[str, Any]:
    """Execute agent task with error handling."""
    try:
        result = process_task(task)
        return {
            "status": "success",
            "result": result
        }
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return {
            "status": "error",
            "error_type": "invalid_input",
            "message": str(e)
        }
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {
            "status": "error",
            "error_type": "internal_error",
            "message": "An unexpected error occurred"
        }
```

## Tool Integration

### Creating Custom Tools

Tools extend agent capabilities. Follow this pattern:

```python
"""Tool module following best practices."""

from typing import Any, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Standard tool result format."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool:
    """Base class for all tools."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize tool with configuration."""
        self.config = config or {}
        self.name = self.__class__.__name__
        logger.info(f"Initialized {self.name}")
    
    def execute(self, input_data: Any) -> ToolResult:
        """
        Execute tool logic.
        
        Args:
            input_data: Input for the tool
            
        Returns:
            ToolResult with success status and data
        """
        try:
            result = self._execute_impl(input_data)
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": self.name}
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def _execute_impl(self, input_data: Any) -> Any:
        """Implement tool-specific logic here."""
        raise NotImplementedError


class FileProcessorTool(BaseTool):
    """Example tool implementation."""
    
    def _execute_impl(self, input_data: Any) -> Dict[str, Any]:
        """Process files based on input."""
        file_path = input_data.get("file_path")
        operation = input_data.get("operation", "read")
        
        if operation == "read":
            return self._read_file(file_path)
        elif operation == "write":
            return self._write_file(file_path, input_data.get("content"))
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents."""
        with open(path, 'r') as f:
            content = f.read()
        return {"content": content, "size": len(content)}
    
    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to file."""
        with open(path, 'w') as f:
            f.write(content)
        return {"bytes_written": len(content)}
```

### Tool Registration

Register tools in `agents/tools/__init__.py`:

```python
"""Tool registry."""

from .file_processor import FileProcessorTool
from .data_analyzer import DataAnalyzerTool
from .api_client import APIClientTool

__all__ = [
    "FileProcessorTool",
    "DataAnalyzerTool",
    "APIClientTool",
]

# Tool registry mapping
TOOL_REGISTRY = {
    "file_processor": FileProcessorTool,
    "data_analyzer": DataAnalyzerTool,
    "api_client": APIClientTool,
}


def get_tool(tool_name: str):
    """Get tool class by name."""
    return TOOL_REGISTRY.get(tool_name)
```

## Model Configuration

### Provider Setup

Configure model providers via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."

# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Model Selection Strategy

Choose models based on agent requirements:

**Fast Response (< 1s):**
- `ollama:qwen2.5-coder` (local)
- `openai:gpt-3.5-turbo` (API)

**High Quality (< 5s):**
- `openai:gpt-4-turbo`
- `anthropic:claude-3-opus`

**Specialized Tasks:**
- Code: `qwen2.5-coder`, `deepseek-coder`
- Analysis: `gpt-4`, `claude-3-opus`
- Fast iteration: `gpt-3.5-turbo`, `mistral-medium`

### Fallback Configuration

Always configure fallbacks for production:

```yaml
model_policy:
  preferred:
    provider: ollama
    model: qwen2.5-coder
  fallbacks:
    - provider: openai
      model: gpt-4-turbo
    - provider: openrouter
      model: meta-llama/llama-3.1-70b-instruct
```

## Testing & Evaluation

### Golden Test Suites

Create comprehensive test cases:

```yaml
test_suite:
  name: code_reviewer_golden_tests
  version: 1.0.0
  description: "Golden tests for code review agent"
  
test_cases:
  # Functional tests
  - id: detect_security_issue
    description: "Agent should detect SQL injection vulnerability"
    input: |
      def get_user(user_id):
          query = f"SELECT * FROM users WHERE id = {user_id}"
          return db.execute(query)
    expected_output_contains:
      - "SQL injection"
      - "parameterized query"
      - "security"
    expected_severity: "critical"
  
  # Edge cases
  - id: handle_empty_input
    description: "Agent should handle empty code gracefully"
    input: ""
    expected_output_contains:
      - "no code"
      - "provide"
  
  # Output format validation
  - id: json_output_format
    description: "Agent should return valid JSON"
    input: "print('hello')"
    expected_output_schema:
      type: "object"
      required: ["findings", "summary"]
```

### Running Evaluations

```bash
# Run all test suites
make eval

# Run specific agent tests
./bin/cbw-agent eval agents/specs/code_reviewer.agent.yaml

# Run with verbose output
./bin/cbw-agent eval agents/specs/code_reviewer.agent.yaml --verbose

# Run and save results
./bin/cbw-agent eval agents/specs/code_reviewer.agent.yaml \
  --output results/code_reviewer_eval.json
```

## Best Practices

### 1. Naming Conventions

**Agent Names:**
- Use lowercase with underscores: `social_media_manager`
- Be descriptive and specific
- Avoid generic names like `agent1`, `helper`

**Tool Names:**
- Use verb_noun format: `analyze_code`, `fetch_data`
- Be action-oriented
- Match the primary function

### 2. Prompt Engineering

**System Prompts:**
- Start with clear role definition
- Include specific responsibilities
- Define output format expectations
- Provide examples for complex tasks
- Keep prompts focused and concise

**User Prompts:**
- Include sufficient context
- Be specific about expected output
- Use structured formats (JSON, YAML) when appropriate

### 3. Error Handling

**Always handle errors gracefully:**

```python
def safe_execute(func, *args, **kwargs):
    """Execute function with error handling."""
    try:
        return {
            "success": True,
            "result": func(*args, **kwargs)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": "invalid_input",
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "internal_error",
            "message": "An error occurred"
        }
```

### 4. Resource Management

**Limit resource usage:**
- Set reasonable timeouts
- Implement rate limiting for API calls
- Clean up resources properly
- Monitor memory usage

### 5. Security

**Security best practices:**
- Never log sensitive data
- Validate all inputs
- Use parameterized queries
- Implement proper authentication
- Follow principle of least privilege

### 6. Performance

**Optimize agent performance:**
- Cache repeated computations
- Use async operations when possible
- Minimize model calls
- Batch operations when appropriate

### 7. Documentation

**Document everything:**
- Inline code comments for complex logic
- Docstrings for all public functions
- README for each agent with usage examples
- Changelog for version tracking

## Advanced Patterns

### Multi-Agent Coordination

Create agents that collaborate:

```yaml
# coordinator_agent.agent.yaml
api_version: v1
kind: Agent
metadata:
  name: coordinator_agent
  version: 1.0.0
spec:
  model_policy:
    preferred:
      provider: openai
      model: gpt-4-turbo
  prompts:
    system: prompts/system/coordinator.md
  tools:
    - id: delegate_task
      type: python
      entrypoint: agents/tools/python/delegation.py:delegate
    - id: aggregate_results
      type: python
      entrypoint: agents/tools/python/aggregation.py:aggregate
  runtime:
    supported: [local, crewai]
```

### Streaming Responses

Support streaming for long-running tasks:

```python
from typing import Iterator

def stream_agent_response(agent, input_data: str) -> Iterator[str]:
    """Stream agent responses as they're generated."""
    for chunk in agent.run_streaming(input_data):
        yield chunk
```

### Agent Composition

Compose agents into workflows:

```yaml
# workflow.yaml
workflow:
  name: content_pipeline
  steps:
    - agent: content_generator
      input: "${user_request}"
      output_var: raw_content
    
    - agent: content_reviewer
      input: "${raw_content}"
      output_var: reviewed_content
    
    - agent: content_publisher
      input: "${reviewed_content}"
      output_var: published_url
```

### Observability Integration

Add tracing and monitoring:

```python
from cbw_foundry.observability.otel import trace_execution

@trace_execution
def execute_agent_task(agent, input_data):
    """Traced agent execution."""
    return agent.run(input_data)
```

## Additional Resources

- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [Runtime Adapters Guide](RUNTIME_ADAPTERS.md)
- [Testing Guide](TESTING_GUIDE.md)
- [API Reference](API.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
