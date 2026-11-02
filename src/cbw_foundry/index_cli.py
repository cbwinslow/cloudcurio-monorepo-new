from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .inventory import Inventory


def _scan(root: Path, glob_pat: str) -> list[str]:
    return sorted([str(p.relative_to(root)) for p in root.glob(glob_pat)])


def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-index")
    ap.add_argument("--outdir", default="registry")
    args = ap.parse_args()

    root = Path.cwd()
    outdir = root / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    # Legacy per-type YAML indexes (backward-compatible)
    indexes = {
        "agents": _scan(root, "agents/specs/**/*.agent.yaml"),
        "workflows": _scan(root, "workflows/**/*.workflow.yaml"),
        "kb": _scan(root, "kb/**/*.md"),
        "tools_py": _scan(root, "agents/tools/python/**/*.py"),
    }
    for name, items in indexes.items():
        (outdir / f"{name}.yaml").write_text(
            yaml.safe_dump({"items": items}, sort_keys=False), encoding="utf-8"
        )

    # Rich JSON index used by cbw-search
    inv = Inventory(root=root, index_path=outdir / "index.json")
    items = inv.scan()
    inv.save()

    print(f"Wrote indexes to {outdir}/ ({len(items)} items in index.json)")
