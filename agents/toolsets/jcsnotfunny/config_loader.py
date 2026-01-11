"""Minimal ConfigLoader for toolsets package.

This is a small, well-documented stub used by tests and by the package
initialization. It can be expanded later with actual JSON/TOML/YAML support.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from pathlib import Path
import json


class ConfigLoader:
    """Simple configuration loader.

    Usage:
        cfg = ConfigLoader(path="toolsets_config.json").load()
    """

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else None

    def load(self) -> Dict[str, Any]:
        if not self.path or not self.path.exists():
            return {}
        try:
            with self.path.open('r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return {}
