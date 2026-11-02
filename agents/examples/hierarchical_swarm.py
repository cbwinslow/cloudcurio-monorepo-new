#!/usr/bin/env python3
"""Hierarchical Swarm Example.

Demonstrates hierarchical agent coordination with coordinator and workers.
"""

from cbw_foundry.swarm import CoordinationMode, Swarm, SwarmAgent, SwarmConfig


def create_hierarchical_swarm() -> Swarm:
    """Create a hierarchical swarm with coordinator and workers.

    Returns:
        Configured swarm instance
    """
    # Define agents with hierarchical roles
    agents = [
        SwarmAgent(
            name="project_manager",
            role="coordinator",
            capabilities=["task_delegation", "aggregation"],
            confidence=0.90,
        ),
        SwarmAgent(
            name="backend_dev",
            role="worker",
            capabilities=["backend", "api_development"],
            confidence=0.85,
        ),
        SwarmAgent(
            name="frontend_dev",
            role="worker",
            capabilities=["frontend", "ui_development"],
            confidence=0.83,
        ),
        SwarmAgent(
            name="database_specialist",
            role="worker",
            capabilities=["database", "data_modeling"],
            confidence=0.88,
        ),
        SwarmAgent(
            name="devops_engineer",
            role="worker",
            capabilities=["deployment", "infrastructure"],
            confidence=0.86,
        ),
    ]

    # Configure swarm for hierarchical coordination
    config = SwarmConfig(
        coordination_mode=CoordinationMode.HIERARCHICAL,
        max_iterations=1,
        quality_threshold=0.80,
        enable_voting=False,
        timeout=600,
    )

    swarm = Swarm(name="hierarchical_dev_team", agents=agents, config=config)

    return swarm


def run_hierarchical_example():
    """Run hierarchical swarm example."""
    print("=== Hierarchical Swarm Example ===\n")

    # Create swarm
    swarm = create_hierarchical_swarm()

    # Define complex task requiring coordination
    task = {
        "task": "Build a new user authentication system",
        "requirements": [
            "RESTful API for authentication",
            "React-based login interface",
            "PostgreSQL user database",
            "Docker deployment setup",
        ],
        "deadline": "2 weeks",
    }

    print(f"Task: {task['task']}")
    print("\nTeam Structure:")
    coordinator = next((a for a in swarm.agents if a.role == "coordinator"), None)
    workers = [a for a in swarm.agents if a.role == "worker"]

    print(f"  Coordinator: {coordinator.name}")
    print("  Workers:")
    for worker in workers:
        print(f"    - {worker.name} ({', '.join(worker.capabilities)})")
    print()

    # Execute swarm
    result = swarm.execute(task)

    # Display results
    print(f"Status: {'✓ Success' if result.success else '✗ Failed'}")
    print(f"Iterations: {result.iterations}")
    print(f"Execution Time: {result.execution_time:.2f}s\n")

    print("Worker Outputs:")
    for agent_name, output in result.agent_outputs.items():
        if agent_name != coordinator.name:
            print(f"\n{agent_name}:")
            print(f"  {output}")

    print("\nCoordinator's Aggregated Result:")
    print(f"  {result.output}")


if __name__ == "__main__":
    run_hierarchical_example()
