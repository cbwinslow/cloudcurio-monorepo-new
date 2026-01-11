from __future__ import annotations
import argparse
from pathlib import Path
import yaml

def _scan(glob_pat: str) -> list[str]:
    return sorted([str(p) for p in Path(".").glob(glob_pat)])

def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-index")
    ap.add_argument("--outdir", default="registry")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    indexes = {
        "agents": _scan("agents/specs/**/*.agent.yaml"),
        "workflows": _scan("workflows/**/*.workflow.yaml"),
        "kb": _scan("kb/**/*.md"),
        "tools_py": _scan("agents/tools/python/**/*.py"),
    }

    for name, items in indexes.items():
        (outdir / f"{name}.yaml").write_text(yaml.safe_dump({"items": items}, sort_keys=False), encoding="utf-8")

    print(f"Wrote indexes to {outdir}/")
