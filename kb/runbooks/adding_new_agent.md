---
title: Adding a new agent
tags: [runbook, agents, development]
owner: cbwinslow
last_reviewed: 2026-01-15
---

# Adding a New Agent to CloudCurio

Complete step-by-step guide for creating, testing, and deploying new agents in the CloudCurio Monorepo.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Guide](#step-by-step-guide)
- [Agent Specification Format](#agent-specification-format)
- [System Prompts](#system-prompts)
- [Tool Integration](#tool-integration)
- [Testing Your Agent](#testing-your-agent)
- [Advanced Topics](#advanced-topics)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

CloudCurio uses a declarative agent specification format where agents are defined in YAML and compiled to optimized JSON artifacts. This approach provides:

- **Human-readable specifications** for easy authoring
- **Machine-optimized execution** for performance
- **Version control friendly** format
- **Automated validation** and testing
- **Framework independence** via runtime adapters

## Prerequisites

Before creating a new agent, ensure:

1. ✅ Environment is bootstrapped (`./scripts/bootstrap.sh`)
2. ✅ Virtual environment is activated
3. ✅ You understand the agent's purpose and requirements
4. ✅ You know which tools the agent will need
5. ✅ You've reviewed existing agents for patterns

## Step-by-Step Guide

### Step 1: Scaffold the Agent

Use the `cbw-capture` CLI to create agent template:

```bash
./bin/cbw-capture agent my_new_agent
```

**What this creates:**

```
agents/
├── specs/
│   └── my_new_agent.agent.yaml    # Agent specification
└── evals/
    └── my_new_agent/
        └── golden_test.yaml        # Test suite
```

**Expected output:**
```
✓ Created agents/specs/my_new_agent.agent.yaml
✓ Created agents/evals/my_new_agent/golden_test.yaml
✓ Agent scaffold complete!

Next steps:
  1. Edit agents/specs/my_new_agent.agent.yaml
  2. Define system prompt and tools
  3. Add test cases to agents/evals/my_new_agent/golden_test.yaml
  4. Run: ./bin/cbw-agent validate agents/specs/my_new_agent.agent.yaml
```

### Step 2: Define Agent Specification

Edit `agents/specs/my_new_agent.agent.yaml`:

```yaml
name: my_new_agent
version: "1.0.0"
description: "Brief description of what this agent does"

# Detailed system prompt - this is the agent's core instruction
system_prompt: |
  You are a specialized agent designed to [primary purpose].
  
  Your responsibilities:
  - [Responsibility 1]
  - [Responsibility 2]
  - [Responsibility 3]
  
  Guidelines:
  - Be precise and accurate
  - Use the provided tools when needed
  - Validate your outputs
  - Handle errors gracefully
  
  Output format:
  [Specify expected output structure]

# Tools this agent can use
tools:
  - name: tool_name_1
    description: "What this tool does"
    required: true  # or false
    
  - name: tool_name_2
    description: "What this tool does"
    required: false

# Runtime configuration
runtime:
  framework: local      # local, crewai, langchain, pydanticai
  model: gpt-4         # Default model to use
  temperature: 0.7     # Creativity level (0.0-1.0)
  max_tokens: 2000     # Maximum response length
  timeout: 300         # Execution timeout in seconds

# Optional: Agent metadata
metadata:
  author: "Your Name"
  tags: ["category", "domain", "purpose"]
  version_history:
    - version: "1.0.0"
      date: "2026-01-15"
      changes: "Initial release"
```

**Key sections explained:**

- **name**: Unique identifier (lowercase, underscores)
- **version**: Semantic version (major.minor.patch)
- **description**: One-line summary for registry
- **system_prompt**: Core instructions for agent behavior
- **tools**: List of tools agent can use
- **runtime**: Execution configuration
- **metadata**: Optional tracking information

### Step 3: Validate the Specification

Check if your agent spec is valid:

```bash
./bin/cbw-agent validate agents/specs/my_new_agent.agent.yaml
```

**If validation passes:**
```
✓ agents/specs/my_new_agent.agent.yaml is valid
```

**If validation fails:**
```
✗ agents/specs/my_new_agent.agent.yaml has errors:
  - Line 5: Missing required field 'version'
  - Line 15: Tool 'unknown_tool' not found in registry
  - Line 22: Invalid runtime framework 'custom'
```

Fix errors and re-validate.

### Step 4: Create Golden Tests

Edit `agents/evals/my_new_agent/golden_test.yaml`:

```yaml
name: "My New Agent Test Suite"
agent: my_new_agent

tests:
  # Test 1: Basic functionality
  - name: "basic_operation"
    description: "Test basic agent functionality"
    input: "Input that triggers core behavior"
    expected_output: "Expected response or pattern"
    match_type: "exact"  # exact, contains, regex
    
  # Test 2: Tool usage
  - name: "tool_integration"
    description: "Test that agent uses tools correctly"
    input: "Input that requires tool usage"
    expected_output: "Output showing tool was used"
    match_type: "contains"
    
  # Test 3: Edge case
  - name: "edge_case_handling"
    description: "Test edge case behavior"
    input: "Edge case input"
    expected_output: "Graceful handling response"
    match_type: "regex"
    expected_pattern: "^Error: .+ handled gracefully$"
    
  # Test 4: Error handling
  - name: "error_handling"
    description: "Test error scenarios"
    input: "Invalid input"
    expected_error: true
    error_message: "Invalid input provided"
```

**Test types:**

- **exact**: Output must match exactly
- **contains**: Output must contain the string
- **regex**: Output must match regex pattern

**Best practices for tests:**

1. Cover the happy path (normal usage)
2. Test tool integrations
3. Test edge cases
4. Test error handling
5. Use realistic inputs
6. Keep tests independent

### Step 5: Test Agent Locally

Run your agent with test input:

```bash
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
  --input "test input here" \
  --runtime local \
  --verbose
```

**Expected output:**
```
CloudCurio Agent Runner
=======================
Agent: my_new_agent
Runtime: local
Input: test input here
---
[Agent reasoning and tool calls appear here]
---
Output: [Agent's response]
✓ Execution completed in 3.2s
```

**Iterate until behavior is correct:**

1. Run agent with various inputs
2. Observe output and behavior
3. Adjust system prompt if needed
4. Re-run and test again
5. Repeat until satisfied

### Step 6: Run Golden Test Suite

Execute your test suite:

```bash
./bin/cbw-agent eval agents/specs/my_new_agent.agent.yaml
```

**Expected output:**
```
Running evaluations for my_new_agent...

✓ basic_operation (1.2s)
✓ tool_integration (2.3s)
✓ edge_case_handling (1.8s)
✓ error_handling (1.0s)

Results: 4/4 tests passed
Coverage: 100%
✓ All tests passed!
```

**If tests fail:**

1. Review failure details
2. Check if agent behavior is wrong OR test expectations are wrong
3. Fix agent spec or test case
4. Re-run eval

### Step 7: Compile Agent

Compile YAML to optimized JSON:

```bash
make compile
```

Or compile specific agent:

```bash
./bin/cbw-agent compile agents/specs/my_new_agent.agent.yaml \
  --out dist/agents
```

**This creates:**
```
dist/agents/my_new_agent.agent.json
```

**JSON format is:**
- Optimized for machine parsing
- Used by runtime adapters
- Includes pre-processed metadata
- Faster to load and execute

### Step 8: Update Registry

Register your agent in the system:

```bash
make index
```

**This updates:**
- `registry/agents.json` - Agent is now discoverable
- Agent appears in CLI listings
- Can be referenced by workflows

**Verify registration:**
```bash
cat registry/agents.json | jq '.agents[] | select(.name=="my_new_agent")'
```

### Step 9: Document Your Agent

Create agent documentation (optional but recommended):

```bash
nano agents/specs/my_new_agent.README.md
```

**Document:**
- Purpose and use cases
- Required tools and their purposes
- Input/output formats
- Usage examples
- Known limitations
- Configuration options

### Step 10: Commit Your Changes

```bash
git add agents/specs/my_new_agent.agent.yaml
git add agents/evals/my_new_agent/
git add dist/agents/my_new_agent.agent.json
git add registry/agents.json
git commit -m "feat(agents): add my_new_agent"
git push origin feature/my-new-agent
```

## Agent Specification Format

### Required Fields

```yaml
name: string           # Unique identifier
version: string        # Semantic version (X.Y.Z)
description: string    # Brief one-line description
system_prompt: string  # Core instructions for agent
```

### Optional Fields

```yaml
tools: array           # List of tool specifications
runtime: object        # Runtime configuration
metadata: object       # Additional tracking info
config: object         # Agent-specific configuration
```

### Tool Specification

```yaml
tools:
  - name: tool_name              # Tool identifier
    description: string          # What the tool does
    required: boolean            # Whether tool is required
    config:                      # Tool-specific configuration
      key: value
```

### Runtime Configuration

```yaml
runtime:
  framework: string     # local, crewai, langchain, pydanticai
  model: string         # LLM model to use
  temperature: float    # 0.0-1.0, creativity level
  max_tokens: integer   # Maximum response length
  timeout: integer      # Execution timeout (seconds)
  top_p: float          # Nucleus sampling parameter
  frequency_penalty: float  # Repetition penalty
  presence_penalty: float   # Topic diversity penalty
```

## System Prompts

### Best Practices

1. **Be specific and clear** - No ambiguity
2. **Define the role** - What is this agent?
3. **List responsibilities** - What should it do?
4. **Provide guidelines** - How should it behave?
5. **Specify output format** - What structure is expected?
6. **Include examples** - Show desired behavior
7. **Handle errors** - Describe error scenarios

### Template

```yaml
system_prompt: |
  You are a [role/title] specialized in [domain/task].
  
  ## Role
  [Detailed description of agent's role and expertise]
  
  ## Responsibilities
  1. [Primary responsibility]
  2. [Secondary responsibility]
  3. [Additional responsibilities...]
  
  ## Guidelines
  - [Guideline 1]
  - [Guideline 2]
  - [Guideline 3]
  
  ## Tools Available
  You have access to the following tools:
  - **tool_name_1**: [When and how to use it]
  - **tool_name_2**: [When and how to use it]
  
  ## Output Format
  [Specify expected output structure]
  
  Example:
  ```
  [Example output]
  ```
  
  ## Error Handling
  If you encounter errors:
  1. [Step 1]
  2. [Step 2]
  3. Return a clear error message
```

### Examples

**Research Agent:**
```yaml
system_prompt: |
  You are a Research Agent specialized in gathering, analyzing, and synthesizing information from multiple sources.
  
  Your goal is to provide comprehensive, accurate, and well-cited research on any topic.
  
  Process:
  1. Break down the research question
  2. Use search tools to gather information
  3. Analyze and synthesize findings
  4. Present results with citations
  
  Output format:
  ## Summary
  [2-3 sentence overview]
  
  ## Key Findings
  1. [Finding with citation]
  2. [Finding with citation]
  
  ## Sources
  - [Source 1]
  - [Source 2]
```

**Code Review Agent:**
```yaml
system_prompt: |
  You are a Code Review Agent specializing in identifying bugs, security issues, and code quality problems.
  
  Review code for:
  - Logic errors and bugs
  - Security vulnerabilities
  - Performance issues
  - Code style and best practices
  - Test coverage
  
  For each issue found, provide:
  - Severity (Critical/High/Medium/Low)
  - Location (file:line)
  - Description
  - Suggested fix
  
  Be constructive and focus on improvements.
```

## Tool Integration

### Using Existing Tools

1. **List available tools:**
   ```bash
   cat registry/tools.json | jq '.tools[] | {name, description}'
   ```

2. **Reference in agent spec:**
   ```yaml
   tools:
     - name: web_search
       description: "Search the web for information"
     - name: code_analyzer
       description: "Analyze code for issues"
   ```

3. **Configure tool parameters:**
   ```yaml
   tools:
     - name: web_search
       config:
         max_results: 10
         search_engine: "google"
   ```

### Creating Custom Tools

If needed tool doesn't exist, create it:

1. **Create tool module:**
   ```python
   # agents/tools/my_custom_tool.py
   from cbw_foundry.tools import BaseTool
   
   class MyCustomTool(BaseTool):
       name = "my_custom_tool"
       description = "What this tool does"
       
       def execute(self, **kwargs):
           # Implementation
           return result
   ```

2. **Register tool:**
   ```python
   # agents/tools/__init__.py
   from .my_custom_tool import MyCustomTool
   __all__ = ["MyCustomTool", ...]
   ```

3. **Update registry:**
   ```bash
   make index
   ```

4. **Use in agent:**
   ```yaml
   tools:
     - name: my_custom_tool
   ```

## Testing Your Agent

### Unit Testing

Test individual agent components:

```python
# tests/test_my_new_agent.py
import pytest
from cbw_foundry.spec.io import load_agent_spec
from cbw_foundry.runtime.local_runtime import LocalRuntime

def test_agent_loads():
    spec = load_agent_spec("agents/specs/my_new_agent.agent.yaml")
    assert spec.name == "my_new_agent"

def test_agent_basic_execution():
    spec = load_agent_spec("agents/specs/my_new_agent.agent.yaml")
    runtime = LocalRuntime()
    result = runtime.run(spec, input="test")
    assert result is not None
```

### Golden Testing

Use the eval framework:

```bash
# Run all tests
make eval

# Run specific agent tests
./bin/cbw-agent eval agents/specs/my_new_agent.agent.yaml

# Verbose output
./bin/cbw-agent eval agents/specs/my_new_agent.agent.yaml --verbose
```

### Manual Testing

Interactive testing:

```bash
# Test with different inputs
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
  --input "various test inputs" \
  --runtime local

# Test with different runtimes
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
  --input "test" \
  --runtime crewai

# Enable debug output
./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
  --input "test" \
  --verbose \
  --debug
```

## Advanced Topics

### Multi-Agent Collaboration

Create agents that work together:

```yaml
# Coordinator agent
name: coordinator_agent
tools:
  - name: agent_caller
    config:
      agents: [research_agent, analysis_agent]
```

### State Management

Agents with persistent state:

```yaml
runtime:
  framework: local
  config:
    state_backend: redis
    state_key: agent_state_{session_id}
```

### Custom Runtime Adapters

Integrate custom frameworks:

```python
# src/cbw_foundry/runtime/adapters/my_adapter.py
from cbw_foundry.runtime.base import BaseRuntime

class MyFrameworkAdapter(BaseRuntime):
    def run(self, spec, input, **kwargs):
        # Integrate with your framework
        pass
```

## Examples

### Example 1: Simple Q&A Agent

```yaml
name: qa_agent
version: "1.0.0"
description: "Answers questions based on knowledge base"

system_prompt: |
  You are a Q&A agent. Answer questions accurately and concisely.
  If you don't know, say so. Don't make up answers.

tools:
  - name: knowledge_base_search

runtime:
  framework: local
  model: gpt-4
  temperature: 0.3
```

### Example 2: Content Creation Agent

```yaml
name: content_creator
version: "1.0.0"
description: "Creates engaging content for various platforms"

system_prompt: |
  You are a content creation agent specialized in writing engaging content.
  
  Adapt tone and style based on platform:
  - Twitter: Concise, punchy, hashtags
  - LinkedIn: Professional, informative
  - Blog: Detailed, well-structured
  
  Always include relevant hashtags and calls-to-action.

tools:
  - name: content_analyzer
  - name: seo_optimizer
  - name: image_generator

runtime:
  framework: local
  model: gpt-4
  temperature: 0.8
```

### Example 3: Code Assistant Agent

```yaml
name: code_assistant
version: "1.0.0"
description: "Helps with code writing, review, and debugging"

system_prompt: |
  You are a code assistant specialized in Python, JavaScript, and Go.
  
  Capabilities:
  - Write clean, efficient code
  - Review code for bugs and issues
  - Debug problems
  - Suggest improvements
  - Explain complex concepts
  
  Always:
  - Follow language best practices
  - Include error handling
  - Add docstrings/comments
  - Consider edge cases

tools:
  - name: code_analyzer
  - name: test_generator
  - name: documentation_generator

runtime:
  framework: local
  model: gpt-4
  temperature: 0.5
```

## Troubleshooting

### Agent Won't Validate

**Error: Missing required fields**
```
Solution: Add all required fields (name, version, description, system_prompt)
```

**Error: Tool not found**
```
Solution: Check tool exists in registry/tools.json
        Update registry with: make index
```

**Error: Invalid YAML syntax**
```
Solution: Check indentation (use 2 spaces)
        Validate YAML: yamllint agents/specs/my_agent.agent.yaml
```

### Agent Behaves Incorrectly

**Problem: Agent doesn't use tools**
```
Solution: Be explicit in system prompt about when to use tools
        Example: "Use the search tool when you need current information"
```

**Problem: Agent output format wrong**
```
Solution: Specify exact format in system prompt with examples
        Add format validation in golden tests
```

**Problem: Agent too verbose/terse**
```
Solution: Adjust temperature in runtime config
        Modify system prompt guidelines
```

### Tests Failing

**Problem: Golden tests don't pass**
```
Solution: 1. Check if agent behavior changed (expected)
        2. Check if test expectations are correct
        3. Update tests or fix agent
        4. Re-run: make eval
```

**Problem: Timeout errors**
```
Solution: Increase timeout in runtime config:
        runtime:
          timeout: 600  # 10 minutes
```

## Quick Reference

```bash
# Create agent
./bin/cbw-capture agent NAME

# Validate
./bin/cbw-agent validate agents/specs/NAME.agent.yaml

# Test locally
./bin/cbw-agent run agents/specs/NAME.agent.yaml --input "test"

# Run evals
./bin/cbw-agent eval agents/specs/NAME.agent.yaml

# Compile
make compile

# Update registry
make index

# Full workflow
./bin/cbw-capture agent NAME
# Edit agents/specs/NAME.agent.yaml
# Edit agents/evals/NAME/golden_test.yaml
make validate compile eval index
git add agents/ dist/ registry/
git commit -m "feat(agents): add NAME"
```

---

**Last Updated:** 2026-01-15  
**Maintained By:** @cbwinslow  
**Related:** [Using the Repo](using_the_repo.md), [Code Quality Rules](../rules/code_quality_rules.md)
