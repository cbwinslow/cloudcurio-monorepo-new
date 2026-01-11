from __future__ import annotations
from pathlib import Path
from .models import AgentSpec
from .io import load_yaml, dump_json
from ..observability.otel import maybe_otel_span

def compile_agent(yaml_path: Path, out_dir: Path) -> Path:
    with maybe_otel_span("compile_agent"):
        raw = load_yaml(yaml_path)
        obj = AgentSpec.model_validate(raw)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{obj.metadata.name}.agent.json"
        dump_json(out_path, obj.model_dump(mode="json"))
        return out_path
