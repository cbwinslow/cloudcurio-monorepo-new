from __future__ import annotations
from .base import AgentRuntime, RunResult

class PydanticAIRuntime(AgentRuntime):
    name = "pydanticai"
    def run(self, spec_path: str, user_input: str) -> RunResult:
        return RunResult(output={"note": "adapter stub", "runtime": "pydanticai", "input": user_input}, runtime=self.name)

class LangChainRuntime(AgentRuntime):
    name = "langchain"
    def run(self, spec_path: str, user_input: str) -> RunResult:
        return RunResult(output={"note": "adapter stub", "runtime": "langchain", "input": user_input}, runtime=self.name)

class CrewAIRuntime(AgentRuntime):
    name = "crewai"
    def run(self, spec_path: str, user_input: str) -> RunResult:
        return RunResult(output={"note": "adapter stub", "runtime": "crewai", "input": user_input}, runtime=self.name)
