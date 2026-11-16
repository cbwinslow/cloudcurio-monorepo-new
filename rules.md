# CloudCurio Monorepo - AI Agent Rules

**Version:** 1.0.0
**Last Updated:** 2026-02-13
**Rulebook Framework**: Inspired by rulebook-ai
**Repository:** cloudcurio-monorepo-new

---

## 🎯 Purpose & Philosophy

This rulebook defines the operational rules, best practices, and guidelines for all AI agents working within the CloudCurio Monorepo ecosystem. These rules ensure consistency, quality, and reliability across all AI-assisted development tasks.

### Core Principles

1. **Local-First Development**: Prioritize local tools and resources; make cloud services optional
2. **Type Safety**: Use Python type hints and Pydantic validation throughout
3. **Test-Driven Quality**: Write tests before or alongside code; maintain 80%+ coverage
4. **Documentation First**: Document intent and architecture before implementation
5. **Security by Default**: Never commit secrets; validate all inputs; sanitize outputs
6. **Framework Agnostic**: Support multiple agent frameworks through unified interfaces

---

## 📋 Rule Categories

### 1. Code Quality & Standards

#### 1.1 Python Code Standards

**RULE: PY-001 - Type Hints Required**
- **Priority**: High
- **Description**: All function signatures must include type hints for parameters and return values
- **Example**:
  ```python
  # Good
  def process_data(items: list[dict[str, Any]], threshold: float = 0.8) -> list[dict[str, Any]]:
      pass


  # Bad
  def process_data(items, threshold=0.8):
      pass
  ```
- **Enforcement**: mypy in CI/CD pipeline

**RULE: PY-002 - Pydantic for Configuration**
- **Priority**: High
- **Description**: Use Pydantic BaseModel for all configuration and data validation
- **Example**:
  ```python
  from pydantic import BaseModel, Field


  class AgentConfig(BaseModel):
      model: str = Field(default="qwen2.5-coder")
      timeout: int = Field(gt=0, le=3600)
      temperature: float = Field(ge=0.0, le=1.0)
  ```
- **Why**: Provides automatic validation, type coercion, and clear error messages

**RULE: PY-003 - Docstring Format**
- **Priority**: High
- **Description**: Use Google-style docstrings for all public functions and classes
- **Template**:
  ```python
  def function_name(param: type) -> return_type:
      """Brief description.

      Args:
          param: Parameter description

      Returns:
          Return value description

      Raises:
          ErrorType: When error occurs

      Example:
          >>> function_name(value)
          result
      """
  ```

**RULE: PY-004 - Line Length**
- **Priority**: Medium
- **Description**: Maximum 100 characters per line
- **Enforcement**: ruff formatter in pre-commit hooks

**RULE: PY-005 - Naming Conventions**
- **Priority**: High
- **Description**:
  - Files: `lowercase_with_underscores.py`
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private: `_leading_underscore`

**RULE: PY-006 - Import Organization**
- **Priority**: Medium
- **Description**: Organize imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- **Example**:
  ```python
  import os
  import sys
  from typing import Any

  from pydantic import BaseModel
  import yaml

  from cbw_foundry.runtime import LocalRuntime
  from cbw_foundry.spec import AgentSpec
  ```

#### 1.2 YAML Standards

**RULE: YAML-001 - Agent Spec Format**
- **Priority**: High
- **Description**: Agent specifications must follow the v1 schema
- **Template**:
  ```yaml
  api_version: v1
  kind: Agent
  metadata:
    name: agent_name        # lowercase_snake_case
    version: 1.0.0          # Semantic versioning
    tags: [domain, type]    # Classification tags
  spec:
    model_policy:
      preferred:
        provider: ollama    # Local-first
        model: qwen2.5-coder
      fallbacks: []
    prompts:
      system: path/to/prompt.md
    tools: []
    runtime:
      supported: [local]
    eval:
      suites: []
  ```

**RULE: YAML-002 - Indentation**
- **Priority**: High
- **Description**: Use 2 spaces for indentation (never tabs)
- **Enforcement**: yamllint in pre-commit hooks

