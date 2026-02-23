# CloudCurio Quick Start Guide

Get started with CloudCurio agents, tools, and workflows in 15 minutes.

## Prerequisites

- Python 3.10+
- Ollama running locally (for LLM tools)
- Git

## Installation

```bash
# Clone repository
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo

# Bootstrap (creates venv, installs dependencies)
./scripts/bootstrap.sh

# Activate virtual environment
source venv/bin/activate

# Verify installation
make doctor
```

## Your First Agent

### 1. Create Agent Specification

Create `agents/specs/my_first_agent.agent.yaml`:

```yaml
api_version: v1
kind: Agent
metadata:
  name: my_first_agent
  version: 1.0.0
  description: My first CloudCurio agent
  tags: [quickstart]

spec:
  model_policy:
    preferred:
      provider: ollama
      model: qwen2.5-coder
  
  prompts:
    system: |
      You are a helpful assistant that can search the web and process data.
      Be concise and accurate in your responses.
  
  tools:
    - id: web_search
      type: python
      entrypoint: agents/tools/web_tools.py:search_engine_tool
    
    - id: llm_completion
      type: python
      entrypoint: agents/tools/llm_tools.py:llm_completion_tool
      config:
        temperature: 0.7
  
  runtime:
    supported: [local]
    timeout: 300
```

### 2. Validate Agent

```bash
./bin/cbw-agent validate agents/specs/my_first_agent.agent.yaml
```

### 3. Run Agent

```bash
./bin/cbw-agent run agents/specs/my_first_agent.agent.yaml \
  --input "Search for information about Python async programming" \
  --runtime local
```

## Your First Multi-Agent System

### 1. Create Swarm Script

Create `my_swarm.py`:

```python
#!/usr/bin/env python3
"""My first multi-agent swarm."""

from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode

# Create agents
agents = [
    SwarmAgent(
        name="researcher",
        role="worker",
        capabilities=["research"],
        confidence=0.9
    ),
    SwarmAgent(
        name="summarizer",
        role="worker",
        capabilities=["summarization"],
        confidence=0.85
    )
]

# Configure swarm for sequential execution
config = SwarmConfig(
    coordination_mode=CoordinationMode.SEQUENTIAL,
    max_iterations=2,
    timeout=300
)

# Create and run swarm
swarm = Swarm(name="research_swarm", agents=agents, config=config)

result = swarm.execute({
    "task": "Research Python best practices and summarize"
})

print(f"Success: {result.success}")
print(f"Time: {result.execution_time:.2f}s")
print(f"\nOutput:\n{result.output}")
```

### 2. Run Swarm

```bash
python my_swarm.py
```

## Your First Workflow

### 1. Create Workflow Definition

Create `workflows/my_workflow.yaml`:

```yaml
api_version: v1
kind: Workflow
metadata:
  name: my_first_workflow
  version: 1.0.0
  description: Simple research and report workflow
  tags: [quickstart]

spec:
  coordination: sequential
  
  steps:
    - id: research
      name: "Research Topic"
      agent: researcher
      input:
        task: "Research ${topic}"
      output_var: research_results
      timeout: 180
    
    - id: summarize
      name: "Summarize Findings"
      agent: summarizer
      input:
        task: "Summarize these findings"
        data: "${research_results}"
      output_var: summary
      depends_on: [research]
      timeout: 120
    
    - id: save
      name: "Save Report"
      action: file_write
      input:
        filepath: "output/report.md"
        content: "${summary}"
      depends_on: [summarize]

  outputs:
    report: "${summary}"
```

### 2. Run Workflow

```bash
./bin/cbw-workflow run workflows/my_workflow.yaml \
  --var topic="Machine Learning"
```

## Using Tools Directly

### LLM Completion

```python
from agents.tools.llm_tools import llm_completion_tool

# Create tool
llm = llm_completion_tool({
    "provider": "ollama",
    "model": "qwen2.5-coder"
})

# Use tool
result = llm.execute(
    prompt="Explain what is a closure in Python",
    temperature=0.5
)

print(result["text"])
```

### Web Scraping

```python
from agents.tools.web_tools import web_scraper_tool

# Create tool
scraper = web_scraper_tool()

# Scrape page
result = scraper.execute(
    url="https://example.com",
    selector="article h2"  # Get all h2 tags
)

print(result["content"])
```

### Data Processing

```python
from agents.tools.data_tools import data_transform_tool

# Create tool
transformer = data_transform_tool()

# Process data
data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 87},
    {"name": "Charlie", "score": 92}
]

result = transformer.execute(
    data=data,
    operation="filter",
    condition={"score": 90}
)

print(result["result"])  # Only scores >= 90
```

### System Monitoring

```python
from agents.tools.system_tools import system_info_tool

# Create tool
sysinfo = system_info_tool()

# Get info
result = sysinfo.execute(info_type="all")

print(f"CPU: {result['cpu']['cpu_percent']}%")
print(f"Memory: {result['memory']['percent']}%")
```

