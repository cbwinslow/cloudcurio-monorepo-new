from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def ensure_repo_root() -> None:
    """Ensure we're running from CloudCurio repo root."""
    cwd = Path.cwd()
    required_paths = [
        "agents",
        "workflows",
        "kb",
        "bin",
        "shell",
        "docker/compose/observability",
        "src",
    ]
    missing = [p for p in required_paths if not (cwd / p).exists()]

    if missing:
        print("ERROR: You are not in CloudCurio repo root.", file=sys.stderr)
        print(f"Please cd to: ~/Documents/cloudcurio_monorepo", file=sys.stderr)
        print(f"\nMissing paths: {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw")
    ap.add_argument("subcommand", nargs="?", default="help")
    ap.add_argument("args", nargs=argparse.REMAINDER)
    ns = ap.parse_args()

    mapping = {
        "agent": "cbw-agent",
        "index": "cbw-index",
        "doctor": "cbw-doctor",
        "workflow": "cbw-workflow",
        "capture": "cbw-capture",
    }

    if ns.subcommand in ("help", "-h", "--help"):
        ap.print_help()
        print("\nCommon:")
        print("  cbw doctor")
        print("  cbw index")
        print("  cbw capture agent my_agent")
        print(
            "  cbw agent run agents/specs/examples/hello_world.agent.yaml --input hi --runtime local"
        )
        raise SystemExit(0)

    exe = mapping.get(ns.subcommand)
    if not exe:
        raise SystemExit(2)
    raise SystemExit(subprocess.call([exe] + ns.args))
