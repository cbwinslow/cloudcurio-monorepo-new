from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    name: str
    version: str
    tags: List[str] = Field(default_factory=list)

class ModelRef(BaseModel):
    provider: str
    model: str

class ModelPolicy(BaseModel):
    preferred: ModelRef
    fallbacks: List[ModelRef] = Field(default_factory=list)

class PromptSpec(BaseModel):
    system: str

class ToolRef(BaseModel):
    id: str
    type: Literal["python", "shell", "mcp", "http"] = "python"
    entrypoint: str

class EvalSuiteRef(BaseModel):
    id: str
    path: str

class EvalSpec(BaseModel):
    suites: List[EvalSuiteRef] = Field(default_factory=list)

class RuntimeSpec(BaseModel):
    supported: List[Literal["local", "pydanticai", "langchain", "crewai"]] = Field(default_factory=lambda: ["local"])

class AgentSpecBody(BaseModel):
    model_policy: ModelPolicy
    prompts: PromptSpec
    tools: List[ToolRef] = Field(default_factory=list)
    runtime: RuntimeSpec = Field(default_factory=RuntimeSpec)
    eval: EvalSpec = Field(default_factory=EvalSpec)

class AgentSpec(BaseModel):
    api_version: str = "v1"
    kind: Literal["Agent"] = "Agent"
    metadata: Metadata
    spec: AgentSpecBody