## Example Use Cases

### Use Case 1: Automated Research Report

```python
# 1. Search web for topic
from agents.tools.web_tools import search_engine_tool
search = search_engine_tool()
results = search.execute(query="AI agents", num_results=5)

# 2. Process and analyze
from agents.tools.llm_tools import llm_completion_tool
llm = llm_completion_tool()
analysis = llm.execute(
    prompt=f"Analyze these search results: {results['results']}"
)

# 3. Save report
from agents.tools.file_tools import file_writer_tool
writer = file_writer_tool()
writer.execute(
    filepath="research_report.md",
    content=analysis["text"]
)
```

### Use Case 2: Data Pipeline

```python
# 1. Read data file
from agents.tools.file_tools import file_reader_tool
reader = file_reader_tool()
data = reader.execute(filepath="data.csv")

# 2. Process CSV
from agents.tools.data_tools import csv_processor_tool
csv = csv_processor_tool()
parsed = csv.execute(data=data["content"], action="parse")

# 3. Transform data
from agents.tools.data_tools import data_transform_tool
transformer = data_transform_tool()
transformed = transformer.execute(
    data=parsed["records"],
    operation="sort",
    key="score",
    reverse=True
)

# 4. Generate statistics
stats = transformer.execute(
    data=transformed["result"],
    operation="aggregate",
    field="score",
    function="avg"
)

print(f"Average score: {stats['result']}")
```

### Use Case 3: System Health Dashboard

```python
from agents.tools.system_tools import (
    system_info_tool,
    health_check_tool,
    process_monitor_tool
)

# Get system info
sysinfo = system_info_tool()
info = sysinfo.execute(info_type="all")

# Health check
health = health_check_tool()
health_status = health.execute()

# Top processes
processes = process_monitor_tool()
top_procs = processes.execute(action="list")

# Display dashboard
print("=== System Health Dashboard ===")
print(f"OS: {info['os']['system']}")
print(f"CPU: {info['cpu']['cpu_percent']}%")
print(f"Memory: {info['memory']['percent']}%")
print(f"Healthy: {health_status['healthy']}")
print(f"\nTop Processes:")
for proc in top_procs['processes'][:5]:
    print(f"  {proc['name']}: {proc['cpu_percent']}%")
```

## Next Steps

### Explore Examples

```bash
# Run swarm examples
python agents/examples/sequential_swarm.py
python agents/examples/parallel_swarm.py
python agents/examples/democratic_swarm.py
python agents/examples/hierarchical_swarm.py

# Run workflows
./bin/cbw-workflow run workflows/library/research_and_report.workflow.yaml
./bin/cbw-workflow run workflows/library/parallel_data_processing.workflow.yaml
```

### Read Documentation

- **Multi-Agent Guide**: [agents/MULTI_AGENT_GUIDE.md](../agents/MULTI_AGENT_GUIDE.md)
- **Tool Registry**: [agents/tools/TOOL_REGISTRY.md](../agents/tools/TOOL_REGISTRY.md)
- **Agent Development**: [docs/AGENT_DEVELOPMENT.md](../docs/AGENT_DEVELOPMENT.md)
- **Swarm Architecture**: [docs/SWARM_ARCHITECTURE.md](../docs/SWARM_ARCHITECTURE.md)

### Create Your Own

1. **Design agent specs** for your use case
2. **Choose tools** from the registry
3. **Write custom tools** if needed
4. **Create workflows** to orchestrate
5. **Test thoroughly** with examples
6. **Deploy** and monitor

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull qwen2.5-coder
```

### Import Errors

```bash
# Reinstall package
pip install -e .

# Check PYTHONPATH
export PYTHONPATH="${PWD}/src:${PWD}"
```

### Tool Failures

```python
# Tools return status in results
result = tool.execute(...)

if result["status"] == "error":
    print(f"Error: {result['error']}")
    # Handle error
```

## Common Commands

```bash
# Health check
make doctor

# Run tests
make test

# Lint code
make lint

# Format code
make fmt

# Update indexes
make index

# Clean artifacts
make clean
```

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `agents/examples/`
- **Tools**: Browse `agents/tools/`
- **Workflows**: Explore `workflows/library/`
- **GitHub Issues**: Report bugs and request features

## What's Next?

You now have:
- ✅ A working agent
- ✅ A multi-agent swarm
- ✅ A workflow pipeline
- ✅ Tool usage examples

Continue with:
- [Multi-Agent Systems Guide](../agents/MULTI_AGENT_GUIDE.md)
- [Advanced Workflows](../docs/workflows/)
- [Custom Tool Development](../docs/TOOL_DEVELOPMENT.md)
- [Production Deployment](../docs/DOCKER_DEPLOYMENT.md)

Happy building! 🚀