**RULE: YAML-003 - Comments**
- **Priority**: Medium
- **Description**: Add inline comments for non-obvious configuration choices
- **Example**:
  ```yaml
  spec:
    model_policy:
      preferred:
        provider: ollama   # Local-first: use Ollama when possible
        model: qwen2.5-coder  # Coding-focused model for development tasks
  ```

### 2. Testing & Quality Assurance

**RULE: TEST-001 - Coverage Requirements**
- **Priority**: High
- **Description**:
  - Minimum 80% code coverage for all new code
  - 100% coverage for security-sensitive code
  - All public APIs must have tests

**RULE: TEST-002 - Test Organization**
- **Priority**: High
- **Description**:
  - Unit tests in `tests/python/`
  - Integration tests marked with `@pytest.mark.integration`
  - Golden tests in `agents/evals/golden/`
- **File naming**: `test_module_name.py`

**RULE: TEST-003 - Test Structure**
- **Priority**: Medium
- **Description**: Follow Arrange-Act-Assert pattern
- **Example**:
  ```python
  def test_process_data():
      # Arrange
      data = [{"score": 0.9}, {"score": 0.5}]
      threshold = 0.7

      # Act
      result = process_data(data, threshold)

      # Assert
      assert len(result) == 1
      assert result[0]["score"] == 0.9
  ```

**RULE: TEST-004 - Golden Tests**
- **Priority**: High
- **Description**: Create golden test suites for all agents to detect regressions
- **Location**: `agents/evals/agent_name/`

**RULE: TEST-005 - Pre-commit Validation**
- **Priority**: High
- **Description**: All code must pass pre-commit hooks before committing
- **Command**: `make pre-commit`
- **Checks**: ruff lint, ruff format, mypy, yamllint, trailing whitespace

### 3. Security & Privacy

**RULE: SEC-001 - No Secrets in Code**
- **Priority**: Critical
- **Description**: Never commit secrets, API keys, passwords, or tokens
- **Implementation**:
  - Use environment variables for sensitive data
  - Store in `.env` files (git-ignored)
  - Provide `.env.example` for documentation
  - Weekly gitleaks scanning in CI

**RULE: SEC-002 - Input Validation**
- **Priority**: High
- **Description**: Validate all user inputs using Pydantic
- **Example**:
  ```python
  from pydantic import BaseModel, validator


  class UserInput(BaseModel):
      path: str
      timeout: int

      @validator("timeout")
      def validate_timeout(cls, v):
          if v < 1 or v > 3600:
              raise ValueError("Timeout must be 1-3600 seconds")
          return v
  ```

**RULE: SEC-003 - Path Sanitization**
- **Priority**: High
- **Description**: Sanitize file paths to prevent directory traversal
- **Example**:
  ```python
  from pathlib import Path


  def safe_path(user_path: str, base_dir: Path) -> Path:
      path = (base_dir / user_path).resolve()
      if not path.is_relative_to(base_dir):
          raise ValueError("Path escapes base directory")
      return path
  ```

**RULE: SEC-004 - Command Injection Prevention**
- **Priority**: High
- **Description**: Use `shlex.split()` for shell command parsing
- **Example**:
  ```python
  import shlex
  import subprocess

  user_input = "file.txt"
  cmd = shlex.split(f"cat {user_input}")
  subprocess.run(cmd, check=True)
  ```

**RULE: SEC-005 - Dependency Security**
- **Priority**: Medium
- **Description**:
  - Keep dependencies updated
  - Use exact versions in requirements
  - Run pip-audit regularly
  - Review security advisories

### 4. Agent Development

**RULE: AGENT-001 - Agent Naming**
- **Priority**: High
- **Description**:
  - Agent names: `lowercase_snake_case`
  - Spec files: `agent_name.agent.yaml`
  - Module files: `agent_name_agent.py`

