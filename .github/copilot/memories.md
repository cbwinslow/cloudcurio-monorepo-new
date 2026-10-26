# GitHub Copilot Memories

This file contains important patterns, conventions, and lessons learned from the CloudCurio Monorepo codebase. These memories help Copilot provide more contextually accurate suggestions.

## Code Patterns & Conventions

### Agent Module Structure

**Pattern**: All agent modules in `agents/library/` follow a consistent structure:
- Shebang: `#!/usr/bin/env python3`
- Comprehensive module docstring describing purpose and capabilities
- Pydantic configuration models with Field validators
- Main agent class with typed methods
- Clear separation between configuration and execution logic

**Example**:
```python
#!/usr/bin/env python3
"""Agent Name Agent.

This agent provides [specific functionality].

Capabilities:
    - Capability 1
    - Capability 2
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for Agent."""

    model: str = Field(default="qwen2.5-coder")
    timeout: int = Field(default=300, gt=0)


class AgentNameAgent:
    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        self.config = config or AgentConfig()
```

**Why**: This pattern ensures consistency, type safety, and clear documentation across all agent modules.

---

### Message Bus Patterns

**Pattern**: The MessageBus in `src/cbw_foundry/swarm/communication/` uses string topics and matches `MessageType.value` for routing:

```python
# Subscribe expects string topics
bus.subscribe("agent.task.started", handler)

# Broadcast matches topic to MessageType.value
bus.broadcast(MessageType.AGENT_TASK_STARTED, data)
```

**Why**: String-based topic matching provides flexibility while enum-based message types ensure type safety.

**Citation**: `src/cbw_foundry/swarm/communication/__init__.py:65-114`

---

### Runtime Adapter Stub Pattern

**Pattern**: Runtime adapters for CrewAI, PydanticAI, and LangChain return mock stub responses with "adapter stub" notation:

```python
def execute(self, agent_spec: AgentSpec, input_data: dict) -> dict:
    """Execute agent (stub implementation)."""
    return {
        "status": "success",
        "result": "adapter stub - not yet implemented",
        "framework": "crewai",
    }
```

**Why**: Only the Local runtime is fully implemented. Stubs allow testing of the adapter interface while implementation is in progress.

**Citation**: `src/cbw_foundry/runtime/adapters.py:4-17`

---

### Agent Spec Validation

**Pattern**: All agent specs must pass validation before compilation:
1. YAML syntax validation (yamllint)
2. Schema validation (Pydantic models)
3. Tool reference validation
4. Runtime compatibility check

**Command**: `./bin/cbw-agent validate agents/specs/agent_name.agent.yaml`

**Why**: Early validation catches errors before compilation and runtime execution, improving developer experience.

---

### Tool Registration Pattern

**Pattern**: Tools are registered in toolsets and referenced by name in agent specs:

```yaml
# In agent spec
tools:
  - name: github_api
    config:
      token: ${GITHUB_TOKEN}
```

```python
# In tool implementation
class GitHubAPITool:
    name = "github_api"
    description = "GitHub API integration"

    def execute(self, **kwargs) -> dict:
        # Implementation
        pass
```

**Why**: Decouples tool implementation from agent definitions, allowing tool reuse across multiple agents.

---

## Testing Patterns

### Test File Organization

**Pattern**: Tests are organized in `tests/python/` with clear naming:
- `test_imports.py` - Import validation
- `test_toolset.py` - Toolset functionality
- `test_agent_spec.py` - Agent spec validation

**Convention**:
- Test classes use `TestClassName` pattern
- Test methods use `test_specific_behavior` pattern
- Integration tests marked with `@pytest.mark.integration`

---

### Golden Test Structure

**Pattern**: Golden tests in `agents/evals/golden/` define expected agent behavior:

```yaml
name: agent_name_golden_test
version: 1.0.0
cases:
  - input: "test input"
    expected_output: "expected result"
    metadata:
      description: "Test case description"
```

**Why**: Golden tests provide regression detection and quality assurance for agent outputs.

---

## Bootstrap & Environment

### Bootstrap Process

