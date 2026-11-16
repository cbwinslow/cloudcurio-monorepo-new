from __future__ import annotations

from .adapters import CrewAIRuntime, LangChainRuntime, PydanticAIRuntime
from .base import AgentRuntime
from .local_runtime import LocalRuntime


def get_runtimes() -> dict[str, AgentRuntime]:
    return {
        "local": LocalRuntime(),
        "pydanticai": PydanticAIRuntime(),
        "langchain": LangChainRuntime(),
        "crewai": CrewAIRuntime(),
    }