**RULE: AGENT-002 - Agent Module Structure**
- **Priority**: High
- **Description**: Follow standard agent module pattern
- **Template**:
  ```python
  #!/usr/bin/env python3
  """Agent Name Agent.

  Description of agent purpose and capabilities.

  Capabilities:
      - Capability 1
      - Capability 2

  Example:
      from agents.library.agent_name_agent import AgentNameAgent
      agent = AgentNameAgent()
      result = agent.execute(task="process this")
  """

  from typing import Any, Optional
  from pydantic import BaseModel, Field


  class AgentConfig(BaseModel):
      """Configuration for AgentName."""

      model: str = Field(default="qwen2.5-coder")
      timeout: int = Field(default=300, gt=0)


  class AgentNameAgent:
      """Agent for specific purpose."""

      def __init__(self, config: Optional[AgentConfig] = None) -> None:
          self.config = config or AgentConfig()

      def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
          """Execute agent task."""
          if not task:
              raise ValueError("Task cannot be empty")
          return {"status": "success", "result": "Task completed"}
  ```

**RULE: AGENT-003 - Model Selection**
- **Priority**: High
- **Description**: Prioritize local models; use cloud as fallback
- **Preferred**:
  1. `ollama` with `qwen2.5-coder` (local coding tasks)
  2. `openrouter` with `qwen/qwen-2.5-coder-32b-instruct` (fallback)
  3. `openai` with `gpt-4-turbo` (second fallback)

**RULE: AGENT-004 - Agent Lifecycle**
- **Priority**: High
- **Description**: Follow the standard agent development lifecycle
- **Steps**:
  1. **Create**: Scaffold with `./bin/cbw-capture agent name`
  2. **Author**: Write YAML spec in `agents/specs/`
  3. **Validate**: Run `./bin/cbw-agent validate spec.yaml`
  4. **Test**: Create golden tests in `agents/evals/`
  5. **Compile**: Generate JSON with `./bin/cbw-agent compile`
  6. **Execute**: Run with `./bin/cbw-agent run`
  7. **Evaluate**: Test quality with `./bin/cbw-agent eval`

**RULE: AGENT-005 - Error Handling**
- **Priority**: High
- **Description**: Implement graceful error handling
- **Pattern**:
  ```python
  def execute(self, task: str) -> dict[str, Any]:
      try:
          result = self._process(task)
          return {"status": "success", "result": result}
      except ValidationError as e:
          return {"status": "error", "error": str(e), "type": "validation"}
      except TimeoutError as e:
          return {"status": "error", "error": "Execution timeout", "type": "timeout"}
      except Exception as e:
          return {"status": "error", "error": str(e), "type": "unknown"}
  ```

### 5. Tool Development

**RULE: TOOL-001 - Tool Interface**
- **Priority**: High
- **Description**: Tools must implement standard interface
- **Required attributes**:
  - `name: str` - Tool identifier
  - `description: str` - Brief description for agent use
- **Required methods**:
  - `execute(**kwargs) -> dict[str, Any]` - Tool execution

**RULE: TOOL-002 - Tool Configuration**
- **Priority**: High
- **Description**: Use Pydantic for tool configuration
- **Example**:
  ```python
  class ToolConfig(BaseModel):
      api_key: str = Field(description="API key for service")
      timeout: int = Field(default=30, gt=0)
      retries: int = Field(default=3, ge=0, le=10)
  ```

**RULE: TOOL-003 - Tool Registration**
- **Priority**: Medium
- **Description**: Register tools in `agents/tools/__init__.py`
- **Example**:
  ```python
  from .github_api import GitHubAPITool
  from .file_processor import FileProcessorTool

  __all__ = ["GitHubAPITool", "FileProcessorTool"]
  ```

### 6. Documentation

**RULE: DOC-001 - README Standards**
- **Priority**: High
- **Description**: Every module/package must have a README
- **Sections**:
  - Overview/Purpose
  - Installation/Setup
  - Usage Examples
  - Configuration Options
  - Troubleshooting

