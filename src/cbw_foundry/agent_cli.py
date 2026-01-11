from __future__ import annotations
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .util.fs import expand_paths
from .spec.models import AgentSpec
from .spec.io import load_yaml
from .spec.compiler import compile_agent
from .evals.runner import run_golden_suite
from .runtime.registry import get_runtimes

console = Console()

def cmd_validate(paths: list[str]) -> int:
    files = expand_paths(paths)
    bad = 0
    for f in files:
        try:
            AgentSpec.model_validate(load_yaml(f))
        except Exception as e:
            bad += 1
            console.print(f"[red]FAIL[/red] {f}: {e}")
    console.print(f"Validated {len(files)} file(s), {bad} failed")
    return 0 if bad == 0 else 1

def cmd_compile(paths: list[str], out: str) -> int:
    files = expand_paths(paths)
    out_dir = Path(out)
    compiled = []
    for f in files:
        compiled.append(compile_agent(f, out_dir))
    t = Table(title="Compiled agents")
    t.add_column("YAML"); t.add_column("JSON")
    for f, j in zip(files, compiled):
        t.add_row(str(f), str(j))
    console.print(t)
    return 0

def cmd_eval(paths: list[str]) -> int:
    files = expand_paths(paths)
    failed = 0
    for f in files:
        ok, failures = run_golden_suite(f)
        if not ok:
            failed += 1
            console.print(f"[red]FAIL[/red] {f}")
            for msg in failures:
                console.print(f"  - {msg}")
    console.print(f"Evals: {len(files)-failed} passed, {failed} failed")
    return 0 if failed == 0 else 1

def cmd_run(spec: str, user_input: str, runtime: str) -> int:
    runtimes = get_runtimes()
    if runtime not in runtimes:
        console.print(f"[red]Unknown runtime[/red]: {runtime}. Options: {', '.join(runtimes)}")
        return 2
    res = runtimes[runtime].run(spec, user_input)
    console.print({"runtime": res.runtime, "output": res.output})
    return 0

def main() -> None:
    ap = argparse.ArgumentParser(prog="cbw-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate")
    pv.add_argument("paths", nargs="+")

    pc = sub.add_parser("compile")
    pc.add_argument("paths", nargs="+")
    pc.add_argument("--out", default="dist/agents")

    pe = sub.add_parser("eval")
    pe.add_argument("paths", nargs="+")

    pr = sub.add_parser("run")
    pr.add_argument("spec")
    pr.add_argument("--input", required=True)
    pr.add_argument("--runtime", default="local")

    args = ap.parse_args()
    if args.cmd == "validate":
        raise SystemExit(cmd_validate(args.paths))
    if args.cmd == "compile":
        raise SystemExit(cmd_compile(args.paths, args.out))
    if args.cmd == "eval":
        raise SystemExit(cmd_eval(args.paths))
    if args.cmd == "run":
        raise SystemExit(cmd_run(args.spec, args.input, args.runtime))
    raise SystemExit(2)
