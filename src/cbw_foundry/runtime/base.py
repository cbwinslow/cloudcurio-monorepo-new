from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class RunResult:
    output: Any
    runtime: str

class AgentRuntime(ABC):
    name: str

    @abstractmethod
    def run(self, spec_path: str, user_input: str) -> RunResult:
        raise NotImplementedError
