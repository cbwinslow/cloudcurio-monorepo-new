from __future__ import annotations
from pathlib import Path
import yaml
from ..observability.otel import maybe_otel_span

def run_golden_suite(path: str | Path) -> tuple[bool, list[str]]:
    with maybe_otel_span("eval_golden_suite"):
        p = Path(path)
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        cases = data.get("cases", [])
        failures: list[str] = []
        for c in cases:
            cid = str(c.get("id", "case"))
            inp = str(c.get("input", ""))
            exp = str(c.get("expect_contains", ""))
            if exp and exp not in inp:
                failures.append(f"{cid}: expected '{exp}' in '{inp}'")
        return (len(failures) == 0, failures)
