# CloudCurio Practical Usage Guide

Real-world examples of using CloudCurio agents, tools, and skills.

## Installation

```bash
# 1. Bootstrap
cd /path/to/cloudcurio-monorepo
./scripts/bootstrap.sh

# 2. Install integrations
./scripts/install_integrations.sh all

# 3. Activate environment
source activate_cloudcurio.sh
```

## Using Tools Directly

### LLM Completions

```python
from agents.tools.llm_tools import llm_completion_tool

llm = llm_completion_tool({"provider": "ollama", "model": "qwen2.5-coder", "temperature": 0.7})

result = llm.execute(prompt="Explain Python decorators")
print(result["text"])
```

### Web Research

```python
from agents.tools.web_tools import search_engine_tool, web_scraper_tool

# Search
search = search_engine_tool()
results = search.execute(query="Python async programming", num_results=5)

# Scrape
scraper = web_scraper_tool()
content = scraper.execute(url="https://example.com", selector="article")
print(content["content"])
```

### File Operations

```python
from agents.tools.file_tools import file_reader_tool, file_writer_tool

# Read
reader = file_reader_tool()
data = reader.execute(filepath="data.txt")

# Write
writer = file_writer_tool({"base_path": "output"})
writer.execute(filepath="result.txt", content="Hello World")
```

### Data Processing

```python
from agents.tools.data_tools import data_transform_tool

transformer = data_transform_tool()

data = [
    {"name": "Alice", "score": 95, "grade": "A"},
    {"name": "Bob", "score": 87, "grade": "B"},
    {"name": "Charlie", "score": 92, "grade": "A"},
]

# Filter
filtered = transformer.execute(data=data, operation="filter", condition={"grade": "A"})
print(filtered["result"])

# Aggregate
avg = transformer.execute(data=data, operation="aggregate", field="score", function="avg")
print(f"Average score: {avg['result']}")
```

### System Monitoring

```python
from agents.tools.system_tools import system_info_tool, health_check_tool

# System info
sysinfo = system_info_tool()
info = sysinfo.execute(info_type="all")
print(f"CPU: {info['cpu']['cpu_percent']}%")
print(f"Memory: {info['memory']['percent']}%")

# Health check
health = health_check_tool()
status = health.execute(thresholds={"cpu_percent": 80, "memory_percent": 85})
print(f"Healthy: {status['healthy']}")
```

## Using Slash Commands

```bash
# Start Python REPL
python3

>>> from cbw_foundry.skills.commands import execute_command
>>>
>>> # Research
>>> result = execute_command('/research topic="AI agents" depth="standard"')
>>> print(result)
>>>
>>> # Analyze data
>>> result = execute_command('/analyze source="data.csv" operations="stats"')
>>> print(result)
>>>
>>> # Review code
>>> result = execute_command('/review path="src/module.py" focus="security"')
>>> print(result)
>>>
>>> # Generate content
>>> result = execute_command('/generate type="blog" topic="AI" length="medium"')
>>> print(result)
>>>
>>> # Monitor system
>>> result = execute_command('/monitor target="cpu" duration=10')
>>> print(result)
```

## Using Agents

### Single Agent

```python
# Load and run agent spec
from cbw_foundry.agent_cli import run_agent

result = run_agent(
    spec_path="agents/specs/researcher.agent.yaml",
    input_data={"task": "Research AI trends"},
    runtime="local",
)
print(result)
```

### Multi-Agent Swarm

```python
from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode

# Create agents
agents = [
    SwarmAgent(name="researcher", role="worker", confidence=0.9),
    SwarmAgent(name="writer", role="worker", confidence=0.85),
    SwarmAgent(name="editor", role="reviewer", confidence=0.9),
]

# Create swarm
swarm = Swarm(
    name="content_team",
    agents=agents,
    config=SwarmConfig(coordination_mode=CoordinationMode.SEQUENTIAL),
)

# Execute
result = swarm.execute({"task": "Create article about AI"})
print(f"Success: {result.success}")
print(f"Output: {result.output}")
```

## Running Workflows

```bash
# Research workflow
./bin/cbw-workflow run workflows/library/research_and_report.workflow.yaml \
  --var topic="Quantum Computing"

# Parallel data processing
./bin/cbw-workflow run workflows/library/parallel_data_processing.workflow.yaml \
  --var api_endpoints='["http://api1.com", "http://api2.com"]'

# Democratic decision
./bin/cbw-workflow run workflows/library/democratic_decision_making.workflow.yaml \
  --var problem_context="Choose database technology"
```

## Automation Scripts

### Automated Blog Post Generation

```python
#!/usr/bin/env python3
"""Generate blog post automatically."""

from agents.tools.web_tools import search_engine_tool
from agents.tools.llm_tools import llm_completion_tool
from agents.tools.file_tools import file_writer_tool


def generate_blog_post(topic):
    # Research
    search = search_engine_tool()
    results = search.execute(query=topic, num_results=5)
    sources = results["results"]

    # Generate content
    llm = llm_completion_tool()
    prompt = f"""Write a blog post about {topic}.

Use these sources:
{chr(10).join([f"- {s['title']}" for s in sources])}

Make it engaging and informative.
"""
    content = llm.execute(prompt=prompt)

    # Save
    writer = file_writer_tool({"base_path": "output"})
    filename = f"blog_{topic.replace(' ', '_').lower()}.md"
    writer.execute(filepath=filename, content=content["text"])

    print(f"Blog post saved to output/{filename}")


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "AI Trends"
    generate_blog_post(topic)
```

### Automated Data Analysis