**Pattern**: Bootstrap script (`./scripts/bootstrap.sh`) follows this sequence:
1. Create Python virtual environment
2. Install dependencies via pip
3. Install pre-commit hooks
4. Verify core CLI tools
5. Run initial health checks

**Command**: `./scripts/bootstrap.sh`

**Citation**: `scripts/bootstrap.sh:1-28`

**Why**: Standardized setup ensures consistent development environment across all contributors.

---

### Testing Infrastructure

**Pattern**: Tests run with `make test` or `pytest -q`
- Current status: 13 tests fail due to missing ffmpeg dependency
- Tests are skipped for ffmpeg-dependent functionality

**Citation**: Test execution results, `Makefile:20-21`

**Why**: Missing ffmpeg is a known issue but doesn't block other functionality. Tests gracefully handle missing dependencies.

---

## Documentation Patterns

### Docstring Style

**Pattern**: Use Google-style docstrings with Args, Returns, Raises, Example sections:

```python
def process(items: list[str], threshold: int = 10) -> list[str]:
    """Process items above threshold.

    Args:
        items: List of items to process
        threshold: Minimum threshold value

    Returns:
        Filtered list of items above threshold

    Raises:
        ValueError: If threshold is negative

    Example:
        >>> process(["a", "bb", "ccc"], 2)
        ["bb", "ccc"]
    """
```

**Why**: Consistent documentation style improves code readability and enables automated documentation generation.

---

### YAML Spec Documentation

**Pattern**: Agent specs include inline comments explaining purpose:

```yaml
api_version: v1
kind: Agent
metadata:
  name: agent_name        # lowercase_snake_case identifier
  version: 1.0.0         # Semantic versioning
  tags: [production]     # Classification tags
spec:
  model_policy:
    preferred:
      provider: ollama   # Local-first: use Ollama when possible
      model: qwen2.5-coder  # Coding-focused model
```

**Why**: Inline comments help developers understand spec structure and make appropriate choices.

---

## Error Handling

### Graceful Degradation Pattern

**Pattern**: Code gracefully handles missing optional dependencies:

```python
try:
    import optional_package

    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False


def feature():
    if not HAS_OPTIONAL:
        raise RuntimeError(
            "Feature requires optional_package. Install with: pip install optional_package"
        )
```

**Why**: Allows core functionality to work without all optional dependencies installed.

---

### Pydantic Validation Pattern

**Pattern**: Use Pydantic for all configuration and input validation:

```python
from pydantic import BaseModel, Field, validator


class Config(BaseModel):
    timeout: int = Field(gt=0, le=3600, description="Timeout in seconds")

    @validator("timeout")
    def validate_timeout(cls, v):
        if v < 10:
            raise ValueError("Timeout must be at least 10 seconds")
        return v
```

**Why**: Pydantic provides comprehensive validation with clear error messages and type coercion.

---

## CLI Patterns

### CLI Tool Structure

**Pattern**: CLI tools in `src/cbw_foundry/` follow this structure:
1. Main function returns int (exit code)
2. Use argparse for argument parsing
3. Rich library for terminal output
4. Proper error handling with sys.stderr

```python
def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    try:
        # Logic
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
```

**Why**: Consistent CLI interface improves user experience and enables scripting.

---

## Security Patterns

### Secret Management

**Pattern**: Never commit secrets; use environment variables:

```python
import os

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

**.env.example** pattern:
```
# API Configuration
API_KEY=your_key_here
API_ENDPOINT=https://api.example.com
```

**Why**: Keeps secrets out of version control while providing clear documentation.

---

### Input Sanitization

**Pattern**: Sanitize all user inputs, especially for shell commands and file paths:

```python
import shlex
from pathlib import Path


def safe_command(user_input: str) -> list[str]:
    """Safely parse command from user input."""
    return shlex.split(user_input)


def safe_path(user_path: str, base_dir: Path) -> Path:
    """Resolve path safely within base directory."""
    path = (base_dir / user_path).resolve()
    if not path.is_relative_to(base_dir):
        raise ValueError("Path escapes base directory")
    return path
