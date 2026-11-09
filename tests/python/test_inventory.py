"""Tests for cbw_foundry.inventory module."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure src/ is on the path regardless of how pytest is invoked
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cbw_foundry.inventory import ITEM_TYPES, Inventory, _slug

REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


class TestSlug:
    def test_agent_suffix_stripped(self) -> None:
        assert _slug("agents/specs/researcher.agent.yaml") == "researcher"

    def test_skill_suffix_stripped(self) -> None:
        assert _slug("skills/research.skill.yaml") == "research"

    def test_workflow_suffix_stripped(self) -> None:
        assert _slug("workflows/library/foo_bar.workflow.yaml") == "foo_bar"

    def test_plain_stem(self) -> None:
        assert _slug("agents/tools/python/echo_tool.py") == "echo_tool"

    def test_hyphens_to_underscores(self) -> None:
        assert _slug("mcp-servers/content-optimizer/server.py") == "server"


class TestItemTypes:
    def test_all_types_have_icons(self) -> None:
        for t in ("agent", "tool", "skill", "workflow", "mcp", "script", "template"):
            assert t in ITEM_TYPES
            assert ITEM_TYPES[t]  # non-empty string


# ---------------------------------------------------------------------------
# Integration tests against the real repo
# ---------------------------------------------------------------------------


class TestInventoryScan:
    """Test scanning against the actual repo layout."""

    def test_scan_returns_list(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        items = inv.scan()
        assert isinstance(items, list)

    def test_scan_finds_agents(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        inv.scan()
        agents = inv.list_all("agent")
        assert len(agents) > 0, "Expected at least one agent in specs/"

    def test_scan_finds_skills(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        inv.scan()
        skills = inv.list_all("skill")
        assert len(skills) > 0, "Expected at least one skill in skills/"

    def test_scan_finds_workflows(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        inv.scan()
        workflows = inv.list_all("workflow")
        assert len(workflows) > 0

    def test_scan_finds_mcp_servers(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        inv.scan()
        mcp = inv.list_all("mcp")
        assert len(mcp) > 0

    def test_all_items_have_required_fields(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        items = inv.scan()
        required = {"type", "name", "path", "icon"}
        for item in items:
            missing = required - set(item.keys())
            assert not missing, f"Item {item.get('name')} missing fields: {missing}"

    def test_all_items_have_valid_type(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        items = inv.scan()
        valid_types = set(ITEM_TYPES.keys())
        for item in items:
            assert item["type"] in valid_types, f"Unknown type: {item['type']}"

    def test_item_paths_are_relative(self) -> None:
        inv = Inventory(root=REPO_ROOT)
        items = inv.scan()
        for item in items:
            path = item["path"]
            assert not Path(path).is_absolute(), f"Path should be relative: {path}"


class TestInventorySearch:
    """Test search functionality."""

    def setup_method(self) -> None:
        self.inv = Inventory(root=REPO_ROOT)
        self.inv.scan()

    def test_search_finds_researcher(self) -> None:
        results = self.inv.search("researcher")
        names = [r["name"] for r in results]
        assert "researcher" in names

    def test_search_is_case_insensitive(self) -> None:
        results_lower = self.inv.search("research")
        results_upper = self.inv.search("RESEARCH")
        assert len(results_lower) == len(results_upper)

    def test_search_with_type_filter(self) -> None:
        results = self.inv.search("research", item_type="agent")
        for r in results:
            assert r["type"] == "agent"

    def test_search_empty_query_returns_empty(self) -> None:
        # empty string matches everything (score > 0 required)
        results = self.inv.search("")
        assert results == []  # score=0 filtered out

    def test_search_whitespace_only_returns_empty(self) -> None:
        results = self.inv.search("   ")
        assert results == []

    def test_search_unknown_term(self) -> None:
        results = self.inv.search("zzz_no_match_xyz")
        assert results == []

    def test_get_existing_item(self) -> None:
        item = self.inv.get("researcher")
        assert item is not None
        assert item["name"] == "researcher"
        assert item["type"] == "agent"

    def test_get_nonexistent_item(self) -> None:
        item = self.inv.get("nonexistent_zzz")
        assert item is None

    def test_types_returns_list(self) -> None:
        types = self.inv.types()
        assert isinstance(types, list)
        assert len(types) > 0

    def test_summary_returns_dict(self) -> None:
        summary = self.inv.summary()
        assert isinstance(summary, dict)
        assert "agent" in summary
        assert summary["agent"] > 0


class TestInventoryPersistence:
    """Test save/load round-trip."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        index_path = tmp_path / "index.json"
        inv = Inventory(root=REPO_ROOT, index_path=index_path)
        original = inv.scan()
        inv.save()

        assert index_path.exists()
        data = json.loads(index_path.read_text())
        assert "items" in data
        assert data["total"] == len(original)

        inv2 = Inventory(root=REPO_ROOT, index_path=index_path)
        loaded = inv2.load()
        assert len(loaded) == len(original)

    def test_load_missing_file_returns_empty(self, tmp_path: Path) -> None:
        inv = Inventory(root=REPO_ROOT, index_path=tmp_path / "missing.json")
        result = inv.load()
        assert result == []

    def test_index_json_schema(self, tmp_path: Path) -> None:
        index_path = tmp_path / "index.json"
        inv = Inventory(root=REPO_ROOT, index_path=index_path)
        inv.scan()
        inv.save()
        data = json.loads(index_path.read_text())
        assert data["version"] == "1.0.0"
        assert isinstance(data["total"], int)
        assert isinstance(data["items"], list)
