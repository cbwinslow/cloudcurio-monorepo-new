---
title: Using the repo
tags: [runbook, daily-workflow]
owner: cbwinslow
last_reviewed: 2026-01-15
---

# Using the CloudCurio Monorepo

Comprehensive guide to daily workflows, common operations, and best practices for working with the CloudCurio Monorepo.

## Table of Contents

- [Daily Workflow](#daily-workflow)
- [Common Commands Reference](#common-commands-reference)
- [Agent Development Cycle](#agent-development-cycle)
- [Tool Development Cycle](#tool-development-cycle)
- [Working with Git](#working-with-git)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Daily Workflow

### Morning Setup

1. **Pull latest changes**
   ```bash
   cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
   git pull origin main
   ```

2. **Activate virtual environment**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Update dependencies (if needed)**
   ```bash
   pip install -e .
   ```

4. **Run health check**
   ```bash
   make doctor
   ```

5. **Update registries**
   ```bash
   make index
   ```

### During Development

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes** to agent specs, tools, or code

3. **Validate frequently**
   ```bash
   make validate  # Validate agent specs
   make lint      # Check code quality
   ```

4. **Test your changes**
   ```bash
   make test      # Run test suite
   make eval      # Run agent evaluations
   ```

5. **Compile agents**
   ```bash
   make compile   # Generate JSON artifacts
   ```

### End of Day

1. **Run full validation**
   ```bash
   make doctor validate lint test eval
   ```

2. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/my-new-feature
   ```

4. **Update documentation** if needed

## Common Commands Reference

### Repository Management

```bash
# Health check - validates entire system
make doctor

# Generate/update registries
make index

# Clean generated artifacts
make clean

# Install/reinstall Python package
make install
```

### Agent Operations

```bash
# Validate all agent specifications
make validate

# Compile agents to JSON
make compile

# Run golden test suites
make eval

# Validate specific agent
./bin/cbw-agent validate agents/specs/my_agent.agent.yaml

# Compile specific agent
./bin/cbw-agent compile agents/specs/my_agent.agent.yaml --out dist/agents

# Run agent locally
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "test input" \
  --runtime local

# Run agent with different runtime
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --runtime crewai \
  --input "test input"

# Create new agent
./bin/cbw-capture agent my_new_agent
```

### Tool Operations

```bash
# List available tools
cat registry/tools.json | jq '.tools[] | {name, description}'

# Test a specific tool
python -c "from agents.tools.my_tool import MyTool; print(MyTool().execute())"

# Add tool to registry
make index
```

### Workflow Operations

```bash
# Run a workflow
./bin/cbw-workflow run workflows/my_workflow.yaml

# Validate workflow
./bin/cbw-workflow validate workflows/my_workflow.yaml

# List workflows
ls -la workflows/
```

### Code Quality

```bash
# Run linter (ruff)
make lint

# Auto-fix linting issues
make fmt

# Run Python tests
make test

# Run tests with coverage
pytest --cov=cbw_foundry tests/

# Run specific test file
pytest tests/test_agent_spec.py

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Observability

```bash
# Start observability stack
docker compose -f docker/compose/observability/docker-compose.yml up -d

# View logs
docker compose -f docker/compose/observability/docker-compose.yml logs -f

# Stop observability stack
docker compose -f docker/compose/observability/docker-compose.yml down

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Jaeger: http://localhost:16686
```

### MCP Servers

```bash
# Start automation MCP server
cd mcp-servers/automation
npm install
npm start

# Start media MCP server
cd mcp-servers/media
pip install -r requirements.txt
python server.py

# Check MCP server status
curl http://localhost:3000/health  # Automation
curl http://localhost:3001/health  # Media
```

## Agent Development Cycle

### 1. Create New Agent

```bash
./bin/cbw-capture agent my_agent
```

This creates:
- `agents/specs/my_agent.agent.yaml` - Agent specification
- `agents/evals/my_agent/golden_test.yaml` - Test suite
- Template system prompt

### 2. Edit Agent Specification

```bash
nano agents/specs/my_agent.agent.yaml
```

Define:
- Agent name, description, version
- System prompt
- Tools to use
- Runtime configuration

Example:
```yaml
name: my_agent
version: "1.0.0"
description: "My custom agent for specific tasks"

system_prompt: |
  You are a helpful agent that performs [specific task].
  Follow these guidelines:
  - Be concise and accurate
  - Use the provided tools effectively
  - Validate your outputs

tools:
  - name: tool1
    description: "Tool for doing X"
  - name: tool2
    description: "Tool for doing Y"

runtime:
  framework: local
  model: gpt-4
```

### 3. Validate Specification

```bash
./bin/cbw-agent validate agents/specs/my_agent.agent.yaml
```

Fix any schema validation errors.

### 4. Create Golden Tests

```bash
nano agents/evals/my_agent/golden_test.yaml
```

Add test cases:
```yaml
tests:
  - name: "basic_functionality"
    input: "test input 1"
    expected_output: "expected output 1"
    
  - name: "edge_case"
    input: "edge case input"
    expected_output: "expected edge case output"
```

### 5. Run Agent Locally

```bash
./bin/cbw-agent run agents/specs/my_agent.agent.yaml \
  --input "test input" \
  --runtime local \
  --verbose
```

Iterate until behavior is correct.

### 6. Run Golden Tests

```bash
./bin/cbw-agent eval agents/specs/my_agent.agent.yaml
```

All tests should pass.

### 7. Compile Agent

```bash
make compile
```

Generates `dist/agents/my_agent.agent.json`.

### 8. Update Registry

```bash
make index
```

Your agent is now registered and discoverable.

## Tool Development Cycle

### 1. Create Tool Module

```bash
nano agents/tools/my_tool.py
```

Implement tool:
```python
from cbw_foundry.tools import BaseTool

class MyTool(BaseTool):
    """Tool for doing X."""
    
    name = "my_tool"
    description = "Detailed description of what this tool does"
    
    def __init__(self):
        super().__init__()
        # Initialize any resources
    
    def execute(self, **kwargs):
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        # Implementation
        result = self._do_work(kwargs)
        return result
    
    def _do_work(self, params):
        """Internal implementation."""
        pass
```

### 2. Add Tests

```bash
nano tests/test_my_tool.py
```

```python
import pytest
from agents.tools.my_tool import MyTool

def test_my_tool_basic():
    tool = MyTool()
    result = tool.execute(param1="value1")
    assert result is not None

def test_my_tool_error_handling():
    tool = MyTool()
    with pytest.raises(ValueError):
        tool.execute(invalid_param="bad")
```

### 3. Register Tool

```bash
nano agents/tools/__init__.py
```

Add import:
```python
from .my_tool import MyTool

__all__ = [
    "MyTool",
    # ... other tools
]
```

### 4. Test Tool

```bash
# Run tool tests
pytest tests/test_my_tool.py

# Test tool manually
python -c "from agents.tools.my_tool import MyTool; print(MyTool().execute())"
```

### 5. Document Tool

Add docstrings and usage examples.

### 6. Update Registry

```bash
make index
```

Tool is now available in `registry/tools.json`.

## Working with Git

### Branch Strategy

```bash
# Main branches
main          # Production-ready code
develop       # Integration branch (if used)

# Feature branches
feature/agent-xyz       # New agent development
feature/tool-abc        # New tool development
feature/framework-123   # Framework improvements

# Fix branches
fix/bug-description     # Bug fixes
hotfix/critical-issue   # Critical production fixes
```

### Commit Message Convention

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat      # New feature
fix       # Bug fix
docs      # Documentation changes
style     # Code style changes (formatting)
refactor  # Code refactoring
test      # Adding or updating tests
chore     # Maintenance tasks

# Examples:
git commit -m "feat(agents): add social media agent"
git commit -m "fix(tools): handle edge case in video tool"
git commit -m "docs(kb): update agent development guide"
git commit -m "test(eval): add golden tests for research agent"
```

### Pre-commit Workflow

Pre-commit hooks automatically run on every commit:

```bash
# Hooks run:
- trailing-whitespace   # Removes trailing whitespace
- end-of-file-fixer     # Ensures files end with newline
- check-yaml            # Validates YAML syntax
- check-added-large-files # Prevents large files
- ruff (lint)           # Python linting
- ruff (format)         # Python formatting

# If hooks fail:
# 1. Review the errors
# 2. Fix the issues
# 3. Stage fixes: git add .
# 4. Commit again: git commit -m "..."

# Skip hooks (not recommended):
git commit --no-verify -m "..."
```

### Daily Git Workflow

```bash
# Start of day
git checkout main
git pull origin main
git checkout -b feature/my-feature

# During work
git add .
git commit -m "feat: add feature X"
# (repeat as needed)

# Before pushing
make doctor validate lint test
git push origin feature/my-feature

# Create PR via GitHub UI
```

## Troubleshooting

### Virtual Environment Issues

**Problem:** Commands not found
```bash
# Solution: Activate venv
source .venv/bin/activate
which python  # Should show .venv path
```

**Problem:** Wrong Python version
```bash
# Solution: Recreate venv
rm -rf .venv
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Validation Failures

**Problem:** Agent spec validation fails
```bash
# Solution: Check detailed errors
./bin/cbw-agent validate agents/specs/my_agent.agent.yaml --verbose

# Common issues:
# - Missing required fields (name, version, description)
# - Invalid YAML syntax
# - Tool references don't exist
```

### Test Failures

**Problem:** Tests fail after changes
```bash
# Solution: Run specific test
pytest tests/test_specific.py -v

# Check test output for details
pytest tests/ -v --tb=long

# Update tests if behavior changed intentionally
```

### Registry Out of Sync

**Problem:** Agent not showing in registry
```bash
# Solution: Regenerate registries
make index

# Verify
cat registry/agents.json | jq '.agents[] | select(.name=="my_agent")'
```

### Import Errors

**Problem:** Module not found errors
```bash
# Solution: Reinstall package
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Docker Issues

**Problem:** Observability stack won't start
```bash
# Solution: Check ports
lsof -i :9090   # Prometheus
lsof -i :3000   # Grafana
lsof -i :16686  # Jaeger

# Stop and restart
docker compose -f docker/compose/observability/docker-compose.yml down
docker compose -f docker/compose/observability/docker-compose.yml up -d

# Check logs
docker compose -f docker/compose/observability/docker-compose.yml logs
```

## Best Practices

### Agent Development

1. **Start with clear requirements** - Know what your agent should do
2. **Use existing tools** when possible - Don't reinvent the wheel
3. **Write golden tests first** - Test-driven development
4. **Keep system prompts focused** - Clear, specific instructions
5. **Validate early and often** - Catch errors quickly
6. **Document your agents** - Help others understand usage

### Tool Development

1. **Follow BaseTool interface** - Consistent tool architecture
2. **Handle errors gracefully** - Don't crash, return useful errors
3. **Add comprehensive tests** - Cover happy path and edge cases
4. **Document parameters** - Clear docstrings with types
5. **Keep tools focused** - Single responsibility principle
6. **Make tools reusable** - Generic implementations

### Code Quality

1. **Run pre-commit hooks** - Maintain code standards
2. **Write meaningful commit messages** - Follow convention
3. **Keep PRs focused** - One feature per PR
4. **Add tests for new code** - Maintain coverage
5. **Update documentation** - Keep docs in sync with code
6. **Review your own PRs** - Catch issues before others review

### Workflow Efficiency

1. **Use make commands** - Automate common tasks
2. **Leverage the CLI** - cbw-* tools are your friends
3. **Keep terminal open** - Faster iteration
4. **Use git aliases** - Speed up git operations
5. **Batch similar tasks** - Edit multiple files before validating
6. **Monitor health regularly** - `make doctor` catches issues early

### Collaboration

1. **Update KB when learning** - Share knowledge
2. **Document decisions** - Add ADRs for major choices
3. **Ask questions** - Use GitHub Discussions
4. **Review others' code** - Help maintain quality
5. **Keep team informed** - Communicate breaking changes
6. **Follow established patterns** - Consistency helps everyone

## Quick Reference Card

```bash
# Daily essentials
make doctor      # Health check
make index       # Update registries
make validate    # Check agent specs
make test        # Run tests
make lint        # Check code
make fmt         # Format code

# Agent workflow
./bin/cbw-capture agent NAME          # Create
./bin/cbw-agent validate SPEC         # Validate
./bin/cbw-agent run SPEC --input TEXT # Test
./bin/cbw-agent eval SPEC             # Evaluate
make compile                          # Build

# Git workflow
git checkout -b feature/NAME  # Start
git add .                     # Stage
git commit -m "TYPE: msg"     # Commit
make doctor validate test     # Verify
git push origin feature/NAME  # Push

# Troubleshooting
source .venv/bin/activate     # Activate env
pip install -e .              # Reinstall
make clean && make compile    # Rebuild
```

---

**Last Updated:** 2026-01-15  
**Maintained By:** @cbwinslow  
**Related:** [Adding New Agents](adding_new_agent.md), [Code Quality Rules](../rules/code_quality_rules.md)