```

**Why**: Prevents command injection and directory traversal attacks.

---

## Performance Patterns

### Lazy Loading

**Pattern**: Lazy load expensive resources:

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

**Why**: Improves startup time and memory usage by only loading resources when needed.

---

### Async/Await Pattern

**Pattern**: Use async/await for I/O-bound operations in MCP servers:

```python
async def process_file(path: str) -> dict:
    """Process file asynchronously."""
    async with aiofiles.open(path, "r") as f:
        content = await f.read()
    result = await async_process(content)
    return result
```

**Why**: Improves throughput for I/O-bound operations in MCP servers.

---

## Version Control Patterns

### Commit Message Convention

**Pattern**: Use conventional commits format:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: restructure code`
- `chore: update tooling`

**Why**: Enables automated changelog generation and semantic versioning.

---

### Branch Naming

**Pattern**: Use descriptive branch names:
- `feature/agent-discovery-api`
- `fix/validation-error`
- `docs/setup-guide`
- `refactor/runtime-adapters`

**Why**: Clear branch names improve project organization and team communication.

---

## Common Pitfalls to Avoid

### ❌ Don't Use Mutable Default Arguments

```python
# Bad
def append_item(item, items=[]):
    items.append(item)
    return items


# Good
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

### ❌ Don't Import at Module Level for Optional Dependencies

```python
# Bad
import optional_package  # Fails if not installed


# Good
def feature():
    try:
        import optional_package

        return optional_package.do_thing()
    except ImportError:
        raise RuntimeError("Feature requires optional_package")
```

---

### ❌ Don't Hardcode Paths

```python
# Bad
with open("/absolute/path/file.txt") as f:
    pass

# Good
from pathlib import Path

base_dir = Path(__file__).parent
with open(base_dir / "file.txt") as f:
    pass
```

---

## Lessons Learned

### 1. Local-First Approach Works

**Lesson**: Starting with local Ollama models and making cloud services optional reduces friction and costs during development.

**Application**: Always provide a local runtime option; make cloud APIs opt-in via environment variables.

---

### 2. YAML for Specs, JSON for Execution

**Lesson**: Human-authored YAML specs compiled to machine-optimized JSON provides the best of both worlds.

**Application**: Continue the Author (YAML) → Validate → Compile (JSON) → Execute pipeline for all declarative definitions.

---

### 3. Stub Adapters Enable Parallel Development

**Lesson**: Implementing stub adapters for CrewAI/LangChain/PydanticAI allows testing the adapter interface before full implementation.

**Application**: Use stub pattern for incomplete features; mark clearly with "adapter stub" or similar notation.

---

### 4. Pre-commit Hooks Catch Issues Early

**Lesson**: Automated checks via pre-commit hooks (ruff, yamllint, mypy) prevent many issues from reaching CI.

**Application**: Keep pre-commit configuration comprehensive; run `make pre-commit` before committing.

---

### 5. Golden Tests Provide Regression Detection

**Lesson**: Golden test suites with expected outputs help catch regressions in agent behavior.

**Application**: Create golden tests for all agents; update when behavior intentionally changes.

---

## Quick Reference

### Most Common Commands

```bash
# Setup & Health
./scripts/bootstrap.sh
make doctor
make index

# Development
make test
make lint
make fmt
make validate

# Agent Development
./bin/cbw-capture agent name
./bin/cbw-agent validate spec.yaml
./bin/cbw-agent compile spec.yaml --out dist/agents
./bin/cbw-agent run spec.yaml --input "test"
./bin/cbw-agent eval agents/evals/golden/*.yaml

# Pre-commit
make pre-commit
```

### Key Files to Reference

- `pyproject.toml` - Project configuration, dependencies
- `Makefile` - Common commands
- `kb/rules/code_quality_rules.md` - Code standards
- `docs/AGENT_DEVELOPMENT.md` - Agent development guide
- `.pre-commit-config.yaml` - Pre-commit configuration

---

*These memories are continuously updated as the project evolves. Reference them when generating code suggestions to maintain consistency with existing patterns.*
