# Swarm Architecture

Multi-agent coordination system for CloudCurio.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Implementation](#implementation)
- [Communication](#communication)
- [Coordination Patterns](#coordination-patterns)

## Overview

The Swarm subsystem provides distributed multi-agent coordination, enabling agents to collaborate on complex tasks through structured communication and governance.

### Key Features

- **Distributed Coordination**: Agents coordinate without centralized control
- **Democratic Decision Making**: Confidence-weighted voting for quality
- **Task Decomposition**: Break complex tasks into agent-specific subtasks
- **State Management**: Shared knowledge base with conflict resolution
- **Quality Assurance**: Built-in governance and quality checks

## Core Concepts

### Swarm

Collection of agents working toward a common goal:

```python
from cbw_foundry.swarm import Swarm, SwarmConfig

swarm = Swarm(
    name="content_pipeline",
    agents=[generator, reviewer, publisher],
    config=SwarmConfig(
        coordination_mode="democratic",
        max_iterations=10,
        quality_threshold=0.8
    )
)

result = swarm.execute(task="Create blog post about AI")
```

### Agent Roles

Agents in swarms have specific roles:

- **Coordinator**: Manages task flow and delegation
- **Worker**: Executes specific subtasks
- **Reviewer**: Quality checks and validation
- **Specialist**: Domain-specific expertise

### Communication

Agents communicate through structured messages:

```python
from cbw_foundry.swarm.communication import Message, MessageType

message = Message(
    type=MessageType.TASK_REQUEST,
    sender="coordinator_agent",
    recipient="worker_agent",
    content={
        "task": "Generate content",
        "deadline": "2026-01-24T12:00:00Z"
    }
)
```

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│           Swarm Orchestrator            │
│  (Task coordination & load balancing)   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│   Agent A   │  │   Agent B   │
│  (Worker)   │  │  (Reviewer) │
└──────┬──────┘  └─────┬───────┘
       │                │
       └────────┬───────┘
                │
     ┌──────────▼──────────┐
     │  Knowledge Base     │
     │  (Shared State)     │
     └─────────────────────┘
```

### Core Modules

**swarm/core/**
- Orchestrator - Task coordination
- Agent registry - Agent discovery
- Load balancer - Work distribution

**swarm/communication/**
- Message bus - Agent messaging
- Protocol handlers - Communication protocols
- Event system - Event-driven coordination

**swarm/governance/**
- Quality gates - Quality enforcement
- Policy engine - Rule enforcement
- Consensus - Democratic decision making

**swarm/knowledge/**
- Knowledge base - Shared state
- Memory manager - Context management
- Conflict resolution - State synchronization

## Implementation

### Creating a Swarm

```python
from cbw_foundry.swarm import Swarm, SwarmAgent
from cbw_foundry.swarm.core import Orchestrator
from cbw_foundry.swarm.governance import DemocraticGovernance

# Define agents
content_generator = SwarmAgent(
    name="content_generator",
    role="worker",
    capabilities=["content_generation", "writing"],
    confidence=0.9
)

content_reviewer = SwarmAgent(
    name="content_reviewer",
    role="reviewer",
    capabilities=["review", "quality_check"],
    confidence=0.85
)

publisher = SwarmAgent(
    name="publisher",
    role="worker",
    capabilities=["publishing", "distribution"],
    confidence=0.8
)

# Create swarm
swarm = Swarm(
    name="content_pipeline",
    agents=[content_generator, content_reviewer, publisher],
    orchestrator=Orchestrator(strategy="sequential"),
    governance=DemocraticGovernance(voting_threshold=0.7)
)

# Execute task
result = swarm.execute({
    "task": "Create and publish blog post",
    "topic": "AI agent coordination",
    "deadline": "2026-01-24"
})
```

### Coordination Strategies

**Sequential**: Execute agents in order

```python
orchestrator = Orchestrator(strategy="sequential")
# Generator → Reviewer → Publisher
```

**Parallel**: Execute agents concurrently

```python
orchestrator = Orchestrator(strategy="parallel")
# All agents work simultaneously
```

**Democratic**: Agents vote on decisions

```python
orchestrator = Orchestrator(
    strategy="democratic",
    governance=DemocraticGovernance()
)
# Agents collaborate through voting
```

### Agent Communication

```python
from cbw_foundry.swarm.communication import MessageBus, Message

# Create message bus
bus = MessageBus()

# Subscribe agent to topics
bus.subscribe(agent_id="reviewer", topic="content_ready")

# Publish message
bus.publish(Message(
    type="content_ready",
    sender="generator",
    data={"content": "...", "metadata": {}}
))

# Agent receives message
messages = bus.receive(agent_id="reviewer")
```

### Knowledge Sharing

```python
from cbw_foundry.swarm.knowledge import KnowledgeBase

kb = KnowledgeBase()

# Store knowledge
kb.store(
    key="project_requirements",
    value={"tone": "professional", "length": 1000},
    agent_id="coordinator"
)

# Retrieve knowledge
requirements = kb.retrieve(key="project_requirements")

# Update knowledge
kb.update(
    key="project_requirements",
    value={"tone": "casual", "length": 800},
    agent_id="reviewer"
)
```

## Communication

### Message Types

```python
class MessageType:
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    KNOWLEDGE_SHARE = "knowledge_share"
    VOTE_REQUEST = "vote_request"
    VOTE_RESPONSE = "vote_response"
    ERROR = "error"
```

### Message Structure

```python
@dataclass
class Message:
    type: MessageType
    sender: str
    recipient: Optional[str]
    content: Dict[str, Any]
    timestamp: str
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Communication Patterns

**Request-Response**:

```python
# Agent A sends request
request = Message(
    type=MessageType.TASK_REQUEST,
    sender="agent_a",
    recipient="agent_b",
    content={"task": "analyze_data"}
)
bus.publish(request)

# Agent B responds
response = Message(
    type=MessageType.TASK_RESPONSE,
    sender="agent_b",
    recipient="agent_a",
    content={"result": {...}}
)
bus.publish(response)
```

**Broadcast**:

```python
# Coordinator broadcasts to all agents
broadcast = Message(
    type=MessageType.STATUS_UPDATE,
    sender="coordinator",
    recipient=None,  # Broadcast
    content={"status": "task_complete"}
)
bus.broadcast(broadcast)
```

## Coordination Patterns

### Pipeline Pattern

Agents work in sequence, each building on previous work:

```python
pipeline = [
    ("data_collector", "collect_data"),
    ("data_processor", "process_data"),
    ("data_analyzer", "analyze_data"),
    ("report_generator", "generate_report")
]

swarm = Swarm(
    agents=agents,
    orchestrator=Orchestrator(
        strategy="pipeline",
        pipeline=pipeline
    )
)
```

### Map-Reduce Pattern

Distribute work across agents, aggregate results:

```python
# Map phase: distribute tasks
tasks = [
    {"agent": "worker_1", "data": chunk_1},
    {"agent": "worker_2", "data": chunk_2},
    {"agent": "worker_3", "data": chunk_3}
]

# Reduce phase: aggregate results
results = swarm.map_reduce(
    tasks=tasks,
    reducer=aggregator_agent
)
```

### Consensus Pattern

Agents vote on decisions:

```python
# Request votes
vote_request = {
    "question": "Approve content for publication?",
    "options": ["approve", "reject", "revise"],
    "voters": ["reviewer_1", "reviewer_2", "reviewer_3"]
}

decision = swarm.consensus(vote_request)
# Returns: {"decision": "approve", "confidence": 0.85}
```

### Hierarchical Pattern

Coordinator delegates to specialist agents:

```python
coordinator = SwarmAgent(name="coordinator", role="coordinator")
specialists = [
    SwarmAgent(name="text_specialist", role="worker"),
    SwarmAgent(name="image_specialist", role="worker"),
    SwarmAgent(name="video_specialist", role="worker")
]

swarm = Swarm(
    agents=[coordinator] + specialists,
    orchestrator=Orchestrator(strategy="hierarchical")
)
```

## Quality Assurance

### Confidence-Based Voting

Agents vote with confidence weights:

```python
from cbw_foundry.swarm.governance import ConfidenceVoting

voting = ConfidenceVoting()

votes = [
    {"agent": "reviewer_1", "vote": "approve", "confidence": 0.9},
    {"agent": "reviewer_2", "vote": "approve", "confidence": 0.7},
    {"agent": "reviewer_3", "vote": "reject", "confidence": 0.6}
]

result = voting.tally(votes)
# Returns: {"decision": "approve", "total_confidence": 0.8}
```

### Quality Gates

Enforce quality standards:

```python
from cbw_foundry.swarm.governance import QualityGate

gate = QualityGate(
    min_confidence=0.75,
    min_votes=3,
    consensus_threshold=0.8
)

if gate.passes(result):
    # Proceed with task
    pass
else:
    # Revision needed
    pass
```

## Observability

### Monitoring Swarm Activity

```python
from cbw_foundry.swarm.monitoring import SwarmMonitor

monitor = SwarmMonitor(swarm)

# Get metrics
metrics = monitor.get_metrics()
# Returns: {
#   "active_agents": 5,
#   "tasks_completed": 42,
#   "average_confidence": 0.82,
#   "error_rate": 0.02
# }

# Track agent performance
performance = monitor.get_agent_performance("content_generator")
# Returns: {
#   "tasks_completed": 15,
#   "success_rate": 0.93,
#   "average_time": 4.2
# }
```

### Distributed Tracing

```python
from cbw_foundry.observability.otel import trace_swarm_execution

@trace_swarm_execution
def execute_content_pipeline(swarm, task):
    """Traced swarm execution."""
    return swarm.execute(task)
```

## Best Practices

### 1. Agent Design

- Keep agents focused on specific capabilities
- Implement confidence metrics accurately
- Handle errors gracefully
- Support asynchronous operation

### 2. Communication

- Use structured message formats
- Implement idempotent message handlers
- Handle message ordering issues
- Set appropriate timeouts

### 3. Coordination

- Choose appropriate coordination strategy
- Implement quality gates
- Monitor agent performance
- Handle agent failures

### 4. State Management

- Use shared knowledge base for coordination
- Implement conflict resolution
- Handle concurrent updates
- Clean up stale state

### 5. Testing

- Test individual agents
- Test swarm coordination
- Test failure scenarios
- Test at scale

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [API Reference](API.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
