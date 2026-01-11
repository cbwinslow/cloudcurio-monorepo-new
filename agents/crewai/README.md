# CrewAI Crews

This directory stores CrewAI crew configurations.

## Structure

Each crew should have its own subdirectory:

```
crews/
├── example_crew/
│   ├── crew_config.yaml
│   ├── agents.yaml
│   ├── tasks.yaml
│   └── README.md
```

## Crew Configuration Format

### crew_config.yaml

```yaml
name: "Example Crew"
description: "Description of what this crew does"
version: "1.0.0"
agents:
  - agent1
  - agent2
process: "sequential"  # or "hierarchical"
```

### agents.yaml

```yaml
agents:
  - name: "agent1"
    role: "Researcher"
    goal: "Research and gather information"
    backstory: "Expert in research and analysis"
    tools:
      - search
      - scrape
  
  - name: "agent2"
    role: "Writer"
    goal: "Write clear documentation"
    backstory: "Expert in technical writing"
    tools:
      - write
```

### tasks.yaml

```yaml
tasks:
  - description: "Task 1 description"
    agent: "agent1"
    expected_output: "Expected output format"
  
  - description: "Task 2 description"
    agent: "agent2"
    expected_output: "Expected output format"
```

## Usage

1. Create a new directory for your crew
2. Add configuration files
3. Use the crew in your CrewAI applications
4. Version control your crew configurations here
