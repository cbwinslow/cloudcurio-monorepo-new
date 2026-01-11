from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import re
import subprocess
import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def _run(cmd: list[str]) -> bool:
    try:
        return subprocess.run(cmd, check=False, capture_output=True).returncode == 0
    except Exception:
        return False

def _parse_frontmatter(md_text: str) -> dict | None:
    m = FRONTMATTER_RE.search(md_text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return None

def _days_since(date_str: str) -> int | None:
    try:
        d = datetime.fromisoformat(date_str).date()
        return (datetime.now().date() - d).days
    except Exception:
        return None

def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-doctor")
    ap.add_argument("--kb-stale-days", type=int, default=90)
    args = ap.parse_args()

    issues: list[str] = []

    for cmd in (["python3", "--version"], ["git", "--version"]):
        if not _run(cmd):
            issues.append(f"Missing or broken: {' '.join(cmd)}")

    required = ["agents", "workflows", "kb", "bin", "shell", "docker/compose/observability", "src"]
    for r in required:
        if not Path(r).exists():
            issues.append(f"Missing path: {r}")

    if Path("kb").exists():
        for p in Path("kb").rglob("*.md"):
            if p.name.lower() == "readme.md":
                continue
            txt = p.read_text(encoding="utf-8")
            fm = _parse_frontmatter(txt)
            if fm is None:
                issues.append(f"KB missing front-matter: {p}")
                continue
            if "last_reviewed" in fm:
                ds = _days_since(str(fm["last_reviewed"]))
                if ds is not None and ds > args.kb_stale_days:
                    issues.append(f"KB stale (> {args.kb_stale_days}d): {p} ({ds}d)")

    if issues:
        print("CBW Doctor found issues:\n")
        for i in issues:
            print(f"- {i}")
        raise SystemExit(1)

    print("CBW Doctor: all checks passed.")
