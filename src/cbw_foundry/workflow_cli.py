from __future__ import annotations
import argparse
import subprocess
from pathlib import Path
import yaml

def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-workflow")
    ap.add_argument("workflow")
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.workflow).read_text(encoding="utf-8")) or {}
    steps = data.get("spec", {}).get("steps", [])
    for s in steps:
        action = s.get("action")
        if action == "shell":
            cmd = s.get("with", {}).get("cmd", "")
            if not cmd:
                raise SystemExit(2)
            print(f"==> {s.get('id')}: {cmd}")
            rc = subprocess.run(cmd, shell=True).returncode
            if rc != 0:
                raise SystemExit(rc)
        else:
            print(f"SKIP (not implemented yet): {s.get('id')} action={action}")
    print("Workflow complete.")
