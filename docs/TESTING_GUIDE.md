# Testing Guide

Comprehensive testing guide for CloudCurio agents, tools, and workflows.

## Table of Contents

- [Overview](#overview)
- [Testing Strategy](#testing-strategy)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [Agent Evaluation](#agent-evaluation)
- [Performance Testing](#performance-testing)
- [Best Practices](#best-practices)

## Overview

CloudCurio uses a multi-layered testing approach:

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **Golden Tests**: Evaluate agent quality
4. **Performance Tests**: Measure performance metrics
5. **End-to-End Tests**: Test complete workflows

### Test Infrastructure

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_agent_spec.py

# Run with coverage
pytest --cov=cbw_foundry tests/

# Run integration tests
pytest -m integration tests/

# Run slow tests
pytest -m slow tests/
```

## Testing Strategy

### Test Pyramid

```
        ┌──────────────┐
        │  E2E Tests   │ ← Few, slow
        ├──────────────┤
        │  Integration │ ← Some, medium
        ├──────────────┤
        │ Unit Tests   │ ← Many, fast
        └──────────────┘
```

### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── test_spec_models.py
│   ├── test_runtime.py
│   └── test_tools.py
├── integration/             # Integration tests
│   ├── test_agent_execution.py
│   └── test_workflow.py
├── evals/                   # Agent evaluations
│   └── test_agent_quality.py
├── performance/             # Performance tests
│   └── test_benchmarks.py
└── conftest.py             # Pytest configuration
```

## Unit Testing

### Testing Agent Specifications

```python
import pytest
from cbw_foundry.spec.models import AgentSpec, RuntimeConfig
from pydantic import ValidationError


class TestAgentSpec:
    """Test agent specification models."""
    
    def test_valid_spec_creation(self):
        """Test creating valid agent spec."""
        spec = AgentSpec(
            api_version="v1",
            kind="Agent",
            metadata={
                "name": "test_agent",
                "version": "1.0.0",
                "tags": ["test"]
            },
            spec={
                "model_policy": {
                    "preferred": {
                        "provider": "ollama",
                        "model": "qwen2.5-coder"
                    }
                },
                "prompts": {
                    "system": "test_prompt.md"
                },
                "runtime": {
                    "supported": ["local"]
                }
            }
        )
        
        assert spec.metadata.name == "test_agent"
        assert spec.metadata.version == "1.0.0"
        assert len(spec.metadata.tags) == 1
    
    def test_invalid_spec_validation(self):
        """Test spec validation fails for invalid data."""
        with pytest.raises(ValidationError):
            AgentSpec(
                api_version="v1",
                kind="Agent",
                metadata={
                    "name": "",  # Invalid: empty name
                    "version": "1.0.0"
                }
            )
    
    def test_spec_serialization(self):
        """Test spec can be serialized to JSON."""
        spec = AgentSpec(
            api_version="v1",
            kind="Agent",
            metadata={
                "name": "test_agent",
                "version": "1.0.0"
            },
            spec={
                "model_policy": {
                    "preferred": {
                        "provider": "ollama",
                        "model": "test"
                    }
                },
                "prompts": {"system": "test.md"},
                "runtime": {"supported": ["local"]}
            }
        )
        
        json_data = spec.model_dump_json()
        assert json_data is not None
        assert "test_agent" in json_data
```

### Testing Tools

```python
import pytest
from agents.tools.python.data_processor import DataProcessorTool


class TestDataProcessorTool:
    """Test data processor tool."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.tool = DataProcessorTool(config={"max_records": 100})
    
    def test_filter_operation(self):
        """Test data filtering."""
        input_data = {
            "data": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 30}
            ],
            "operation": "filter",
            "criteria": {"age": 30}
        }
        
        result = self.tool.execute(input_data)
        
        assert result.success
        assert len(result.data["processed_data"]) == 2
    
    def test_transform_operation(self):
        """Test data transformation."""
        input_data = {
            "data": [{"first": "John", "last": "Doe"}],
            "operation": "transform",
            "mapping": {"first": "given", "last": "family"}
        }
        
        result = self.tool.execute(input_data)
        
        assert result.success
        assert "given" in result.data["processed_data"][0]
    
    def test_invalid_input_handling(self):
        """Test error handling for invalid input."""
        result = self.tool.execute("invalid")
        
        assert not result.success
        assert result.error is not None
    
    def test_configuration(self):
        """Test tool configuration."""
        tool = DataProcessorTool(config={"max_records": 50})
        assert tool.max_records == 50
```

### Testing Runtime Adapters

```python
import pytest
from unittest.mock import Mock, patch
from cbw_foundry.runtime.local_runtime import LocalRuntime


class TestLocalRuntime:
    """Test local runtime adapter."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runtime = LocalRuntime()
    
    def test_runtime_name(self):
        """Test runtime name."""
        assert self.runtime.name == "local"
    
    @patch('cbw_foundry.spec.io.load_yaml')
    def test_run_with_tool(self, mock_load):
        """Test running agent with Python tool."""
        mock_load.return_value = {
            "api_version": "v1",
            "kind": "Agent",
            "metadata": {"name": "test", "version": "1.0.0"},
            "spec": {
                "tools": [{
                    "type": "python",
                    "entrypoint": "test_tool.py:test_func"
                }],
                "model_policy": {
                    "preferred": {"provider": "ollama", "model": "test"}
                },
                "prompts": {"system": "test.md"},
                "runtime": {"supported": ["local"]}
            }
        }
        
        # Test execution
        result = self.runtime.run("test.yaml", "test input")
        
        assert result is not None
        assert result.runtime == "local"
    
    def test_run_without_tool(self):
        """Test running agent without tools (echo mode)."""
        with patch('cbw_foundry.spec.io.load_yaml') as mock_load:
            mock_load.return_value = {
                "api_version": "v1",
                "kind": "Agent",
                "metadata": {"name": "test", "version": "1.0.0"},
                "spec": {
                    "tools": [],
                    "model_policy": {
                        "preferred": {"provider": "ollama", "model": "test"}
                    },
                    "prompts": {"system": "test.md"},
                    "runtime": {"supported": ["local"]}
                }
            }
            
            result = self.runtime.run("test.yaml", "test input")
            
            assert result.output == {"echo": "test input"}
```

## Integration Testing

### Testing Agent Execution

```python
import pytest
from cbw_foundry.runtime.local_runtime import LocalRuntime
from cbw_foundry.spec.io import load_agent_spec


@pytest.mark.integration
class TestAgentExecution:
    """Integration tests for agent execution."""
    
    def test_hello_world_agent(self):
        """Test hello world agent execution."""
        runtime = LocalRuntime()
        
        result = runtime.run(
            spec_path="agents/specs/examples/hello_world.agent.yaml",
            user_input="Hello!"
        )
        
        assert result is not None
        assert result.runtime == "local"
    
    @pytest.mark.slow
    def test_agent_with_real_llm(self):
        """Test agent with real LLM call."""
        # Requires API keys to be set
        pytest.skip("Requires API credentials")
        
        runtime = LocalRuntime()
        result = runtime.run(
            spec_path="agents/specs/test_agent.yaml",
            user_input="What is 2+2?"
        )
        
        assert result.success
        assert "4" in str(result.output)
```

### Testing Workflows

```python
import pytest
from cbw_foundry.workflow import WorkflowRunner


@pytest.mark.integration
class TestWorkflows:
    """Integration tests for workflows."""
    
    def test_simple_workflow(self):
        """Test simple workflow execution."""
        runner = WorkflowRunner()
        
        result = runner.run("workflows/test_workflow.yaml")
        
        assert result.success
        assert result.steps_completed > 0
    
    def test_multi_agent_workflow(self):
        """Test workflow with multiple agents."""
        runner = WorkflowRunner()
        
        result = runner.run("workflows/multi_agent_test.yaml")
        
        assert result.success
        assert len(result.agent_outputs) > 1
```

## Agent Evaluation

### Golden Test Suites

Create golden test cases for agents:

`agents/evals/golden/test_agent_cases.yaml`:

```yaml
test_suite:
  name: test_agent_golden_tests
  version: 1.0.0
  
test_cases:
  - id: basic_functionality
    input: "Test input"
    expected_output_contains:
      - "expected"
      - "output"
    
  - id: error_handling
    input: "invalid ###"
    expected_output_contains:
      - "error"
      - "invalid"
    
  - id: output_format
    input: "Format test"
    expected_output_schema:
      type: object
      required: ["status", "data"]
```

### Running Evaluations

```python
import pytest
from cbw_foundry.evals.runner import EvaluationRunner


class TestAgentEvaluation:
    """Test agent quality with golden tests."""
    
    def test_run_golden_tests(self):
        """Run golden test suite."""
        runner = EvaluationRunner()
        
        results = runner.run(
            agent_spec="agents/specs/test_agent.agent.yaml",
            test_suite="agents/evals/golden/test_agent_cases.yaml"
        )
        
        assert results.total_tests > 0
        assert results.passed_tests >= results.total_tests * 0.8  # 80% pass rate
    
    def test_evaluation_metrics(self):
        """Test evaluation metrics calculation."""
        runner = EvaluationRunner()
        
        results = runner.run(
            agent_spec="agents/specs/test_agent.agent.yaml",
            test_suite="agents/evals/golden/test_agent_cases.yaml"
        )
        
        assert hasattr(results, 'accuracy')
        assert hasattr(results, 'precision')
        assert hasattr(results, 'recall')
```

### CLI Evaluation

```bash
# Run golden tests
./bin/cbw-agent eval agents/specs/my_agent.agent.yaml

# Run with verbose output
./bin/cbw-agent eval agents/specs/my_agent.agent.yaml --verbose

# Save results
./bin/cbw-agent eval agents/specs/my_agent.agent.yaml \
  --output results/eval_results.json
```

## Performance Testing

### Benchmarking

```python
import pytest
import time
from cbw_foundry.runtime.local_runtime import LocalRuntime


@pytest.mark.performance
class TestPerformance:
    """Performance tests for agents."""
    
    def test_agent_execution_time(self):
        """Test agent execution time."""
        runtime = LocalRuntime()
        
        start_time = time.time()
        result = runtime.run(
            "agents/specs/test_agent.agent.yaml",
            "test input"
        )
        execution_time = time.time() - start_time
        
        assert execution_time < 5.0  # Should complete in < 5 seconds
    
    def test_throughput(self):
        """Test agent throughput."""
        runtime = LocalRuntime()
        
        num_requests = 10
        start_time = time.time()
        
        for i in range(num_requests):
            runtime.run(
                "agents/specs/test_agent.agent.yaml",
                f"test input {i}"
            )
        
        total_time = time.time() - start_time
        throughput = num_requests / total_time
        
        assert throughput > 1.0  # At least 1 request/second
```

### Load Testing

```python
import pytest
from concurrent.futures import ThreadPoolExecutor
from cbw_foundry.runtime.local_runtime import LocalRuntime


@pytest.mark.performance
@pytest.mark.slow
class TestLoadTesting:
    """Load tests for agents."""
    
    def test_concurrent_execution(self):
        """Test concurrent agent execution."""
        runtime = LocalRuntime()
        
        def execute_agent(index):
            return runtime.run(
                "agents/specs/test_agent.agent.yaml",
                f"test input {index}"
            )
        
        # Execute 10 agents concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(execute_agent, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r is not None for r in results)
```

## Best Practices

### 1. Test Organization

- Keep tests close to the code they test
- Use descriptive test names
- Group related tests in classes
- Use pytest markers for categorization

### 2. Fixtures

Use pytest fixtures for setup:

```python
@pytest.fixture
def sample_agent_spec():
    """Provide sample agent spec for tests."""
    return AgentSpec(
        api_version="v1",
        kind="Agent",
        metadata={"name": "test", "version": "1.0.0"},
        spec={
            "model_policy": {
                "preferred": {"provider": "ollama", "model": "test"}
            },
            "prompts": {"system": "test.md"},
            "runtime": {"supported": ["local"]}
        }
    )

def test_with_fixture(sample_agent_spec):
    """Test using fixture."""
    assert sample_agent_spec.metadata.name == "test"
```

### 3. Mocking

Use mocking for external dependencies:

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    """Test with mocked API call."""
    mock_get.return_value = Mock(status_code=200, json=lambda: {"data": "test"})
    
    # Your test code
    result = call_api()
    
    assert result["data"] == "test"
    mock_get.assert_called_once()
```

### 4. Parameterization

Use pytest parameterization for multiple test cases:

```python
@pytest.mark.parametrize("input_data,expected", [
    ({"age": 30}, 2),
    ({"age": 25}, 1),
    ({"age": 35}, 0)
])
def test_filter_with_params(input_data, expected):
    """Test filtering with different criteria."""
    tool = DataProcessorTool()
    result = tool.execute({
        "data": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ],
        "operation": "filter",
        "criteria": input_data
    })
    
    assert len(result.data["processed_data"]) == expected
```

### 5. Coverage

Aim for high test coverage:

```bash
# Run with coverage
pytest --cov=cbw_foundry --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### 6. Continuous Testing

Set up pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [API Reference](API.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
