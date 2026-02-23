# CloudCurio Integration for Gemini CLI

## Overview

This integration enables Gemini CLI to use CloudCurio agents, tools, and skills.

## Setup

1. Install Gemini CLI (if not installed)
2. Configure CloudCurio integration:

```bash
cd /path/to/cloudcurio-monorepo
./integrations/gemini/install.sh
```

## Configuration

File: `gemini.config.yaml`

```yaml
project: cloudcurio-agents
version: 0.4.0

# Tools Configuration
tools:
  provider: mcp
  server:
    command: python3
    args: ["-m", "cbw_foundry.mcp.unified_server"]
    env:
      PYTHONPATH: "${workspaceFolder}/src:${workspaceFolder}"
      OLLAMA_HOST: "http://localhost:11434"
  
  available:
    - llm_completion
    - web_search
    - web_scrape
    - file_read
    - file_write
    - data_transform
    - system_monitor

# Agents Configuration
agents:
  specs_dir: agents/specs
  available:
    - name: researcher
      spec: researcher.agent.yaml
    - name: data_analyst
      spec: data_analyst.agent.yaml
    - name: code_reviewer
      spec: code_reviewer.agent.yaml
    - name: task_coordinator
      spec: task_coordinator.agent.yaml

# Skills Configuration
skills:
  specs_dir: skills
  commands:
    - /research
    - /analyze
    - /review
    - /generate
    - /monitor

# Model Configuration
models:
  default: gemini-pro
  fallback: gemini-pro-vision
  
# Integration Settings
settings:
  auto_load_tools: true
  auto_discover_agents: true
  enable_skills: true
  cache_duration: 3600
```

## Usage

### Using Tools

```python
# Via Gemini CLI
gemini --tool llm_completion --prompt "Explain async programming"
gemini --tool web_search --query "Python best practices"
```

### Using Agents

```python
# Run agent via Gemini
gemini agent researcher --input "Research AI trends 2024"
gemini agent code_reviewer --input "Review src/module.py"
```

### Using Skills

```python
# Execute skills via Gemini
gemini skill /research topic="quantum computing"
gemini skill /analyze source="data.csv"
gemini skill /review path="src/"
```

## API Integration

```python
from gemini_cli import GeminiClient

# Initialize with CloudCurio tools
client = GeminiClient(tools_config="integrations/gemini/gemini.config.yaml")

# Use CloudCurio tools
result = client.use_tool("web_search", query="AI agents")

# Run CloudCurio agent
response = client.run_agent("researcher", input="Research topic")

# Execute skill
output = client.execute_skill("/research", params={"topic": "AI"})
```

## Environment Variables

```bash
# Required
export GOOGLE_API_KEY="your-api-key"
export PYTHONPATH="/path/to/cloudcurio-monorepo/src:${PYTHONPATH}"

# Optional
export OLLAMA_HOST="http://localhost:11434"
export CLOUDCURIO_TOOLS_TIMEOUT=300
export CLOUDCURIO_CACHE_DIR="$HOME/.cache/cloudcurio"
```

## Troubleshooting

### Tools Not Loading

```bash
# Check MCP server
python3 -m cbw_foundry.mcp.unified_server --test

# Verify PYTHONPATH
echo $PYTHONPATH
```

### Agent Spec Errors

```bash
# Validate agent specs
./bin/cbw-agent validate agents/specs/*.agent.yaml
```

### Skill Discovery Issues

```bash
# List available skills
python3 -c "from cbw_foundry.skills import discover_skills, get_registry; discover_skills('skills'); print(get_registry().list_skills())"
```

## Examples

### Research Workflow

```bash
# Research and generate report
gemini skill /research topic="AI safety" depth="comprehensive" sources=10
```

### Data Analysis

```bash
# Analyze CSV data
gemini skill /analyze source="sales_data.csv" operations="stats,filter"
```

### Code Review

```bash
# Review code with security focus
gemini skill /review path="src/" focus="security" severity="critical"
```

## Advanced Usage

### Custom Tool Registration

```python
from gemini_cli import register_tool
from agents.tools.custom_tool import custom_tool

# Register CloudCurio tool
register_tool("custom_tool", custom_tool())
```

### Multi-Agent Workflows

```python
# Run multi-agent workflow
client.run_workflow("workflows/library/research_and_report.workflow.yaml", 
                   vars={"topic": "AI trends"})
```

## Support

- Documentation: `docs/`
- Examples: `agents/examples/`
- Issues: GitHub Issues
