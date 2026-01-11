# Example Research Crew

This is an example CrewAI crew configuration for a research and documentation team.

## Overview

This crew consists of two agents:
1. **Researcher** - Gathers information and performs analysis
2. **Writer** - Creates documentation from research findings

## Files

- `crew_config.yaml` - Main crew configuration
- `agents.yaml` - Agent definitions
- `tasks.yaml` - Task definitions

## Usage

```python
from crewai import Crew, Agent, Task
import yaml

# Load configurations
with open('crew_config.yaml') as f:
    crew_config = yaml.safe_load(f)

with open('agents.yaml') as f:
    agents_config = yaml.safe_load(f)

with open('tasks.yaml') as f:
    tasks_config = yaml.safe_load(f)

# Create crew and run
crew = Crew(
    agents=[...],
    tasks=[...],
    process=crew_config['process']
)

result = crew.kickoff()
```

## Customization

Modify the YAML files to:
- Add more agents
- Change agent roles and goals
- Define new tasks
- Adjust the process flow
