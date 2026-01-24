# Runtime Adapters Guide

Guide to implementing and using runtime adapters for different agent frameworks.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Supported Runtimes](#supported-runtimes)
- [Implementing Adapters](#implementing-adapters)
- [Configuration](#configuration)
- [Testing Adapters](#testing-adapters)

## Overview

Runtime adapters bridge CloudCurio agent specifications with different agent frameworks, enabling agents to run on multiple platforms without modification.

### Adapter Interface

All adapters implement the `BaseRuntime` interface:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class RunResult:
    """Standard runtime execution result."""
    output: Any
    runtime: str
    metadata: Dict[str, Any] = None
    error: str = None


class AgentRuntime(ABC):
    """Base class for all runtime adapters."""
    
    name: str = "base"
    
    @abstractmethod
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """
        Execute agent with given input.
        
        Args:
            spec_path: Path to agent specification
            user_input: Input for the agent
            
        Returns:
            RunResult with execution outcome
        """
        pass
```

## Architecture

### Runtime System

```
Agent Spec (YAML) → Runtime Adapter → Framework → LLM → Result
        ↓                  ↓              ↓         ↓       ↓
    Validate         Translate      Execute    Generate  Format
```

### Adapter Responsibilities

1. **Load Specification**: Parse and validate agent specs
2. **Configure Framework**: Set up framework-specific components
3. **Execute Agent**: Run agent with user input
4. **Handle Errors**: Manage framework errors gracefully
5. **Return Results**: Format output consistently

## Supported Runtimes

### Local Runtime

Built-in lightweight execution without external dependencies:

```python
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec
from ..spec.io import load_yaml


class LocalRuntime(AgentRuntime):
    """Local execution runtime."""
    
    name = "local"
    
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """Execute agent locally."""
        # Load and validate spec
        agent = AgentSpec.model_validate(load_yaml(spec_path))
        
        # Find Python tool
        tool = next((t for t in agent.spec.tools if t.type == "python"), None)
        
        if tool:
            # Load tool module
            mod_path, func = tool.entrypoint.split(":")
            mod_fs = Path(mod_path)
            
            if not mod_fs.exists():
                return RunResult(
                    output={"error": f"tool module not found: {mod_fs}"},
                    runtime=self.name
                )
            
            # Import and execute
            sp = spec_from_file_location(mod_fs.stem, mod_fs)
            assert sp and sp.loader
            m = module_from_spec(sp)
            sp.loader.exec_module(m)
            fn = getattr(m, func, None)
            
            if fn is None:
                return RunResult(
                    output={"error": f"tool func not found: {func}"},
                    runtime=self.name
                )
            
            return RunResult(output=fn(user_input), runtime=self.name)
        
        # No tool - echo input
        return RunResult(output={"echo": user_input}, runtime=self.name)
```

**Usage:**

```bash
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "test input" \
  --runtime local
```

### CrewAI Runtime

Multi-agent collaboration framework:

```python
from crewai import Agent, Task, Crew
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec
from ..spec.io import load_yaml


class CrewAIRuntime(AgentRuntime):
    """CrewAI framework adapter."""
    
    name = "crewai"
    
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """Execute agent using CrewAI."""
        # Load spec
        agent_spec = AgentSpec.model_validate(load_yaml(spec_path))
        
        # Load system prompt
        system_prompt = self._load_prompt(agent_spec.spec.prompts.system)
        
        # Create CrewAI agent
        agent = Agent(
            role=agent_spec.metadata.name,
            goal=agent_spec.metadata.name.replace("_", " ").title(),
            backstory=system_prompt,
            verbose=True,
            allow_delegation=False
        )
        
        # Create task
        task = Task(
            description=user_input,
            agent=agent,
            expected_output="Processed result"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            return RunResult(
                output={"result": str(result)},
                runtime=self.name,
                metadata={"agent": agent_spec.metadata.name}
            )
        except Exception as e:
            return RunResult(
                output=None,
                runtime=self.name,
                error=str(e)
            )
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load system prompt from file."""
        from pathlib import Path
        return Path(prompt_path).read_text()
```

**Usage:**

```bash
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "task description" \
  --runtime crewai
```

### PydanticAI Runtime

Type-safe agent framework:

```python
from pydantic_ai import Agent as PydanticAgent
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec
from ..spec.io import load_yaml


class PydanticAIRuntime(AgentRuntime):
    """PydanticAI framework adapter."""
    
    name = "pydanticai"
    
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """Execute agent using PydanticAI."""
        # Load spec
        agent_spec = AgentSpec.model_validate(load_yaml(spec_path))
        
        # Get model configuration
        model_ref = agent_spec.spec.model_policy.preferred
        model_name = f"{model_ref.provider}/{model_ref.model}"
        
        # Load system prompt
        system_prompt = self._load_prompt(agent_spec.spec.prompts.system)
        
        # Create PydanticAI agent
        agent = PydanticAgent(
            model=model_name,
            system_prompt=system_prompt
        )
        
        try:
            # Run agent
            result = agent.run_sync(user_input)
            
            return RunResult(
                output={"result": result.data},
                runtime=self.name,
                metadata={
                    "agent": agent_spec.metadata.name,
                    "model": model_name
                }
            )
        except Exception as e:
            return RunResult(
                output=None,
                runtime=self.name,
                error=str(e)
            )
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load system prompt from file."""
        from pathlib import Path
        return Path(prompt_path).read_text()
```

**Usage:**

```bash
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "query" \
  --runtime pydanticai
```

### LangChain Runtime

Industry-standard LLM framework:

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec
from ..spec.io import load_yaml


class LangChainRuntime(AgentRuntime):
    """LangChain framework adapter."""
    
    name = "langchain"
    
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """Execute agent using LangChain."""
        # Load spec
        agent_spec = AgentSpec.model_validate(load_yaml(spec_path))
        
        # Get model
        model_ref = agent_spec.spec.model_policy.preferred
        llm = self._create_llm(model_ref)
        
        # Load system prompt
        system_prompt = self._load_prompt(agent_spec.spec.prompts.system)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Load tools
        tools = self._load_tools(agent_spec.spec.tools)
        
        # Create agent
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        try:
            # Execute
            result = agent_executor.invoke({"input": user_input})
            
            return RunResult(
                output=result,
                runtime=self.name,
                metadata={"agent": agent_spec.metadata.name}
            )
        except Exception as e:
            return RunResult(
                output=None,
                runtime=self.name,
                error=str(e)
            )
    
    def _create_llm(self, model_ref):
        """Create LLM instance."""
        if model_ref.provider == "openai":
            return ChatOpenAI(model=model_ref.model)
        else:
            raise ValueError(f"Unsupported provider: {model_ref.provider}")
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load system prompt."""
        from pathlib import Path
        return Path(prompt_path).read_text()
    
    def _load_tools(self, tool_refs):
        """Load and configure tools."""
        # Tool loading logic
        return []
```

**Usage:**

```bash
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "question" \
  --runtime langchain
```

## Implementing Adapters

### Step 1: Create Adapter Class

```python
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec


class CustomRuntime(AgentRuntime):
    """Custom framework adapter."""
    
    name = "custom"
    
    def __init__(self, config: dict = None):
        """Initialize adapter with configuration."""
        self.config = config or {}
    
    def run(self, spec_path: str, user_input: str) -> RunResult:
        """Execute agent using custom framework."""
        try:
            # 1. Load and validate specification
            agent_spec = self._load_spec(spec_path)
            
            # 2. Configure framework
            framework_agent = self._create_agent(agent_spec)
            
            # 3. Execute
            output = self._execute(framework_agent, user_input)
            
            # 4. Format result
            return RunResult(
                output=output,
                runtime=self.name,
                metadata=self._get_metadata(agent_spec)
            )
        except Exception as e:
            return RunResult(
                output=None,
                runtime=self.name,
                error=str(e)
            )
    
    def _load_spec(self, spec_path: str) -> AgentSpec:
        """Load agent specification."""
        from ..spec.io import load_yaml
        return AgentSpec.model_validate(load_yaml(spec_path))
    
    def _create_agent(self, spec: AgentSpec):
        """Create framework-specific agent."""
        # Framework initialization
        pass
    
    def _execute(self, agent, user_input: str):
        """Execute agent."""
        # Framework execution
        pass
    
    def _get_metadata(self, spec: AgentSpec) -> dict:
        """Get execution metadata."""
        return {
            "agent_name": spec.metadata.name,
            "agent_version": spec.metadata.version
        }
```

### Step 2: Register Adapter

Add to `src/cbw_foundry/runtime/__init__.py`:

```python
from .local_runtime import LocalRuntime
from .adapters import CrewAIRuntime, PydanticAIRuntime, LangChainRuntime
from .custom_runtime import CustomRuntime

RUNTIME_REGISTRY = {
    "local": LocalRuntime,
    "crewai": CrewAIRuntime,
    "pydanticai": PydanticAIRuntime,
    "langchain": LangChainRuntime,
    "custom": CustomRuntime,
}


def get_runtime(runtime_name: str):
    """Get runtime adapter by name."""
    return RUNTIME_REGISTRY.get(runtime_name)
```

### Step 3: Test Adapter

```python
import pytest
from cbw_foundry.runtime.custom_runtime import CustomRuntime


def test_custom_runtime_execution():
    """Test custom runtime execution."""
    runtime = CustomRuntime()
    
    result = runtime.run(
        spec_path="agents/specs/test_agent.agent.yaml",
        user_input="test input"
    )
    
    assert result.runtime == "custom"
    assert result.output is not None


def test_custom_runtime_error_handling():
    """Test error handling."""
    runtime = CustomRuntime()
    
    result = runtime.run(
        spec_path="nonexistent.yaml",
        user_input="test"
    )
    
    assert result.error is not None
```

## Configuration

### Environment Variables

Configure runtimes via environment:

```bash
# Model provider API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Ollama configuration
export OLLAMA_BASE_URL="http://localhost:11434"

# Runtime-specific config
export CREWAI_VERBOSE="true"
export LANGCHAIN_TRACING="true"
```

### Runtime Configuration File

`configs/runtimes.yaml`:

```yaml
runtimes:
  local:
    enabled: true
    default_timeout: 30
    
  crewai:
    enabled: true
    verbose: true
    allow_delegation: false
    
  pydanticai:
    enabled: true
    retry_attempts: 3
    
  langchain:
    enabled: true
    verbose: true
    max_iterations: 10
```

## Testing Adapters

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from cbw_foundry.runtime.adapters import CrewAIRuntime


class TestCrewAIRuntime:
    """Test CrewAI runtime adapter."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runtime = CrewAIRuntime()
    
    def test_spec_loading(self):
        """Test specification loading."""
        spec = self.runtime._load_spec("agents/specs/test.agent.yaml")
        assert spec is not None
    
    @patch('crewai.Crew.kickoff')
    def test_execution(self, mock_kickoff):
        """Test agent execution."""
        mock_kickoff.return_value = "test result"
        
        result = self.runtime.run(
            "agents/specs/test.agent.yaml",
            "test input"
        )
        
        assert result.runtime == "crewai"
        assert result.output is not None
    
    def test_error_handling(self):
        """Test error handling."""
        result = self.runtime.run(
            "nonexistent.yaml",
            "test"
        )
        
        assert result.error is not None
```

### Integration Tests

```python
@pytest.mark.integration
class TestRuntimeIntegration:
    """Integration tests for runtime adapters."""
    
    def test_local_runtime_integration(self):
        """Test local runtime with real agent."""
        from cbw_foundry.runtime.local_runtime import LocalRuntime
        
        runtime = LocalRuntime()
        result = runtime.run(
            "agents/specs/examples/hello_world.agent.yaml",
            "Hello, world!"
        )
        
        assert result.output is not None
    
    @pytest.mark.slow
    def test_crewai_runtime_integration(self):
        """Test CrewAI runtime with real agent."""
        from cbw_foundry.runtime.adapters import CrewAIRuntime
        
        runtime = CrewAIRuntime()
        result = runtime.run(
            "agents/specs/examples/hello_world.agent.yaml",
            "Test task"
        )
        
        assert result.output is not None
```

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [API Reference](API.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
