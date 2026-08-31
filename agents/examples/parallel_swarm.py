#!/usr/bin/env python3
"""Parallel Swarm Example.

Demonstrates parallel agent coordination where agents work simultaneously.
"""

from cbw_foundry.swarm import CoordinationMode, Swarm, SwarmAgent, SwarmConfig


def create_parallel_swarm() -> Swarm:
    """Create a parallel swarm for concurrent research tasks.

    Returns:
        Configured swarm instance
    """
    # Define multiple researcher agents for parallel work
    agents = [
        SwarmAgent(
            name="tech_researcher",
            role="worker",
            capabilities=["technology_research"],
            confidence=0.9,
        ),
        SwarmAgent(
            name="market_researcher",
            role="worker",
            capabilities=["market_research"],
            confidence=0.85,
        ),
        SwarmAgent(
            name="competitor_researcher",
            role="worker",
            capabilities=["competitor_analysis"],
            confidence=0.88,
        ),
        SwarmAgent(
            name="trend_researcher", role="worker", capabilities=["trend_analysis"], confidence=0.87
        ),
    ]

    # Configure swarm for parallel execution
    config = SwarmConfig(
        coordination_mode=CoordinationMode.PARALLEL,
        max_iterations=1,
        quality_threshold=0.8,
        enable_voting=False,
        timeout=300,
    )

    swarm = Swarm(name="parallel_research_team", agents=agents, config=config)

    return swarm


def run_parallel_example():
    """Run parallel swarm example."""
    print("=== Parallel Swarm Example ===\n")

    # Create swarm
    swarm = create_parallel_swarm()

    # Define task (same task for all agents, but different aspects)
    task = {
        "task": "Research AI agent market landscape",
        "aspects": [
            "technical capabilities",
            "market size and growth",
            "key competitors",
            "emerging trends",
        ],
    }

    print(f"Task: {task['task']}")
    print(f"Agents working in parallel: {[a.name for a in swarm.agents]}\n")

    # Execute swarm
    result = swarm.execute(task)

    # Display results
    print(f"Status: {'✓ Success' if result.success else '✗ Failed'}")
    print(f"Iterations: {result.iterations}")
    print(f"Execution Time: {result.execution_time:.2f}s\n")

    print("Parallel Agent Outputs:")
    for agent_name, output in result.agent_outputs.items():
        print(f"\n{agent_name}:")
        print(f"  {output}")

    print("\nAggregated Results:")
    print(f"  {result.output}")


if __name__ == "__main__":
    run_parallel_example()
