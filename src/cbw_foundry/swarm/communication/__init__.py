"""Swarm Communication System - Inter-agent messaging and coordination.

Provides message bus, protocols, and event system for agent communication.

Key Components:
- MessageBus: Central message routing
- Message: Structured message format
- MessageType: Message classification
- EventEmitter: Event-driven coordination

Usage:
    from cbw_foundry.swarm.communication import MessageBus, Message, MessageType
    
    bus = MessageBus()
    bus.subscribe("agent_1", "task_complete")
    
    message = Message(
        type=MessageType.TASK_COMPLETE,
        sender="agent_2",
        recipient="agent_1",
        content={"result": "success"}
    )
    bus.publish(message)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Message types for agent communication."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_COMPLETE = "task_complete"
    STATUS_UPDATE = "status_update"
    KNOWLEDGE_SHARE = "knowledge_share"
    VOTE_REQUEST = "vote_request"
    VOTE_RESPONSE = "vote_response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class Message:
    """Structured message for inter-agent communication."""
    
    type: MessageType
    sender: str
    content: Dict[str, Any]
    recipient: Optional[str] = None  # None for broadcast
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MessageBus:
    """Central message bus for agent communication."""
    
    def __init__(self):
        """Initialize message bus."""
        self._subscriptions: Dict[str, List[str]] = defaultdict(list)
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_queue: Dict[str, List[Message]] = defaultdict(list)
        logger.info("Initialized MessageBus")
    
    def subscribe(self, agent_id: str, topic: str) -> None:
        """Subscribe agent to topic.
        
        Args:
            agent_id: Agent identifier
            topic: Topic to subscribe to
        """
        if topic not in self._subscriptions[agent_id]:
            self._subscriptions[agent_id].append(topic)
            logger.debug(f"Agent '{agent_id}' subscribed to '{topic}'")
    
    def unsubscribe(self, agent_id: str, topic: str) -> None:
        """Unsubscribe agent from topic.
        
        Args:
            agent_id: Agent identifier
            topic: Topic to unsubscribe from
        """
        if topic in self._subscriptions[agent_id]:
            self._subscriptions[agent_id].remove(topic)
            logger.debug(f"Agent '{agent_id}' unsubscribed from '{topic}'")
    
    def publish(self, message: Message) -> None:
        """Publish message to bus.
        
        Args:
            message: Message to publish
        """
        if message.recipient:
            # Direct message
            self._message_queue[message.recipient].append(message)
            logger.debug(f"Message from '{message.sender}' queued for '{message.recipient}'")
        else:
            # Broadcast to subscribers
            topic = message.type.value
            for agent_id, topics in self._subscriptions.items():
                if topic in topics and agent_id != message.sender:
                    self._message_queue[agent_id].append(message)
            logger.debug(f"Broadcast message from '{message.sender}' on topic '{topic}'")
    
    def receive(self, agent_id: str, limit: Optional[int] = None) -> List[Message]:
        """Receive messages for agent.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages for the agent
        """
        messages = self._message_queue.get(agent_id, [])
        if limit:
            result = messages[:limit]
            self._message_queue[agent_id] = messages[limit:]
        else:
            result = messages
            self._message_queue[agent_id] = []
        
        logger.debug(f"Agent '{agent_id}' received {len(result)} messages")
        return result
    
    def peek(self, agent_id: str) -> List[Message]:
        """Peek at messages without removing them.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            List of pending messages
        """
        return self._message_queue.get(agent_id, []).copy()
    
    def clear(self, agent_id: str) -> None:
        """Clear message queue for agent.
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id in self._message_queue:
            count = len(self._message_queue[agent_id])
            self._message_queue[agent_id] = []
            logger.debug(f"Cleared {count} messages for agent '{agent_id}'")


__all__ = [
    "MessageBus",
    "Message",
    "MessageType",
]
