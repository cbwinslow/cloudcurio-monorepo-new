#!/bin/bash

# Create swarm/communication/__init__.py
cat > src/cbw_foundry/swarm/communication/__init__.py << 'EOF1'
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
EOF1

# Create swarm/knowledge/__init__.py
cat > src/cbw_foundry/swarm/knowledge/__init__.py << 'EOF2'
"""Swarm Knowledge Management - Shared state and knowledge base.

Provides knowledge storage, retrieval, and synchronization for agent swarms.

Key Components:
- KnowledgeBase: Central knowledge store
- KnowledgeEntry: Structured knowledge item
- ConflictResolution: Handle concurrent updates

Usage:
    from cbw_foundry.swarm.knowledge import KnowledgeBase
    
    kb = KnowledgeBase()
    kb.store("requirements", {"tone": "professional"}, "coordinator")
    data = kb.retrieve("requirements")
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictStrategy(str, Enum):
    """Strategies for resolving knowledge conflicts."""
    LAST_WRITE_WINS = "last_write_wins"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MERGE = "merge"
    MANUAL = "manual"


@dataclass
class KnowledgeEntry:
    """Structured knowledge entry."""
    
    key: str
    value: Any
    agent_id: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1


class KnowledgeBase:
    """Shared knowledge base for agent swarm."""
    
    def __init__(self, conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS):
        """Initialize knowledge base.
        
        Args:
            conflict_strategy: Strategy for resolving conflicts
        """
        self._storage: Dict[str, KnowledgeEntry] = {}
        self._history: Dict[str, List[KnowledgeEntry]] = {}
        self._conflict_strategy = conflict_strategy
        logger.info(f"Initialized KnowledgeBase with {conflict_strategy} strategy")
    
    def store(
        self,
        key: str,
        value: Any,
        agent_id: str,
        confidence: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store knowledge in the base.
        
        Args:
            key: Knowledge identifier
            value: Knowledge value
            agent_id: Agent storing the knowledge
            confidence: Confidence in the knowledge (0-1)
            metadata: Additional metadata
        """
        existing = self._storage.get(key)
        version = existing.version + 1 if existing else 1
        
        entry = KnowledgeEntry(
            key=key,
            value=value,
            agent_id=agent_id,
            confidence=confidence,
            metadata=metadata or {},
            version=version
        )
        
        # Store in history
        if key not in self._history:
            self._history[key] = []
        if existing:
            self._history[key].append(existing)
        
        # Resolve conflicts if needed
        if existing:
            entry = self._resolve_conflict(existing, entry)
        
        self._storage[key] = entry
        logger.debug(f"Stored knowledge '{key}' from agent '{agent_id}' (v{version})")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve knowledge from base.
        
        Args:
            key: Knowledge identifier
            
        Returns:
            Knowledge value or None if not found
        """
        entry = self._storage.get(key)
        return entry.value if entry else None
    
    def get_entry(self, key: str) -> Optional[KnowledgeEntry]:
        """Get full knowledge entry.
        
        Args:
            key: Knowledge identifier
            
        Returns:
            KnowledgeEntry or None
        """
        return self._storage.get(key)
    
    def update(
        self,
        key: str,
        value: Any,
        agent_id: str,
        confidence: float = 1.0
    ) -> bool:
        """Update existing knowledge.
        
        Args:
            key: Knowledge identifier
            value: New value
            agent_id: Agent updating the knowledge
            confidence: Confidence in update
            
        Returns:
            True if updated, False if key doesn't exist
        """
        if key not in self._storage:
            return False
        
        self.store(key, value, agent_id, confidence)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete knowledge.
        
        Args:
            key: Knowledge identifier
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._storage:
            del self._storage[key]
            logger.debug(f"Deleted knowledge '{key}'")
            return True
        return False
    
    def keys(self) -> List[str]:
        """Get all knowledge keys."""
        return list(self._storage.keys())
    
    def get_history(self, key: str) -> List[KnowledgeEntry]:
        """Get history of knowledge updates.
        
        Args:
            key: Knowledge identifier
            
        Returns:
            List of historical entries
        """
        return self._history.get(key, [])
    
    def _resolve_conflict(
        self,
        existing: KnowledgeEntry,
        new: KnowledgeEntry
    ) -> KnowledgeEntry:
        """Resolve conflict between entries.
        
        Args:
            existing: Existing entry
            new: New entry
            
        Returns:
            Resolved entry
        """
        if self._conflict_strategy == ConflictStrategy.LAST_WRITE_WINS:
            return new
        elif self._conflict_strategy == ConflictStrategy.HIGHEST_CONFIDENCE:
            return new if new.confidence > existing.confidence else existing
        elif self._conflict_strategy == ConflictStrategy.MERGE:
            # Simple merge: keep newer value but merge metadata
            merged = new
            merged.metadata = {**existing.metadata, **new.metadata}
            return merged
        else:
            return new


__all__ = [
    "KnowledgeBase",
    "KnowledgeEntry",
    "ConflictStrategy",
]
EOF2

echo "Swarm modules created successfully"
