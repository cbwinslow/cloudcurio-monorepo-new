#!/usr/bin/env python3
"""CloudCurio Inventory Manager.

Scans the monorepo for all assets (agents, tools, skills, workflows, MCP servers,
scripts) and produces a rich, searchable JSON index at ``registry/index.json``.

Example::

    from cbw_foundry.inventory import Inventory
    inv = Inventory()
    inv.scan()
    results = inv.search("transcription")
    for item in results:
        print(item["name"], item["type"], item["path"])
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Item types
# ---------------------------------------------------------------------------
ITEM_TYPES = {
    "agent": "🤖",
    "tool": "🔧",
    "skill": "⚡",
    "workflow": "🔄",
    "mcp": "🔌",
    "script": "📜",
    "template": "📋",
}


def _slug(path: str) -> str:
    """Convert a file path to a slug name."""
    stem = Path(path).stem
    # strip suffixes like .agent, .skill, .workflow
    for suffix in (".agent", ".skill", ".workflow", ".tool"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem.replace("-", "_")


def _load_yaml_safe(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning empty dict on error."""
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_description_from_python(path: Path) -> str:
    """Extract module docstring from a Python file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'"""(.+?)"""', text, re.DOTALL)
        if match:
            first_line = match.group(1).strip().split("\n")[0].strip()
            return first_line[:160]
    except Exception:
        pass
    return ""


# Directives that look like comments but are not useful descriptions
_SH_SKIP_PATTERNS = re.compile(
    r"^(shellcheck|source|#!\s*/|set\s+[-+]|export\s+|#\s*[-=*]{3,}|#\s*$)",
    re.IGNORECASE,
)


def _extract_description_from_sh(path: Path) -> str:
    """Extract description comment from a shell script."""
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            if stripped.startswith("#!"):
                continue
            desc = stripped.lstrip("# ").strip()
            if not desc:
                continue
            # Skip shellcheck, linter directives, and other non-descriptive lines
            if _SH_SKIP_PATTERNS.search(desc):
                continue
            # Skip very short fragments or lines that look like code
            if len(desc) < 8 or "=" in desc[:20]:
                continue
            return desc[:160]
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Scanners per asset type
# ---------------------------------------------------------------------------

def _scan_agents(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("agents/specs/**/*.agent.yaml")):
        data = _load_yaml_safe(p)
        meta = data.get("metadata", {})
        items.append(
            {
                "type": "agent",
                "name": meta.get("name") or _slug(str(p)),
                "version": str(meta.get("version", "1.0.0")),
                "description": meta.get("description", ""),
                "tags": meta.get("tags") or [],
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["agent"],
            }
        )
    return items


def _scan_skills(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("skills/**/*.skill.yaml")):
        data = _load_yaml_safe(p)
        meta = data.get("metadata", {})
        spec = data.get("spec", {})
        items.append(
            {
                "type": "skill",
                "name": meta.get("name") or _slug(str(p)),
                "version": str(meta.get("version", "1.0.0")),
                "description": meta.get("description", ""),
                "tags": meta.get("tags") or [],
                "command": spec.get("command", ""),
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["skill"],
            }
        )
    return items


def _scan_workflows(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("workflows/**/*.workflow.yaml")):
        data = _load_yaml_safe(p)
        items.append(
            {
                "type": "workflow",
                "name": data.get("name") or _slug(str(p)),
                "version": str(data.get("version", "1.0.0")),
                "description": data.get("description", ""),
                "tags": data.get("tags") or [],
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["workflow"],
            }
        )
    return items


def _scan_tools(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("agents/tools/**/*.py")):
        if p.name.startswith("_"):
            continue
        desc = _extract_description_from_python(p)
        items.append(
            {
                "type": "tool",
                "name": _slug(str(p)),
                "version": "1.0.0",
                "description": desc,
                "tags": [],
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["tool"],
            }
        )
    return items


def _scan_mcp_servers(root: Path) -> list[dict[str, Any]]:
    items = []
    mcp_root = root / "mcp-servers"
    if not mcp_root.is_dir():
        return items
    for server_dir in sorted(mcp_root.iterdir()):
        if not server_dir.is_dir():
            continue
        # Look for a server.py or main entrypoint
        entrypoint = ""
        desc = ""
        for candidate in ["server.py", "main.py", "__main__.py"]:
            ep = server_dir / candidate
            if ep.exists():
                entrypoint = str(ep.relative_to(root))
                desc = _extract_description_from_python(ep)
                break
        # Check for package.json (Node-based MCP servers)
        pkg_json = server_dir / "package.json"
        if pkg_json.exists() and not entrypoint:
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                desc = pkg.get("description", "")
                entrypoint = str((server_dir / pkg.get("main", "index.js")).relative_to(root))
            except Exception:
                pass
        items.append(
            {
                "type": "mcp",
                "name": server_dir.name.replace("-", "_"),
                "version": "1.0.0",
                "description": desc,
                "tags": ["mcp", "server"],
                "path": entrypoint or str(server_dir.relative_to(root)),
                "icon": ITEM_TYPES["mcp"],
            }
        )
    return items


def _scan_scripts(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("scripts/**/*.sh")):
        desc = _extract_description_from_sh(p)
        items.append(
            {
                "type": "script",
                "name": _slug(str(p)),
                "version": "1.0.0",
                "description": desc,
                "tags": ["shell", "script"],
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["script"],
            }
        )
    return items


def _scan_templates(root: Path) -> list[dict[str, Any]]:
    items = []
    for p in sorted(root.glob("templates/**/*.yaml")):
        data = _load_yaml_safe(p)
        meta = data.get("metadata", {})
        items.append(
            {
                "type": "template",
                "name": meta.get("name") or _slug(str(p)),
                "version": str(meta.get("version", "1.0.0")),
                "description": meta.get("description", ""),
                "tags": meta.get("tags") or ["template"],
                "path": str(p.relative_to(root)),
                "icon": ITEM_TYPES["template"],
            }
        )
    return items


# ---------------------------------------------------------------------------
# Main Inventory class
# ---------------------------------------------------------------------------

class Inventory:
    """Manage the CloudCurio asset inventory.

    Args:
        root: Repository root path (defaults to cwd).
        index_path: Where to write/read the JSON index.
    """

    def __init__(
        self,
        root: Path | None = None,
        index_path: Path | None = None,
    ) -> None:
        self.root = (root or Path.cwd()).resolve()
        self.index_path = index_path or (self.root / "registry" / "index.json")
        self._items: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan(self) -> list[dict[str, Any]]:
        """Scan the repo and populate internal items list."""
        self._items = []
        scanners = [
            _scan_agents,
            _scan_skills,
            _scan_workflows,
            _scan_tools,
            _scan_mcp_servers,
            _scan_scripts,
            _scan_templates,
        ]
        for scanner in scanners:
            self._items.extend(scanner(self.root))
        return self._items

    def save(self) -> None:
        """Persist the index to disk as JSON."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": "1.0.0",
            "total": len(self._items),
            "items": self._items,
        }
        self.index_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self) -> list[dict[str, Any]]:
        """Load items from the JSON index on disk."""
        if not self.index_path.exists():
            return []
        try:
            payload = json.loads(self.index_path.read_text(encoding="utf-8"))
            self._items = payload.get("items", [])
        except Exception:
            self._items = []
        return self._items

    @property
    def items(self) -> list[dict[str, Any]]:
        """Return loaded/scanned items, loading from disk if needed."""
        if not self._items:
            self.load()
        return self._items

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def list_all(self, item_type: str | None = None) -> list[dict[str, Any]]:
        """Return all items, optionally filtered by type."""
        if item_type:
            return [i for i in self.items if i["type"] == item_type]
        return list(self.items)

    def search(self, query: str, item_type: str | None = None) -> list[dict[str, Any]]:
        """Fuzzy-ish search across name, description, tags, and path.

        Args:
            query: Search term (case-insensitive substring match). Empty string returns [].
            item_type: Optional asset type filter.

        Returns:
            Matching items sorted by relevance (name match first).
        """
        if not query or not query.strip():
            return []
        q = query.lower()
        pool = self.list_all(item_type)

        def _score(item: dict[str, Any]) -> int:
            score = 0
            name = item.get("name", "").lower()
            desc = item.get("description", "").lower()
            tags = " ".join(item.get("tags") or []).lower()
            path = item.get("path", "").lower()
            if q in name:
                score += 10
                if name.startswith(q):
                    score += 5
            if q in desc:
                score += 4
            if q in tags:
                score += 3
            if q in path:
                score += 1
            return score

        scored = [(item, _score(item)) for item in pool]
        matched = [(item, s) for item, s in scored if s > 0]
        matched.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in matched]

    def get(self, name: str) -> dict[str, Any] | None:
        """Get a single item by exact name."""
        for item in self.items:
            if item["name"] == name:
                return item
        return None

    def types(self) -> list[str]:
        """Return sorted list of all unique item types in the index."""
        return sorted({i["type"] for i in self.items})

    def summary(self) -> dict[str, int]:
        """Return count of items per type."""
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item["type"]] = counts.get(item["type"], 0) + 1
        return counts
