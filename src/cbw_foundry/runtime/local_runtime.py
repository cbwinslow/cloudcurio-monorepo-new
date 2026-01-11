from __future__ import annotations
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from .base import AgentRuntime, RunResult
from ..spec.models import AgentSpec
from ..spec.io import load_yaml

class LocalRuntime(AgentRuntime):
    name = "local"

    def run(self, spec_path: str, user_input: str) -> RunResult:
        agent = AgentSpec.model_validate(load_yaml(spec_path))
        tool = next((t for t in agent.spec.tools if t.type == "python"), None)
        if tool:
            mod_path, func = tool.entrypoint.split(":")
            mod_fs = Path(mod_path)
            if not mod_fs.exists():
                return RunResult(output={"error": f"tool module not found: {mod_fs}"}, runtime=self.name)
            sp = spec_from_file_location(mod_fs.stem, mod_fs)
            assert sp and sp.loader
            m = module_from_spec(sp)
            sp.loader.exec_module(m)
            fn = getattr(m, func, None)
            if fn is None:
                return RunResult(output={"error": f"tool func not found: {func}"}, runtime=self.name)
            return RunResult(output=fn(user_input), runtime=self.name)
        return RunResult(output={"echo": user_input}, runtime=self.name)
