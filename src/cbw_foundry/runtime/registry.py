from __future__ import annotations
from typing import Dict
from .base import AgentRuntime
from .local_runtime import LocalRuntime
from .adapters import PydanticAIRuntime, LangChainRuntime, CrewAIRuntime

def get_runtimes() -> Dict[str, AgentRuntime]:
    return {
        "local": LocalRuntime(),
        "pydanticai": PydanticAIRuntime(),
        "langchain": LangChainRuntime(),
        "crewai": CrewAIRuntime(),
    }