```python
#!/usr/bin/env python3
"""Analyze dataset automatically."""

from agents.tools.file_tools import file_reader_tool
from agents.tools.data_tools import csv_processor_tool, data_transform_tool
from agents.tools.llm_tools import llm_completion_tool


def analyze_data(filepath):
    # Load data
    reader = file_reader_tool()
    data = reader.execute(filepath=filepath)

    # Parse CSV
    csv = csv_processor_tool()
    parsed = csv.execute(data=data["content"], action="parse")
    records = parsed["records"]

    # Calculate statistics
    transformer = data_transform_tool()
    stats = {}

    if records:
        numeric_fields = [k for k, v in records[0].items() if isinstance(v, (int, float))]

        for field in numeric_fields[:5]:
            avg = transformer.execute(
                data=records, operation="aggregate", field=field, function="avg"
            )
            stats[field] = avg["result"]

    # Generate insights
    llm = llm_completion_tool()
    insights = llm.execute(prompt=f"Analyze this data and provide insights: {stats}")

    print(f"Dataset: {filepath}")
    print(f"Records: {len(records)}")
    print(f"\nStatistics: {stats}")
    print(f"\nInsights:\n{insights['text']}")


if __name__ == "__main__":
    import sys

    filepath = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
    analyze_data(filepath)
```

### System Health Dashboard

```python
#!/usr/bin/env python3
"""Display system health dashboard."""

from agents.tools.system_tools import system_info_tool, health_check_tool, process_monitor_tool
import time


def show_dashboard():
    sysinfo = system_info_tool()
    health = health_check_tool()
    processes = process_monitor_tool()

    while True:
        # Clear screen
        print("\033[2J\033[H")

        # System info
        info = sysinfo.execute(info_type="all")
        print("=" * 60)
        print("SYSTEM HEALTH DASHBOARD")
        print("=" * 60)

        print(f"\nOS: {info['os']['system']} {info['os']['release']}")
        print(f"CPU: {info['cpu']['cpu_percent']}% | Cores: {info['cpu']['logical_cores']}")
        print(
            f"Memory: {info['memory']['percent']}% | {info['memory']['used'] // 1024 // 1024}MB used"
        )
        print(
            f"Disk: {info['disk']['percent']}% | {info['disk']['free'] // 1024 // 1024 // 1024}GB free"
        )

        # Health status
        health_status = health.execute()
        status = "✓ HEALTHY" if health_status["healthy"] else "✗ UNHEALTHY"
        print(f"\nStatus: {status}")

        # Top processes
        top = processes.execute(action="list")
        print(f"\nTop Processes:")
        for proc in top["processes"][:5]:
            print(f"  {proc['name']:<20} CPU: {proc['cpu_percent']}%")

        print("\n" + "=" * 60)
        print("Press Ctrl+C to exit")

        time.sleep(5)


if __name__ == "__main__":
    try:
        show_dashboard()
    except KeyboardInterrupt:
        print("\nDashboard stopped")
```

## Integration with AI Tools

### Via GitHub Copilot

```python
# Just write a comment and let Copilot suggest
# Copilot will use .github/copilot/instructions.md

# Research a topic
# Use cloudcurio to research AI agents

# Analyze data
# Use cloudcurio to analyze sales_data.csv

# Review code
# Use cloudcurio to review this file for security issues
```

### Via Cursor

```
# In Cursor chat:
"Use cloudcurio to research AI trends"
"Run /analyze on data.csv"
"Execute /review on src/"
```

### Via CLI

```bash
# Kilocode
kilocode skill /research topic="AI"

# Gemini
gemini skill /analyze source="data.csv"

# OpenCode
/cloudcurio research "AI agents"
```

## Tips & Tricks

### Chaining Tools

```python
from agents.tools.web_tools import search_engine_tool
from agents.tools.llm_tools import llm_completion_tool

# Search + Summarize
search = search_engine_tool()
llm = llm_completion_tool()

results = search.execute(query="Python async", num_results=3)
summary = llm.execute(prompt=f"Summarize these search results: {results['results']}")
print(summary["text"])
```

### Error Handling

```python
from agents.tools.llm_tools import llm_completion_tool

llm = llm_completion_tool()
result = llm.execute(prompt="Test")

if result["status"] == "success":
    print(result["text"])
else:
    print(f"Error: {result['error']}")
```

### Configuration

```python
from agents.tools.llm_tools import llm_completion_tool

# Custom configuration
llm = llm_completion_tool(
    {
        "provider": "ollama",
        "model": "qwen2.5-coder",
        "temperature": 0.3,  # Lower for more deterministic
        "max_tokens": 4000,  # Longer responses
    }
)

result = llm.execute(prompt="Explain in detail...")
```

### Batch Processing

```python
from agents.tools.file_tools import directory_tool, file_reader_tool
from agents.tools.data_tools import data_transform_tool

# Process all CSV files in directory
dir_tool = directory_tool()
files = dir_tool.execute(action="list", dirpath="data", pattern="*.csv")

reader = file_reader_tool()
transformer = data_transform_tool()

for file_info in files["files"]:
    if file_info["type"] == "file":
        print(f"Processing {file_info['name']}...")
        # Process file
```

## Common Patterns

### Research Pipeline
1. Search web → 2. Extract content → 3. Synthesize → 4. Generate report

### Data Pipeline
1. Load data → 2. Transform → 3. Analyze → 4. Generate insights

### Code Review Pipeline
1. Read code → 2. Analyze → 3. Check security → 4. Generate feedback

### Content Pipeline
1. Research → 2. Generate draft → 3. Edit → 4. Publish

## Next Steps

- Explore more examples in `examples/use_cases/`
- Try swarm coordination in `agents/examples/`
- Create custom agents using templates
- Build custom workflows
- Integrate with your favorite AI tool

## Support

- Documentation: `docs/`
- Examples: `examples/`
- Templates: `templates/`
- Issues: GitHub Issues