**RULE: DOC-002 - Architecture Decision Records**
- **Priority**: Medium
- **Description**: Document significant architectural decisions in `kb/decisions/`
- **Template**:
  ```markdown
  # ADR-XXX: Title

  ## Status
  Accepted / Proposed / Deprecated

  ## Context
  What is the issue we're seeing?

  ## Decision
  What is the change we're proposing?

  ## Consequences
  What becomes easier/harder?
  ```

**RULE: DOC-003 - Runbook Standards**
- **Priority**: Medium
- **Description**: Operational procedures in `kb/runbooks/`
- **Sections**:
  - Purpose
  - Prerequisites
  - Step-by-step instructions
  - Troubleshooting
  - Related documentation

**RULE: DOC-004 - API Documentation**
- **Priority**: Medium
- **Description**: Document public APIs in `docs/API.md`
- **Include**:
  - Function signatures
  - Parameter descriptions
  - Return values
  - Usage examples
  - Error conditions

### 7. Version Control & CI/CD

**RULE: VCS-001 - Commit Message Format**
- **Priority**: High
- **Description**: Use conventional commits format
- **Format**: `<type>: <description>`
- **Types**:
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `docs:` - Documentation changes
  - `test:` - Test additions/changes
  - `refactor:` - Code restructuring
  - `chore:` - Maintenance tasks
- **Example**: `feat: add github api integration tool`

**RULE: VCS-002 - Branch Naming**
- **Priority**: Medium
- **Description**: Use descriptive branch names
- **Format**: `<type>/<description>`
- **Examples**:
  - `feature/agent-discovery-api`
  - `fix/validation-error`
  - `docs/setup-guide`

**RULE: VCS-003 - Pull Request Requirements**
- **Priority**: High
- **Description**: PRs must meet these criteria
- **Requirements**:
  - ✅ Passing CI checks (lint, test, type-check)
  - ✅ Code review approval
  - ✅ Documentation updates (if adding features)
  - ✅ Test coverage maintained/improved
  - ✅ No secrets committed

**RULE: VCS-004 - Gitignore Management**
- **Priority**: High
- **Description**: Keep generated artifacts out of version control
- **Always ignore**:
  - `.env` files
  - `__pycache__/` directories
  - `*.pyc` files
  - `dist/` build artifacts
  - `.pytest_cache/`
  - `.mypy_cache/`
  - IDE-specific files (`.vscode/`, `.idea/`)

### 8. Performance & Optimization

**RULE: PERF-001 - Lazy Loading**
- **Priority**: Medium
- **Description**: Lazy load expensive resources
- **Example**:
  ```python
  class Agent:
      def __init__(self):
          self._model = None

      @property
      def model(self):
          if self._model is None:
              self._model = load_expensive_model()
          return self._model
  ```

**RULE: PERF-002 - Async for I/O**
- **Priority**: Medium
- **Description**: Use async/await for I/O-bound operations
- **When**: File operations, network requests, database queries
- **Example**:
  ```python
  async def process_file(path: str) -> dict:
      async with aiofiles.open(path, "r") as f:
          content = await f.read()
      return await process_content(content)
  ```

**RULE: PERF-003 - Resource Cleanup**
- **Priority**: High
- **Description**: Always clean up resources
- **Pattern**:
  ```python
  # Use context managers
  with open(file_path) as f:
      process(f)


  # Or implement __enter__/__exit__
  class Resource:
      def __enter__(self):
          self.acquire()
          return self

      def __exit__(self, *args):
          self.release()
  ```

### 9. Workflow & Orchestration

**RULE: WORKFLOW-001 - YAML Workflow Format**
- **Priority**: High
- **Description**: Workflows must follow standard format
- **Template**:
  ```yaml
  name: workflow_name
  version: 1.0.0
  description: Workflow purpose

  steps:
    - name: step_name
      agent: agent_name
      input: ${previous_step.output}
      config:
        timeout: 300
      dependencies: []
  ```

