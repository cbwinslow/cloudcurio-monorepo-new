from __future__ import annotations
from pathlib import Path
from typing import List

def expand_paths(patterns: list[str]) -> List[Path]:
    out: list[Path] = []
    for pat in patterns:
        p = Path(pat)
        if p.exists():
            out.append(p)
            continue
        out.extend(Path(".").glob(pat))
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        rp = str(p.resolve())
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
