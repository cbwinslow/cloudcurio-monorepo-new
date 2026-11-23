# GitHub Copilot Instructions for CloudCurio

## Project Context

CloudCurio is a comprehensive AI agent framework with multi-agent coordination, tools, workflows, and skills.

### Key Components

1. **Agents** (`agents/specs/`, `agents/library/`)
   - Defined in YAML specs
   - Roles: coordinator, worker, reviewer, specialist
   - Use tools and workflows

2. **Tools** (`agents/tools/`)
   - LLM tools: completions, embeddings
   - Web tools: scraping, API calls, search
   - File tools: read, write, directory operations
   - Data tools: JSON, CSV, transformations
   - System tools: monitoring, health checks

3. **Workflows** (`workflows/library/`)
   - Sequential, parallel, democratic, hierarchical
   - Defined in YAML
   - Coordinate multiple agents

4. **Skills** (`skills/`)
   - Slash command interface
   - Combines agents and workflows
   - Examples: /research, /analyze, /review

5. **Swarm System** (`src/cbw_foundry/swarm/`)
   - Multi-agent coordination
   - Voting mechanisms
   - Task delegation

## Code Conventions

### Python Code Style

- **Type Hints**: Always use type hints
- **Docstrings**: Google-style docstrings
- **Line Length**: 100 characters max
- **Imports**: Organize with `from __future__ import annotations`
- **Error Handling**: Return `{"status": "success|error"}` dicts

### File Naming

- **Agents**: `agent_name.agent.yaml`
- **Workflows**: `workflow_name.workflow.yaml`
- **Skills**: `skill_name.skill.yaml`
- **Tools**: `tool_name.py` with `tool_name_tool()` factory

### Agent Specs

```yaml
api_version: v1
kind: Agent
metadata:
  name: agent_name
  version: 1.0.0
  tags: [category, type]
spec:
  model_policy:
    preferred:
      provider: ollama
      model: qwen2.5-coder
  prompts:
    system: "..."
  tools:
    - id: tool_name
      type: python
      entrypoint: path:function
  runtime:
    supported: [local, langchain, crewai]
```

### Tool Pattern

```python
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    param: str = Field(description="...")


class ToolName:
    name: str = "tool_name"
    description: str = "..."

    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            # Implementation
            return {"status": "success", "output": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def tool_name_tool(config: Optional[Dict] = None) -> ToolName:
    cfg = ToolConfig(**config) if config else ToolConfig()
    return ToolName(cfg)
```

## Common Tasks

### Creating New Agent

1. Copy `templates/agents/agent.template.yaml`
2. Replace placeholders
3. Add to `agents/specs/`
4. Reference in workflows/skills

### Creating New Tool

1. Copy `templates/tools/tool.template.py`
2. Implement `execute()` method
3. Add to `agents/tools/`
4. Update tool registry

### Creating New Skill

1. Copy `templates/skills/skill.template.yaml`
2. Define command and parameters
3. Link agents/workflow
4. Add to `skills/`

### Creating New Workflow

1. Copy `templates/workflows/workflow.template.yaml`
2. Define steps with agents
3. Set dependencies
4. Add to `workflows/library/`

## Integration Points

### MCP Servers

Configuration in `configs/mcp-servers.json`:
- automation
- media
- web-research
- data-processing
- system-monitor
- llm-tools

### Runtime Adapters

- **Local**: Fully implemented
- **LangChain**: Stub (needs implementation)
- **CrewAI**: Stub (needs implementation)
- **PydanticAI**: Stub (needs implementation)

## Best Practices

1. **Use Existing Tools**: Check `agents/tools/TOOL_REGISTRY.md`
2. **Follow Templates**: Use templates for consistency
3. **Add Examples**: Include usage examples in docstrings
4. **Test Thoroughly**: Validate all configurations
5. **Document**: Update relevant documentation

## Quick Reference

### Import Swarm Components

```python
from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode
```

### Import Skills

```python
from cbw_foundry.skills import get_registry, execute_command
```

### Import Tools

```python
from agents.tools.llm_tools import llm_completion_tool
from agents.tools.web_tools import web_scraper_tool
from agents.tools.file_tools import file_reader_tool
```

## Help Resources

- **Multi-Agent Guide**: `agents/MULTI_AGENT_GUIDE.md`
- **Tool Registry**: `agents/tools/TOOL_REGISTRY.md`
- **Quickstart**: `docs/QUICKSTART_GUIDE.md`
- **Swarm Architecture**: `docs/SWARM_ARCHITECTURE.md`
