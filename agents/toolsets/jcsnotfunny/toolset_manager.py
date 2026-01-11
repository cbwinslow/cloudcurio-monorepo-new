"""Minimal ToolsetManager stub for the toolsets package.

Provides a lightweight interface expected by package consumers and tests.
This is intentionally small and can be extended with lifecycle hooks and
resource management later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class ToolsetManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, Any] = {}

    def register(self, name: str, tool: Any) -> None:
        self.tools[name] = tool

    def get_config(self) -> Dict[str, Any]:
        return self.config
