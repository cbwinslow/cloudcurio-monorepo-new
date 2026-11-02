"""Multi-Agent Coordinator - Agent communication and state management.

Coordinates multiple agents by managing their communication, state, and task distribution.
Uses the MessageBus system for inter-agent messaging and maintains agent registry.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from cbw_foundry.swarm.communication import Message, MessageBus, MessageType

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Agent state tracking."""

    agent_id: str
    status: str  # idle, busy, error, offline
    current_task: str | None = None
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class MultiAgentCoordinator:
    """Coordinates multiple agents for distributed task execution."""

    def __init__(self):
        """Initialize multi-agent coordinator."""
        self.message_bus = MessageBus()
        self.agents: dict[str, AgentState] = {}
        self.task_queue: list[dict[str, Any]] = []
        logger.info("Initialized MultiAgentCoordinator")

    def register_agent(self, agent_id: str, metadata: dict[str, Any] | None = None) -> None:
        """Register an agent with the coordinator.

        Args:
            agent_id: Unique agent identifier
            metadata: Optional agent metadata (capabilities, etc.)
        """
        self.agents[agent_id] = AgentState(
            agent_id=agent_id, status="idle", metadata=metadata or {}
        )
        self.message_bus.subscribe(agent_id, MessageType.TASK_REQUEST.value)
        self.message_bus.subscribe(agent_id, MessageType.HEARTBEAT.value)
        logger.info(f"Registered agent '{agent_id}'")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent.

        Args:
            agent_id: Agent identifier to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent '{agent_id}'")

    def assign_task(self, agent_id: str, task: dict[str, Any]) -> None:
        """Assign task to specific agent.

        Args:
            agent_id: Target agent identifier
            task: Task definition
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not registered")

        message = Message(
            type=MessageType.TASK_REQUEST, sender="coordinator", recipient=agent_id, content=task
        )
        self.message_bus.publish(message)

        self.agents[agent_id].status = "busy"
        self.agents[agent_id].current_task = task.get("task_id")
        logger.info(f"Assigned task to agent '{agent_id}'")

    def broadcast_message(self, message_type: MessageType, content: dict[str, Any]) -> None:
        """Broadcast message to all agents.

        Args:
            message_type: Type of message
            content: Message content
        """
        message = Message(type=message_type, sender="coordinator", content=content)
        self.message_bus.publish(message)
        logger.info(f"Broadcast message of type '{message_type}'")

    def get_agent_status(self, agent_id: str) -> AgentState | None:
        """Get current agent status.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent state or None if not found
        """
        return self.agents.get(agent_id)

    def get_all_agents(self) -> dict[str, AgentState]:
        """Get all registered agents and their states.

        Returns:
            Dictionary of agent IDs to states
        """
        return self.agents.copy()

    def update_agent_status(self, agent_id: str, status: str, task_id: str | None = None) -> None:
        """Update agent status.

        Args:
            agent_id: Agent identifier
            status: New status
            task_id: Optional task ID
        """
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].current_task = task_id
            self.agents[agent_id].last_heartbeat = datetime.utcnow().isoformat()
            logger.debug(f"Updated agent '{agent_id}' status to '{status}'")

    def handle_task_complete(self, agent_id: str, result: dict[str, Any]) -> None:
        """Handle task completion from agent.

        Args:
            agent_id: Agent that completed task
            result: Task result
        """
        if agent_id in self.agents:
            self.agents[agent_id].status = "idle"
            self.agents[agent_id].current_task = None
            logger.info(f"Agent '{agent_id}' completed task")

    def process_messages(self) -> None:
        """Process pending messages for coordinator."""
        messages = self.message_bus.receive("coordinator")
        for msg in messages:
            if msg.type == MessageType.TASK_COMPLETE:
                self.handle_task_complete(msg.sender, msg.content)
            elif msg.type == MessageType.STATUS_UPDATE:
                self.update_agent_status(
                    msg.sender, msg.content.get("status", "idle"), msg.content.get("task_id")
                )
            elif msg.type == MessageType.HEARTBEAT:
                if msg.sender in self.agents:
                    self.agents[msg.sender].last_heartbeat = datetime.utcnow().isoformat()


__all__ = ["AgentState", "MultiAgentCoordinator"]
