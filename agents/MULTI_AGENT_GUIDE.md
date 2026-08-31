# Multi-Agent Systems Guide

Comprehensive guide to building and using multi-agent systems in CloudCurio.

## Table of Contents

- [Overview](#overview)
- [Agent Types](#agent-types)
- [Coordination Patterns](#coordination-patterns)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

CloudCurio provides a complete framework for building multi-agent systems with different coordination patterns:

- **Sequential**: Agents work in order, each building on previous results
- **Parallel**: Agents work simultaneously on independent tasks
- **Democratic**: Agents vote on decisions using confidence weighting
- **Hierarchical**: Coordinator delegates to workers and aggregates results

## Agent Types

### Coordinator Agents
**Role**: Orchestrate multi-agent workflows

**Capabilities**:
- Task decomposition
- Agent delegation
- Result aggregation
- Workflow management

**Example Agents**:
- `task_coordinator` - General purpose coordinator
- `project_manager` - Software project coordination

**System Prompt**: [prompts/agents/coordinator_system.md](../../../prompts/agents/coordinator_system.md)

### Worker Agents
**Role**: Execute specific tasks

**Capabilities**:
- Focused task execution
- Tool usage
- Quality output generation
- Progress reporting

**Example Agents**:
- `researcher` - Web research and information gathering
- `data_analyst` - Data processing and analysis
- `writer` - Content creation
- `developer` - Code generation

**System Prompt**: [prompts/agents/worker_system.md](../../../prompts/agents/worker_system.md)

### Reviewer Agents
**Role**: Quality assurance and validation

**Capabilities**:
- Work review and validation
- Quality assessment
- Improvement suggestions
- Standards compliance

**Example Agents**:
- `code_reviewer` - Code quality and security review
- `editor` - Content review and editing
- `qa_specialist` - Testing and quality assurance

**System Prompt**: [prompts/agents/reviewer_system.md](../../../prompts/agents/reviewer_system.md)

### Specialist Agents
**Role**: Domain expertise

**Capabilities**:
- Specialized knowledge
- Technical analysis
- Expert recommendations
- Niche problem solving

**Example Agents**:
- `system_monitor` - System monitoring and diagnostics
- `security_analyst` - Security assessment
- `data_scientist` - Advanced analytics

## Coordination Patterns

### Sequential Pattern

**Use When**: Tasks must be completed in order

**Example**: Content creation pipeline
```
Research → Analysis → Writing → Editing → Publishing
```

**Code**:
```python
from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode

agents = [
    SwarmAgent(name="researcher", role="worker"),
    SwarmAgent(name="writer", role="worker"),
    SwarmAgent(name="editor", role="reviewer"),
]

config = SwarmConfig(coordination_mode=CoordinationMode.SEQUENTIAL)
swarm = Swarm(name="content_pipeline", agents=agents, config=config)

result = swarm.execute({"task": "Create blog post about AI"})
```

**Workflow**:
```yaml
spec:
  coordination: sequential
  steps:
    - id: research
      agent: researcher
      output_var: research_data

    - id: write
      agent: writer
      input: "${research_data}"
      depends_on: [research]
```

### Parallel Pattern

**Use When**: Tasks are independent and can run simultaneously

**Example**: Multi-source data collection
```
API Data ─┐
DB Data  ─┼─→ Merge → Analyze
Files    ─┘
```

**Code**:
```python
agents = [
    SwarmAgent(name="api_collector", role="worker"),
    SwarmAgent(name="db_collector", role="worker"),
    SwarmAgent(name="file_collector", role="worker"),
]

config = SwarmConfig(coordination_mode=CoordinationMode.PARALLEL)
swarm = Swarm(name="data_collection", agents=agents, config=config)

result = swarm.execute({"task": "Collect data from all sources"})
```

**Workflow**:
```yaml
spec:
  coordination: parallel
  steps:
    - id: collect_api
      agent: api_collector
      parallel_group: collection

    - id: collect_db
      agent: db_collector
      parallel_group: collection

    - id: merge
      agent: data_merger
      depends_on: [collect_api, collect_db]
```

### Democratic Pattern

**Use When**: Need consensus on decisions

**Example**: Architecture decision
```
Senior Arch (0.95) ─┐
Backend Lead (0.85) ─┤
Frontend Lead (0.85)─┼→ Vote → Best Solution
DevOps Eng (0.80)   ─┘
```

**Code**:
```python
agents = [
    SwarmAgent(name="senior_arch", role="specialist", confidence=0.95),
    SwarmAgent(name="backend_lead", role="worker", confidence=0.85),
    SwarmAgent(name="frontend_lead", role="worker", confidence=0.85),
    SwarmAgent(name="devops_eng", role="worker", confidence=0.80),
]

config = SwarmConfig(coordination_mode=CoordinationMode.DEMOCRATIC, enable_voting=True)
swarm = Swarm(name="design_team", agents=agents, config=config)

result = swarm.execute({"task": "Choose best architecture pattern"})
```

**Workflow**:
```yaml
spec:
  coordination: democratic
  voting:
    method: confidence_weighted
    threshold: 0.75
  steps:
    - id: vote
      coordination: vote
      voting_weights:
        senior_arch: 0.95
        backend_lead: 0.85
```

### Hierarchical Pattern

**Use When**: Need centralized coordination

**Example**: Software development team
```
Project Manager (Coordinator)
    ├─→ Backend Dev
    ├─→ Frontend Dev
    ├─→ Database Specialist
    └─→ DevOps Engineer
```

**Code**:
```python
agents = [
    SwarmAgent(name="pm", role="coordinator"),
    SwarmAgent(name="backend_dev", role="worker"),
    SwarmAgent(name="frontend_dev", role="worker"),
    SwarmAgent(name="devops", role="worker"),
]

config = SwarmConfig(coordination_mode=CoordinationMode.HIERARCHICAL)
swarm = Swarm(name="dev_team", agents=agents, config=config)

result = swarm.execute({"task": "Build authentication system"})
```

## Quick Start

### 1. Run Pre-built Examples

```bash
# Sequential pattern
python agents/examples/sequential_swarm.py

# Parallel pattern
python agents/examples/parallel_swarm.py

# Democratic pattern
python agents/examples/democratic_swarm.py

# Hierarchical pattern
python agents/examples/hierarchical_swarm.py
```

### 2. Create Your First Swarm

```python
#!/usr/bin/env python3
from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode

# Define agents
agents = [
    SwarmAgent(
        name="researcher", role="worker", capabilities=["research", "analysis"], confidence=0.9
    ),
    SwarmAgent(name="writer", role="worker", capabilities=["writing", "editing"], confidence=0.85),
]

# Configure swarm
config = SwarmConfig(coordination_mode=CoordinationMode.SEQUENTIAL, max_iterations=2, timeout=300)

# Create swarm
swarm = Swarm(name="my_swarm", agents=agents, config=config)

# Execute task
result = swarm.execute(
    {"task": "Research and write about quantum computing", "length": "500 words"}
)

# Check results
print(f"Success: {result.success}")
print(f"Output: {result.output}")
```

### 3. Run a Workflow

```bash
# Run research workflow
./bin/cbw-workflow run workflows/library/research_and_report.workflow.yaml \
  --var topic="AI agents"

# Run parallel data processing
./bin/cbw-workflow run workflows/library/parallel_data_processing.workflow.yaml \
  --var api_endpoints="[...]"

# Run democratic decision making
./bin/cbw-workflow run workflows/library/democratic_decision_making.workflow.yaml \
  --var problem_context="Choose database technology"
```

## Examples

### Example 1: Research Pipeline

```python
from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig, CoordinationMode

# Create research team
researchers = [
    SwarmAgent(name="tech_researcher", role="worker", confidence=0.9),
    SwarmAgent(name="market_researcher", role="worker", confidence=0.85),
    SwarmAgent(name="analyst", role="worker", confidence=0.88),
]

# Sequential: research → analyze → summarize
config = SwarmConfig(coordination_mode=CoordinationMode.SEQUENTIAL)
pipeline = Swarm(name="research_pipeline", agents=researchers, config=config)

result = pipeline.execute({"topic": "AI market trends 2024"})
```

### Example 2: Code Review Team

```python
# Create review team with different expertise
reviewers = [
    SwarmAgent(name="security_reviewer", role="reviewer", confidence=0.95),
    SwarmAgent(name="performance_reviewer", role="reviewer", confidence=0.88),
    SwarmAgent(name="style_reviewer", role="reviewer", confidence=0.82),
]

# Parallel reviews, then aggregate feedback
config = SwarmConfig(coordination_mode=CoordinationMode.PARALLEL)
review_team = Swarm(name="code_reviewers", agents=reviewers, config=config)

result = review_team.execute({"code_path": "src/my_module.py"})
```

### Example 3: Decision Making Committee

```python
# Create decision committee
committee = [
    SwarmAgent(name="cto", role="specialist", confidence=0.95),
    SwarmAgent(name="lead_architect", role="specialist", confidence=0.90),
    SwarmAgent(name="senior_dev_1", role="worker", confidence=0.85),
    SwarmAgent(name="senior_dev_2", role="worker", confidence=0.85),
]

# Democratic voting
config = SwarmConfig(
    coordination_mode=CoordinationMode.DEMOCRATIC, enable_voting=True, quality_threshold=0.80
)
committee_swarm = Swarm(name="tech_committee", agents=committee, config=config)

result = committee_swarm.execute({"decision": "Choose microservices architecture pattern"})
```

## Best Practices

### 1. Choose the Right Pattern

- **Sequential**: When order matters and tasks depend on each other
- **Parallel**: When tasks are independent and speed is important
- **Democratic**: When you need consensus and have multiple valid approaches
- **Hierarchical**: When you need centralized control and coordination

### 2. Design Clear Agent Roles

```python
# Good: Specific, focused capabilities
SwarmAgent(
    name="backend_api_developer",
    role="worker",
    capabilities=["rest_api", "database", "python"],
    confidence=0.85,
)

# Avoid: Too broad or vague
SwarmAgent(name="developer", role="worker", capabilities=["coding"], confidence=0.8)
```

### 3. Set Appropriate Confidence Levels

- **0.90-1.00**: Senior experts, specialists
- **0.80-0.89**: Experienced professionals
- **0.70-0.79**: Mid-level practitioners
- **0.60-0.69**: Junior or learning agents
- **Below 0.60**: Trainee or experimental agents

### 4. Handle Errors Gracefully

```python
config = SwarmConfig(
    coordination_mode=CoordinationMode.SEQUENTIAL,
    max_iterations=3,  # Allow retries
    timeout=300,  # Set reasonable timeout
)

result = swarm.execute(task)

if not result.success:
    print(f"Error: {result.error}")
    # Handle failure appropriately
```

### 5. Monitor and Log

```python
import logging

logging.basicConfig(level=logging.INFO)

swarm = Swarm(name="monitored_swarm", agents=agents, config=config)
result = swarm.execute(task)

print(f"Iterations: {result.iterations}")
print(f"Execution time: {result.execution_time:.2f}s")
print(f"Agent outputs: {result.agent_outputs}")
```

### 6. Start Simple, Scale Up

1. **Start**: Single agent performing task
2. **Add**: Second agent for quality review
3. **Expand**: Multiple parallel agents for speed
4. **Optimize**: Add coordination and voting

### 7. Test Thoroughly

```python
# Test individual agents first
agent = SwarmAgent(name="test_agent", role="worker")
# ... validate agent behavior

# Then test coordination
swarm = Swarm(name="test_swarm", agents=[agent1, agent2], config=config)
# ... validate swarm behavior
```

## Related Documentation

- [Swarm Architecture](../../../docs/SWARM_ARCHITECTURE.md)
- [Agent Development](../../../docs/AGENT_DEVELOPMENT.md)
- [Tool Development](../../../docs/TOOL_DEVELOPMENT.md)
- [Workflow Guide](../../../docs/workflows/README.md)

## Support

For questions and issues:
- Check documentation in `docs/`
- Review examples in `agents/examples/`
- See workflows in `workflows/library/`
- Open an issue on GitHub
