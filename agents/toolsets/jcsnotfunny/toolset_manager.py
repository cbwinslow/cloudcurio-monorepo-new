"""Minimal ToolsetManager stub for the toolsets package.

Provides a lightweight interface expected by package consumers and tests.
This is intentionally small and can be extended with lifecycle hooks and
resource management later.
"""

from __future__ import annotations

from typing import Any


class ToolsetManager:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.tools: dict[str, Any] = {}

    def register(self, name: str, tool: Any) -> None:
        self.tools[name] = tool

    def get_config(self) -> dict[str, Any]:
        return self.config
