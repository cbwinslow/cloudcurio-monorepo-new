#!/usr/bin/env python3
"""Democratic Swarm Example.

Demonstrates democratic agent coordination with confidence-weighted voting.
"""

from cbw_foundry.swarm import CoordinationMode, Swarm, SwarmAgent, SwarmConfig


def create_democratic_swarm() -> Swarm:
    """Create a democratic swarm for decision-making with voting.

    Returns:
        Configured swarm instance
    """
    # Define agents with different confidence levels
    agents = [
        SwarmAgent(
            name="senior_architect",
            role="specialist",
            capabilities=["architecture_design", "decision_making"],
            confidence=0.95,
        ),
        SwarmAgent(
            name="mid_level_dev_1",
            role="worker",
            capabilities=["coding", "design"],
            confidence=0.80,
        ),
        SwarmAgent(
            name="mid_level_dev_2",
            role="worker",
            capabilities=["coding", "design"],
            confidence=0.82,
        ),
        SwarmAgent(name="junior_dev", role="worker", capabilities=["coding"], confidence=0.65),
    ]

    # Configure swarm for democratic voting
    config = SwarmConfig(
        coordination_mode=CoordinationMode.DEMOCRATIC,
        max_iterations=1,
        quality_threshold=0.75,
        enable_voting=True,
        timeout=300,
    )

    swarm = Swarm(name="democratic_design_team", agents=agents, config=config)

    return swarm


def run_democratic_example():
    """Run democratic swarm example."""
    print("=== Democratic Swarm Example ===\n")

    # Create swarm
    swarm = create_democratic_swarm()

    # Define task requiring group decision
    task = {
        "task": "Choose the best architecture pattern for a microservices system",
        "options": [
            "Event-driven architecture",
            "API Gateway pattern",
            "Service Mesh",
            "Choreography-based saga",
        ],
        "criteria": ["scalability", "maintainability", "complexity", "team expertise"],
    }

    print(f"Task: {task['task']}")
    print("Voting agents:")
    for agent in swarm.agents:
        print(f"  - {agent.name} (confidence: {agent.confidence})")
    print()

    # Execute swarm
    result = swarm.execute(task)

    # Display results
    print(f"Status: {'✓ Success' if result.success else '✗ Failed'}")
    print(f"Iterations: {result.iterations}")
    print(f"Execution Time: {result.execution_time:.2f}s\n")

    print("Agent Proposals:")
    for agent_name, output in result.agent_outputs.items():
        agent = swarm.get_agent(agent_name)
        print(f"\n{agent_name} (confidence: {agent.confidence}):")
        print(f"  {output}")

    print("\nDemocratic Decision (highest confidence vote):")
    print(f"  {result.output}")


if __name__ == "__main__":
    run_democratic_example()
