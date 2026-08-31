# GitHub Copilot Instructions for CloudCurio Monorepo

**Version:** 1.0.0
**Last Updated:** 2026-02-13
**Repository:** CloudCurio Monorepo (Master Toolbox)

## Repository Overview

CloudCurio Monorepo is a comprehensive AI agent framework and tooling ecosystem designed for production-grade automation. This repository provides:

- **Multi-Framework Agent Support**: CrewAI, PydanticAI, LangChain, and custom swarm systems
- **Declarative Agent Specs**: Define agents in human-friendly YAML, compile to machine-optimized JSON
- **Tool Ecosystem**: Extensive library of pre-built tools for content creation, automation, and system integration
- **Workflow Orchestration**: YAML-based workflow definitions for repeatable automation
- **Local-First Architecture**: Everything runs locally without external dependencies

## Code Generation Guidelines

### General Principles

1. **Follow Python 3.11+ Standards**: Use modern Python features including type hints, match statements, and dataclasses
2. **Type Safety First**: All function signatures must include type hints for parameters and return values
3. **Pydantic for Validation**: Use Pydantic models for configuration and data validation
4. **Local-First Development**: Avoid external API dependencies; make paid services optional
5. **Framework Agnostic**: Support multiple runtime adapters through unified interfaces

### Code Style & Formatting

- **Line Length**: 100 characters maximum (configured in pyproject.toml)
- **Linter**: Use `ruff` for linting and formatting
- **Type Checker**: Use `mypy` for static type checking
- **Naming Conventions**:
  - Files: `lowercase_with_underscores.py`
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Agent specs: `agent_name.agent.yaml`

### Documentation Standards

#### Docstrings

Use Google-style docstrings for all functions and classes:

```python
def process_data(items: list[dict[str, Any]], threshold: float = 0.8) -> list[dict[str, Any]]:
    """Process data items above a threshold.

    Args:
        items: List of data dictionaries to process
        threshold: Minimum confidence threshold (0.0-1.0)

    Returns:
        List of filtered data items above threshold

    Raises:
        ValueError: If threshold is not between 0.0 and 1.0

    Example:
        >>> data = [{"score": 0.9, "name": "test"}]
        >>> process_data(data, 0.8)
        [{"score": 0.9, "name": "test"}]
    """
```

#### Module Docstrings

Every Python module should start with:

```python
#!/usr/bin/env python3
"""Module description.

This module provides [brief description of functionality].

Example:
    Basic usage example::

        from module_name import ClassName
        obj = ClassName()
        result = obj.method()
"""
```

### Agent Development

#### Agent Specification Format (YAML)

```yaml
api_version: v1
kind: Agent
metadata:
  name: agent_name              # lowercase_snake_case
  version: 1.0.0                # Semantic versioning
  tags: [domain, type]          # Classification tags
spec:
  model_policy:
    preferred:
      provider: ollama           # Local-first: ollama preferred
      model: qwen2.5-coder      # Coding-focused model
    fallbacks:
      - provider: openrouter     # Fallback to cloud if needed
        model: qwen/qwen-2.5-coder-32b-instruct
  prompts:
    system: prompts/agent_name_system.md
  tools:
    - name: tool_name
      config: {}
  runtime:
    supported: [local, langchain, crewai]
  eval:
    suites:
      - agents/evals/agent_name/golden_test.yaml
```

#### Agent Implementation Pattern

When creating agent modules in `agents/library/`:

```python
#!/usr/bin/env python3
"""Agent Name Agent.

This agent provides [specific functionality description].

Capabilities:
    - Capability 1
    - Capability 2
    - Capability 3

Example:
    Basic usage::

        from agents.library.agent_name_agent import AgentNameAgent
        agent = AgentNameAgent()
        result = agent.execute(task="process this")
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for AgentName agent."""

    model: str = Field(default="qwen2.5-coder", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Model temperature")
    timeout: int = Field(default=300, gt=0, description="Execution timeout in seconds")


class AgentNameAgent:
    """Agent for [specific purpose]."""

    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        """Initialize the agent.

        Args:
            config: Agent configuration, uses defaults if None
        """
        self.config = config or AgentConfig()

    def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Execute the agent task.

        Args:
            task: Task description
            **kwargs: Additional task parameters

        Returns:
            Execution result dictionary

        Raises:
            ValueError: If task is empty or invalid
        """
        if not task:
            raise ValueError("Task cannot be empty")

        # Implementation
        return {"status": "success", "result": "Task completed", "metadata": {}}
```

### Tool Development

#### Tool Implementation Pattern

Tools should follow this structure in `agents/tools/`:

```python
#!/usr/bin/env python3
"""Tool Name Tool.

Description of what this tool does and when to use it.
"""

from typing import Any
from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """Configuration for ToolName."""

    option1: str = Field(description="First configuration option")
    option2: bool = Field(default=True, description="Second configuration option")


class ToolName:
    """Tool for [specific purpose]."""

    name: str = "tool_name"
    description: str = "Brief description for agent use"

    def __init__(self, config: ToolConfig) -> None:
        """Initialize tool with configuration."""
        self.config = config

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute tool operation.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        # Implementation
        return {"status": "success"}
```

### Testing Standards

#### Test File Structure

```python
"""Tests for module_name.

Test suite for [component description].
"""

import pytest
from module_name import ClassName


class TestClassName:
    """Test suite for ClassName."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality works as expected."""
        obj = ClassName()
        result = obj.method()
        assert result is not None

    def test_error_handling(self) -> None:
        """Test error handling for invalid input."""
        obj = ClassName()
        with pytest.raises(ValueError, match="Expected error message"):
            obj.method(invalid_param=True)

    @pytest.mark.integration
    def test_integration_scenario(self) -> None:
        """Test integration with external systems."""
        # Integration test implementation
        pass
```