**RULE: WORKFLOW-002 - Step Dependencies**
- **Priority**: High
- **Description**: Explicitly declare step dependencies
- **Example**:
  ```yaml
  steps:
    - name: fetch_data
      agent: data_fetcher
      input: "source_url"

    - name: process_data
      agent: data_processor
      input: ${fetch_data.result}
      dependencies: [fetch_data]
  ```

### 10. MCP Server Development

**RULE: MCP-001 - Server Structure**
- **Priority**: High
- **Description**: MCP servers in `mcp-servers/server_name/`
- **Required files**:
  - `__init__.py` - Server implementation
  - `README.md` - Server documentation
  - `requirements.txt` - Dependencies

**RULE: MCP-002 - Tool Registration**
- **Priority**: High
- **Description**: Register tools with decorators
- **Example**:
  ```python
  from mcp import Server


  class MyMCPServer(Server):
      def __init__(self):
          super().__init__(name="my-server", version="1.0.0")
          self.register_tools()

      def register_tools(self):
          @self.tool("tool_name")
          async def tool_name(param: str) -> dict:
              return {"result": "success"}
  ```

**RULE: MCP-003 - Error Handling**
- **Priority**: High
- **Description**: MCP servers must handle errors gracefully
- **Pattern**:
  ```python
  async def tool_execute(**kwargs):
      try:
          result = await process()
          return {"status": "success", "result": result}
      except Exception as e:
          return {"status": "error", "error": str(e)}
  ```

---

## 🔧 Common Commands Reference

### Setup & Health
```bash
./scripts/bootstrap.sh    # Initial setup
make doctor              # Health check
make index               # Generate registries
```

### Development
```bash
make test                # Run test suite
make lint                # Lint code
make fmt                 # Format code
make validate            # Validate agent specs
make compile             # Compile specs to JSON
make eval                # Run golden tests
make pre-commit          # Run pre-commit hooks
```

### Agent Development
```bash
./bin/cbw-capture agent name              # Scaffold new agent
./bin/cbw-agent validate spec.yaml        # Validate spec
./bin/cbw-agent compile spec.yaml --out dist/agents  # Compile
./bin/cbw-agent run spec.yaml --input "test"  # Run agent
./bin/cbw-agent eval agents/evals/golden/*.yaml  # Evaluate
```

---

## 📊 Quality Metrics

All code must meet these quality thresholds:

| Metric | Requirement | Enforcement |
|--------|-------------|-------------|
| Test Coverage | ≥ 80% | pytest-cov |
| Type Coverage | 100% public APIs | mypy |
| Linting | No errors | ruff |
| Format | Consistent | ruff format |
| YAML Validation | Valid syntax | yamllint |
| Security Scan | No secrets | gitleaks |

---

## 🚨 Common Pitfalls to Avoid

### ❌ Mutable Default Arguments
```python
# Bad
def append(item, items=[]):
    items.append(item)


# Good
def append(item, items=None):
    if items is None:
        items = []
    items.append(item)
```

### ❌ Hardcoded Paths
```python
# Bad
with open("/absolute/path/file.txt") as f:
    pass

# Good
from pathlib import Path

base = Path(__file__).parent
with open(base / "file.txt") as f:
    pass
```

### ❌ Missing Error Handling
```python
# Bad
def process():
    result = risky_operation()
    return result


# Good
def process():
    try:
        result = risky_operation()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## 📚 Additional Resources

- **Documentation**: See `docs/` directory for comprehensive guides
- **Knowledge Base**: See `kb/` for runbooks, decisions, and rules
- **Examples**: Reference implementations in `agents/specs/examples/`
- **Code Quality Rules**: See `kb/rules/code_quality_rules.md`

---

## 🔄 Rule Updates

This rulebook is a living document. To propose changes:

1. Open an issue with `[RULE]` prefix
2. Discuss in team/community
3. Submit PR with rule changes
4. Update version number and last updated date

---

**Version:** 1.0.0
**Maintained by:** @cbwinslow
**Last Updated:** 2026-02-13

*These rules ensure consistent, high-quality AI-assisted development across the CloudCurio Monorepo ecosystem.*
