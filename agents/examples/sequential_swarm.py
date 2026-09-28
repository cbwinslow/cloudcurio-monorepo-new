#!/usr/bin/env python3
"""Sequential Swarm Example.

Demonstrates sequential agent coordination where agents process tasks in order.
"""

from cbw_foundry.swarm import CoordinationMode, Swarm, SwarmAgent, SwarmConfig


def create_sequential_swarm() -> Swarm:
    """Create a sequential swarm for content creation pipeline.

    Returns:
        Configured swarm instance
    """
    # Define agents with specific roles
    agents = [
        SwarmAgent(
            name="researcher",
            role="worker",
            capabilities=["web_search", "content_extraction"],
            confidence=0.9,
        ),
        SwarmAgent(
            name="writer",
            role="worker",
            capabilities=["content_creation", "writing"],
            confidence=0.85,
        ),
        SwarmAgent(
            name="editor",
            role="reviewer",
            capabilities=["editing", "quality_check"],
            confidence=0.9,
        ),
    ]

    # Configure swarm for sequential execution
    config = SwarmConfig(
        coordination_mode=CoordinationMode.SEQUENTIAL,
        max_iterations=3,
        quality_threshold=0.8,
        enable_voting=False,  # No voting in sequential mode
        timeout=600,
    )

    swarm = Swarm(name="content_creation_pipeline", agents=agents, config=config)

    return swarm


def run_sequential_example():
    """Run sequential swarm example."""
    print("=== Sequential Swarm Example ===\n")

    # Create swarm
    swarm = create_sequential_swarm()

    # Define task
    task = {
        "task": "Create a blog post about AI agent frameworks",
        "topic": "AI agent frameworks",
        "length": "1000 words",
        "tone": "technical but accessible",
    }

    print(f"Task: {task['task']}")
    print(f"Agents: {[a.name for a in swarm.agents]}\n")

    # Execute swarm
    result = swarm.execute(task)

    # Display results
    print(f"Status: {'✓ Success' if result.success else '✗ Failed'}")
    print(f"Iterations: {result.iterations}")
    print(f"Execution Time: {result.execution_time:.2f}s\n")

    print("Agent Outputs:")
    for agent_name, output in result.agent_outputs.items():
        print(f"\n{agent_name}:")
        print(f"  {output}")

    print("\nFinal Output:")
    print(f"  {result.output}")


if __name__ == "__main__":
    run_sequential_example()
