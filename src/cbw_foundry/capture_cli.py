from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import textwrap
import subprocess

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def new_agent(name: str) -> Path:
    p = Path("agents/specs") / f"{name}.agent.yaml"
    _write(p, textwrap.dedent(f"""\
    api_version: v1
    kind: Agent
    metadata:
      name: {name}
      version: 0.1.0
      tags: [user]
    spec:
      model_policy:
        preferred:
          provider: ollama
          model: qwen2.5-coder
        fallbacks: []
      prompts:
        system: prompts/system/default.md
      tools: []
      runtime:
        supported: [local]
      eval:
        suites: []
    """))
    return p

def new_workflow(name: str) -> Path:
    p = Path("workflows/library") / f"{name}.workflow.yaml"
    _write(p, textwrap.dedent(f"""\
    api_version: v1
    kind: Workflow
    metadata:
      name: {name}
      version: 0.1.0
      tags: [user]
    spec:
      steps:
        - id: step1
          action: shell
          with:
            cmd: "echo hello"
    """))
    return p

def new_kb(slug: str, title: str) -> Path:
    p = Path("kb/notes") / f"{_ts()}_{slug}.md"
    today = datetime.now().strftime("%Y-%m-%d")
    _write(p, textwrap.dedent(f"""\
    ---
    title: {title}
    tags: [note]
    owner: cbwinslow
    last_reviewed: {today}
    ---

    # {title}

    """))
    return p

def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-capture")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("agent")
    a.add_argument("name")

    wf = sub.add_parser("workflow")
    wf.add_argument("name")

    k = sub.add_parser("kb")
    k.add_argument("slug")
    k.add_argument("--title", default="Note")

    args = ap.parse_args()
    if args.cmd == "agent":
        p = new_agent(args.name)
    elif args.cmd == "workflow":
        p = new_workflow(args.name)
    else:
        p = new_kb(args.slug, args.title)

    print(f"Wrote: {p}")
    subprocess.run(["./bin/cbw-index"], check=False)
