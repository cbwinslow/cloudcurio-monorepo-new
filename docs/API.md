# CloudCurio Framework API Reference

Comprehensive API documentation for the `cbw_foundry` Python package.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Modules](#core-modules)
- [CLI Modules](#cli-modules)
- [Runtime System](#runtime-system)
- [Specification System](#specification-system)
- [Observability](#observability)
- [Utilities](#utilities)
- [Usage Examples](#usage-examples)

## Overview

The `cbw_foundry` package is the core framework for CloudCurio, providing:

- **Agent Specification System**: Define and validate agent specs
- **Runtime Adapters**: Execute agents across multiple frameworks
- **CLI Tools**: Command-line interface for operations
- **Observability**: OpenTelemetry integration
- **Evaluation**: Golden test harness

### Package Structure

```
cbw_foundry/
├── cli.py              # Main CLI entry point
├── agent_cli.py        # Agent operations CLI
├── workflow_cli.py     # Workflow operations CLI
├── doctor_cli.py       # Health check CLI
├── capture_cli.py      # Scaffolding CLI
├── index_cli.py        # Registry management CLI
├── runtime/            # Runtime adapters
│   ├── base.py         # Abstract runtime interface
│   ├── local_runtime.py # Local execution
│   ├── adapters.py     # Framework bridges
│   ├── stubs.py        # Framework stubs
│   └── registry.py     # Component registration
├── spec/               # Specification system
│   ├── models.py       # Pydantic schemas
│   ├── io.py           # File I/O
│   └── compiler.py     # YAML→JSON compiler
├── observability/      # Monitoring
│   └── otel.py         # OpenTelemetry
├── evals/              # Evaluation
│   └── runner.py       # Test runner
└── util/               # Utilities
    └── fs.py           # Filesystem helpers
```

## Installation

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"

# In a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Core Modules

### cbw_foundry.spec.models

Pydantic models for agent specifications.

#### AgentSpec

```python
from cbw_foundry.spec.models import AgentSpec

class AgentSpec(BaseModel):
    """Agent specification model."""
    
    name: str                    # Unique identifier
    version: str                 # Semantic version
    description: str             # Brief description
    system_prompt: str           # Core instructions
    tools: List[ToolSpec] = []   # Tool configurations
    runtime: RuntimeConfig       # Runtime settings
    metadata: Optional[Dict] = None  # Additional info
```

**Fields:**

- `name` (str, required): Unique agent identifier (lowercase, underscores)
- `version` (str, required): Semantic version (X.Y.Z format)
- `description` (str, required): One-line description for registry
- `system_prompt` (str, required): Instructions for agent behavior
- `tools` (List[ToolSpec], optional): Tools the agent can use
- `runtime` (RuntimeConfig, required): Execution configuration
- `metadata` (dict, optional): Custom metadata

**Example:**

```python
from cbw_foundry.spec.models import AgentSpec, RuntimeConfig

spec = AgentSpec(
    name="my_agent",
    version="1.0.0",
    description="My custom agent",
    system_prompt="You are a helpful agent.",
    runtime=RuntimeConfig(
        framework="local",
        model="gpt-4"
    )
)
```

#### ToolSpec

```python
from cbw_foundry.spec.models import ToolSpec

class ToolSpec(BaseModel):
    """Tool specification model."""
    
    name: str                    # Tool identifier
    description: str             # What the tool does
    required: bool = False       # Whether tool is required
    config: Optional[Dict] = {}  # Tool-specific config
```

**Example:**

```python
from cbw_foundry.spec.models import ToolSpec

tool = ToolSpec(
    name="web_search",
    description="Search the web for information",
    required=True,
    config={"max_results": 10}
)
```

#### RuntimeConfig

```python
from cbw_foundry.spec.models import RuntimeConfig

class RuntimeConfig(BaseModel):
    """Runtime configuration model."""
    
    framework: str               # local, crewai, langchain, pydanticai
    model: str = "gpt-4"        # LLM model
    temperature: float = 0.7     # Creativity (0.0-1.0)
    max_tokens: int = 2000      # Max response length
    timeout: int = 300          # Timeout in seconds
```

**Example:**

```python
from cbw_foundry.spec.models import RuntimeConfig

config = RuntimeConfig(
    framework="local",
    model="gpt-4",
    temperature=0.5,
    max_tokens=1000,
    timeout=600
)
```

### cbw_foundry.spec.io

File I/O operations for agent specifications.

#### load_agent_spec()

```python
from cbw_foundry.spec.io import load_agent_spec

def load_agent_spec(path: str) -> AgentSpec:
    """
    Load agent specification from YAML file.
    
    Args:
        path: Path to YAML file
        
    Returns:
        AgentSpec: Parsed and validated spec
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If spec is invalid
    """
```

**Example:**

```python
from cbw_foundry.spec.io import load_agent_spec

spec = load_agent_spec("agents/specs/my_agent.agent.yaml")
print(f"Loaded agent: {spec.name} v{spec.version}")
```

#### save_agent_spec()

```python
from cbw_foundry.spec.io import save_agent_spec

def save_agent_spec(spec: AgentSpec, path: str) -> None:
    """
    Save agent specification to YAML file.
    
    Args:
        spec: Agent specification
        path: Output file path
    """
```

**Example:**

```python
from cbw_foundry.spec.io import save_agent_spec

save_agent_spec(spec, "agents/specs/my_agent.agent.yaml")
```

### cbw_foundry.spec.compiler

Compile YAML specs to optimized JSON artifacts.

#### compile_agent()

```python
from cbw_foundry.spec.compiler import compile_agent

def compile_agent(
    yaml_path: str,
    json_path: str,
    optimize: bool = True
) -> None:
    """
    Compile agent spec from YAML to JSON.
    
    Args:
        yaml_path: Input YAML file
        json_path: Output JSON file
        optimize: Apply optimizations
    """
```

**Example:**

```python
from cbw_foundry.spec.compiler import compile_agent

compile_agent(
    yaml_path="agents/specs/my_agent.agent.yaml",
    json_path="dist/agents/my_agent.agent.json",
    optimize=True
)
```

## CLI Modules

### cbw_foundry.cli

Main CLI entry point.

```python
from cbw_foundry.cli import cli

@click.group()
def cli():
    """CloudCurio CLI."""
    pass
```

### cbw_foundry.agent_cli

Agent operations.

#### validate_agent()

```python
from cbw_foundry.agent_cli import validate_agent

def validate_agent(spec_path: str, verbose: bool = False) -> bool:
    """
    Validate agent specification.
    
    Args:
        spec_path: Path to agent YAML file
        verbose: Show detailed errors
        
    Returns:
        bool: True if valid, False otherwise
    """
```

#### compile_agent_cli()

```python
from cbw_foundry.agent_cli import compile_agent_cli

def compile_agent_cli(
    spec_path: str,
    output_dir: str = "dist/agents"
) -> None:
    """Compile agent to JSON."""
```

#### run_agent()

```python
from cbw_foundry.agent_cli import run_agent

def run_agent(
    spec_path: str,
    input_text: str,
    runtime: str = "local",
    verbose: bool = False
) -> str:
    """
    Run agent with input.
    
    Args:
        spec_path: Agent specification path
        input_text: Input to agent
        runtime: Runtime to use (local, crewai, etc.)
        verbose: Enable verbose output
        
    Returns:
        str: Agent output
    """
```

#### eval_agent()

```python
from cbw_foundry.agent_cli import eval_agent

def eval_agent(
    spec_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run golden test suite for agent.
    
    Args:
        spec_path: Agent specification path
        verbose: Show detailed results
        
    Returns:
        dict: Test results with pass/fail counts
    """
```

## Runtime System

### cbw_foundry.runtime.base

Abstract runtime interface.

#### BaseRuntime

```python
from cbw_foundry.runtime.base import BaseRuntime
from abc import ABC, abstractmethod

class BaseRuntime(ABC):
    """Base class for all runtime adapters."""
    
    @abstractmethod
    def run(
        self,
        spec: AgentSpec,
        input: str,
        **kwargs
    ) -> str:
        """
        Execute agent with given input.
        
        Args:
            spec: Agent specification
            input: Input string
            **kwargs: Runtime-specific options
            
        Returns:
            str: Agent output
        """
        pass
```

**Implementing a Custom Runtime:**

```python
from cbw_foundry.runtime.base import BaseRuntime
from cbw_foundry.spec.models import AgentSpec

class MyCustomRuntime(BaseRuntime):
    """Custom runtime adapter."""
    
    def run(self, spec: AgentSpec, input: str, **kwargs) -> str:
        # Your implementation
        return result
```

### cbw_foundry.runtime.local_runtime

Local execution runtime.

#### LocalRuntime

```python
from cbw_foundry.runtime.local_runtime import LocalRuntime

class LocalRuntime(BaseRuntime):
    """Local execution runtime (fully implemented)."""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        
    def run(self, spec: AgentSpec, input: str, **kwargs) -> str:
        """Execute agent locally."""
```

**Example:**

```python
from cbw_foundry.runtime.local_runtime import LocalRuntime
from cbw_foundry.spec.io import load_agent_spec

# Load spec
spec = load_agent_spec("agents/specs/my_agent.agent.yaml")

# Create runtime
runtime = LocalRuntime(model="gpt-4")

# Run agent
output = runtime.run(spec, input="Hello, agent!")
print(output)
```

### cbw_foundry.runtime.adapters

Framework adapters (CrewAI, LangChain, PydanticAI).

#### CrewAIAdapter

```python
from cbw_foundry.runtime.adapters import CrewAIAdapter

class CrewAIAdapter(BaseRuntime):
    """CrewAI framework adapter."""
    
    def run(self, spec: AgentSpec, input: str, **kwargs) -> str:
        # CrewAI integration
```

#### LangChainAdapter

```python
from cbw_foundry.runtime.adapters import LangChainAdapter

class LangChainAdapter(BaseRuntime):
    """LangChain framework adapter (stub)."""
```

#### PydanticAIAdapter

```python
from cbw_foundry.runtime.adapters import PydanticAIAdapter

class PydanticAIAdapter(BaseRuntime):
    """PydanticAI framework adapter."""
```

## Specification System

Full schema and validation for agent specifications.

### Validation

```python
from cbw_foundry.spec.models import AgentSpec
from pydantic import ValidationError

try:
    spec = AgentSpec(
        name="test",
        version="1.0.0",
        description="Test agent",
        system_prompt="You are helpful.",
        runtime={"framework": "local"}
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Schema Export

```python
from cbw_foundry.spec.models import AgentSpec
import json

# Get JSON schema
schema = AgentSpec.schema_json(indent=2)
print(schema)
```

## Observability

### cbw_foundry.observability.otel

OpenTelemetry integration for distributed tracing.

#### setup_observability()

```python
from cbw_foundry.observability.otel import setup_observability

def setup_observability(
    service_name: str = "cloudcurio",
    endpoint: str = "http://localhost:4317"
) -> None:
    """
    Initialize OpenTelemetry.
    
    Args:
        service_name: Service identifier
        endpoint: OTLP endpoint
    """
```

**Example:**

```python
from cbw_foundry.observability.otel import setup_observability

# Enable tracing
setup_observability(
    service_name="my-agent-service",
    endpoint="http://jaeger:4317"
)

# Now all operations are traced
```

#### trace_agent_execution()

```python
from cbw_foundry.observability.otel import trace_agent_execution
from opentelemetry import trace

@trace_agent_execution
def run_my_agent(input: str) -> str:
    """Function execution will be traced."""
    # Your code here
    return result
```

## Utilities

### cbw_foundry.util.fs

Filesystem utilities.

#### find_agent_specs()

```python
from cbw_foundry.util.fs import find_agent_specs

def find_agent_specs(directory: str = "agents/specs") -> List[str]:
    """
    Find all agent spec files.
    
    Args:
        directory: Root directory to search
        
    Returns:
        list: Paths to agent spec files
    """
```

#### ensure_directory()

```python
from cbw_foundry.util.fs import ensure_directory

def ensure_directory(path: str) -> None:
    """Create directory if it doesn't exist."""
```

## Usage Examples

### Example 1: Load and Run Agent

```python
from cbw_foundry.spec.io import load_agent_spec
from cbw_foundry.runtime.local_runtime import LocalRuntime

# Load agent specification
spec = load_agent_spec("agents/specs/research_agent.agent.yaml")

# Create runtime
runtime = LocalRuntime()

# Execute agent
result = runtime.run(
    spec=spec,
    input="Research quantum computing advances in 2024"
)

print(f"Agent output: {result}")
```

### Example 2: Create Agent Programmatically

```python
from cbw_foundry.spec.models import AgentSpec, RuntimeConfig, ToolSpec
from cbw_foundry.spec.io import save_agent_spec

# Define agent
spec = AgentSpec(
    name="custom_analyzer",
    version="1.0.0",
    description="Custom data analyzer agent",
    system_prompt="""
    You are a data analysis agent.
    Analyze data and provide insights.
    """,
    tools=[
        ToolSpec(
            name="data_loader",
            description="Load data from sources"
        ),
        ToolSpec(
            name="statistical_analyzer",
            description="Perform statistical analysis"
        )
    ],
    runtime=RuntimeConfig(
        framework="local",
        model="gpt-4",
        temperature=0.3
    )
)

# Save to file
save_agent_spec(spec, "agents/specs/custom_analyzer.agent.yaml")
```

### Example 3: Compile and Validate

```python
from cbw_foundry.agent_cli import validate_agent, compile_agent_cli

# Validate
is_valid = validate_agent(
    spec_path="agents/specs/my_agent.agent.yaml",
    verbose=True
)

if is_valid:
    # Compile
    compile_agent_cli(
        spec_path="agents/specs/my_agent.agent.yaml",
        output_dir="dist/agents"
    )
    print("✓ Agent compiled successfully")
else:
    print("✗ Validation failed")
```

### Example 4: Run Evaluations

```python
from cbw_foundry.agent_cli import eval_agent

# Run golden tests
results = eval_agent(
    spec_path="agents/specs/my_agent.agent.yaml",
    verbose=True
)

print(f"Tests passed: {results['passed']}/{results['total']}")
print(f"Coverage: {results['coverage']}%")

if results['failed'] > 0:
    print("Failed tests:")
    for test in results['failures']:
        print(f"  - {test['name']}: {test['reason']}")
```

### Example 5: Custom Runtime Integration

```python
from cbw_foundry.runtime.base import BaseRuntime
from cbw_foundry.spec.models import AgentSpec

class MyFrameworkRuntime(BaseRuntime):
    """Custom framework integration."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def run(self, spec: AgentSpec, input: str, **kwargs) -> str:
        """Execute using custom framework."""
        # Initialize framework
        agent = self._create_agent(spec)
        
        # Execute
        result = agent.process(input)
        
        return result
    
    def _create_agent(self, spec: AgentSpec):
        """Create agent from spec."""
        # Framework-specific initialization
        pass

# Use custom runtime
runtime = MyFrameworkRuntime(api_key="...")
output = runtime.run(spec, input="test")
```

## API Versioning

The `cbw_foundry` package follows Semantic Versioning:

- **Major version** (X.0.0): Breaking API changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

### Current Version: 0.4.0

### Stability Guarantees

- **Stable**: `spec.models`, `runtime.base`, `spec.io`
- **Beta**: `runtime.adapters` (subject to changes)
- **Alpha**: `observability.otel` (experimental)

## Error Handling

```python
from cbw_foundry.spec.io import load_agent_spec
from cbw_foundry.runtime.local_runtime import LocalRuntime
from pydantic import ValidationError

try:
    # Load and validate
    spec = load_agent_spec("agents/specs/my_agent.agent.yaml")
    
    # Run
    runtime = LocalRuntime()
    result = runtime.run(spec, input="test")
    
except FileNotFoundError as e:
    print(f"Agent spec not found: {e}")
except ValidationError as e:
    print(f"Invalid agent spec: {e}")
except TimeoutError as e:
    print(f"Agent execution timed out: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Type Hints

All public APIs include type hints for IDE support:

```python
from cbw_foundry.spec.models import AgentSpec
from cbw_foundry.runtime.base import BaseRuntime
from typing import Optional, Dict, Any

def process_agent(
    spec: AgentSpec,
    runtime: BaseRuntime,
    input_data: str,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """Fully type-hinted function."""
    pass
```

## Testing

```python
import pytest
from cbw_foundry.spec.models import AgentSpec, RuntimeConfig

def test_agent_spec_creation():
    """Test creating an agent spec."""
    spec = AgentSpec(
        name="test_agent",
        version="1.0.0",
        description="Test",
        system_prompt="Test prompt",
        runtime=RuntimeConfig(framework="local")
    )
    
    assert spec.name == "test_agent"
    assert spec.version == "1.0.0"

def test_agent_spec_validation():
    """Test spec validation."""
    with pytest.raises(ValidationError):
        AgentSpec(
            name="",  # Invalid: empty name
            version="1.0.0",
            description="Test",
            system_prompt="Test",
            runtime=RuntimeConfig(framework="local")
        )
```

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [Runtime Adapters Guide](RUNTIME_ADAPTERS.md)
- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated:** 2026-01-15  
**API Version:** 0.4.0  
**Maintained By:** @cbwinslow