#### Test Coverage Requirements

- **Minimum Coverage**: 80% for all new code
- **Critical Paths**: 100% coverage for security-sensitive code
- **Test Types**:
  - Unit tests for all public methods
  - Integration tests for external interactions
  - Golden tests for agent behavior validation

### Security Best Practices

1. **Never Commit Secrets**:
   - Use environment variables for API keys
   - Store sensitive data in `.env` files (git-ignored)
   - Use `.env.example` files for documentation

2. **Input Validation**:
   - Validate all user inputs with Pydantic
   - Sanitize file paths and shell commands
   - Use parameterized queries for databases

3. **Dependency Management**:
   - Keep dependencies updated regularly
   - Use exact versions in requirements
   - Scan for vulnerabilities with `pip-audit`

4. **Error Handling**:
   - Never expose sensitive data in error messages
   - Log errors securely (avoid logging secrets)
   - Provide user-friendly error messages

### Workflow & YAML Specifications

#### Workflow Definition Format

```yaml
name: workflow_name
version: 1.0.0
description: Workflow purpose and use case

steps:
  - name: step_name
    agent: agent_name
    input: ${previous_step.output}
    config:
      timeout: 300

  - name: next_step
    agent: another_agent
    input: ${step_name.result}
    dependencies: [step_name]
```

### CLI Tool Development

When creating CLI tools in `src/cbw_foundry/`:

```python
#!/usr/bin/env python3
"""CLI tool description.

Command-line tool for [purpose].
"""

import argparse
import sys
from typing import Optional


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Tool description", formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", required=True, help="Input parameter")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        # CLI logic
        print("Success")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### MCP Server Development

#### MCP Server Structure

MCP servers should be in `mcp-servers/server_name/`:

```python
"""MCP Server Name.

Model Context Protocol server for [purpose].

Capabilities:
    - Capability 1
    - Capability 2
"""

from typing import Any
from mcp import Server, Tool


class ServerNameMCP(Server):
    """MCP server for [specific purpose]."""

    def __init__(self) -> None:
        """Initialize MCP server."""
        super().__init__(name="server-name", version="1.0.0")
        self.register_tools()

    def register_tools(self) -> None:
        """Register available tools."""

        @self.tool("tool_name")
        async def tool_name(param: str) -> dict[str, Any]:
            """Tool description.

            Args:
                param: Parameter description

            Returns:
                Tool result
            """
            return {"result": "success"}
```

### Pre-commit Hooks

All code must pass pre-commit hooks before committing:

```bash
# Run manually
make pre-commit

# Hooks include:
# - ruff check (linting)
# - ruff format (formatting)
# - mypy (type checking)
# - yamllint (YAML validation)
# - trailing whitespace removal
```

### CI/CD Integration

#### GitHub Actions Workflow Pattern

```yaml
name: Workflow Name
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest -q

      - name: Lint
        run: ruff check .
```

### Project Structure Conventions

```
cloudcurio-monorepo/
├── agents/                    # Agent ecosystem
│   ├── library/              # Pre-built agent modules
│   ├── specs/                # YAML agent specifications
│   ├── evals/                # Golden test suites
│   ├── tools/                # Reusable tool implementations
│   └── toolsets/             # Domain-specific collections
├── src/cbw_foundry/          # Core Python framework
│   ├── cli/                  # CLI tools
│   ├── runtime/              # Runtime adapters
│   └── spec/                 # Spec compiler
├── workflows/                # YAML workflow definitions
├── mcp-servers/              # Model Context Protocol servers
├── kb/                       # Knowledge base
│   ├── runbooks/            # Operational procedures
│   ├── decisions/           # Architecture Decision Records
│   └── rules/               # Code quality guidelines
├── docs/                     # User-facing documentation
├── tests/                    # Python test suite
└── scripts/                  # Utility scripts
```

### Common Tasks

#### Creating a New Agent

```bash
# Scaffold new agent
./bin/cbw-capture agent my_new_agent

# Validate specification
./bin/cbw-agent validate agents/specs/my_new_agent.agent.yaml

# Compile to JSON
./bin/cbw-agent compile agents/specs/my_new_agent.agent.yaml --out dist/agents

# Run locally
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml --input "test"
```

#### Running Tests

```bash
# Full test suite
make test

# Specific test file
pytest tests/test_specific.py

# With coverage
pytest --cov=cbw_foundry tests/

# Integration tests only
pytest -m integration
```

#### Code Quality Checks

```bash
# Lint code
make lint

# Auto-fix formatting
make fmt

# Type check
mypy src

# Full validation
make validate
```

### Troubleshooting Guide

#### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and package is installed with `pip install -e .`
2. **YAML Validation Errors**: Check indentation (use 2 spaces) and quote strings with special characters
3. **Type Check Errors**: Add proper type hints and ensure imports are from `typing` module
4. **Test Failures**: Check for unset environment variables and missing test fixtures

### Additional Resources

- **Documentation**: See `docs/` directory for comprehensive guides
- **Examples**: Reference implementations in `agents/specs/examples/`
- **Runbooks**: Operational guides in `kb/runbooks/`
- **Code Quality Rules**: See `kb/rules/code_quality_rules.md`

### Contact & Support

- **Issues**: Report bugs via GitHub Issues
- **Maintainer**: @cbwinslow
- **Version**: v0.4.0

---

*These instructions are for GitHub Copilot to generate context-aware code suggestions. Follow these patterns for consistent, high-quality contributions to the CloudCurio Monorepo.*
