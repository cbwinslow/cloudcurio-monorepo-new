from __future__ import annotations
from .base import AgentRuntime, RunResult

class StubRuntime(AgentRuntime):
    def __init__(self, name: str):
        self.name = name
    def run(self, spec_path: str, user_input: str) -> RunResult:
        return RunResult(output={"note": f"{self.name} adapter stub", "input": user_input}, runtime=self.name)
