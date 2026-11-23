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

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 1


class KnowledgeBase:
    """Shared knowledge base for agent swarm."""

    def __init__(self, conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS):
        """Initialize knowledge base.

        Args:
            conflict_strategy: Strategy for resolving conflicts
        """
        self._storage: dict[str, KnowledgeEntry] = {}
        self._history: dict[str, list[KnowledgeEntry]] = {}
        self._conflict_strategy = conflict_strategy
        logger.info(f"Initialized KnowledgeBase with {conflict_strategy} strategy")

    def store(
        self,
        key: str,
        value: Any,
        agent_id: str,
        confidence: float = 1.0,
        metadata: dict | None = None,
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
            version=version,
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

    def retrieve(self, key: str) -> Any | None:
        """Retrieve knowledge from base.

        Args:
            key: Knowledge identifier

        Returns:
            Knowledge value or None if not found
        """
        entry = self._storage.get(key)
        return entry.value if entry else None

    def get_entry(self, key: str) -> KnowledgeEntry | None:
        """Get full knowledge entry.

        Args:
            key: Knowledge identifier

        Returns:
            KnowledgeEntry or None
        """
        return self._storage.get(key)

    def update(self, key: str, value: Any, agent_id: str, confidence: float = 1.0) -> bool:
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

    def keys(self) -> list[str]:
        """Get all knowledge keys."""
        return list(self._storage.keys())

    def get_history(self, key: str) -> list[KnowledgeEntry]:
        """Get history of knowledge updates.

        Args:
            key: Knowledge identifier

        Returns:
            List of historical entries
        """
        return self._history.get(key, [])

    def _resolve_conflict(self, existing: KnowledgeEntry, new: KnowledgeEntry) -> KnowledgeEntry:
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
    "ConflictStrategy",
    "KnowledgeBase",
    "KnowledgeEntry",
]
