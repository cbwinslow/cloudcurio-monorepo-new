#!/usr/bin/env python3
"""Base Models for CloudCurio Framework.

Pydantic base models for agents, tools, workflows, and skills.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ==================== Agent Models ====================


class AgentRole(str, Enum):
    """Agent role types."""

    COORDINATOR = "coordinator"
    WORKER = "worker"
    REVIEWER = "reviewer"
    SPECIALIST = "specialist"


class ModelProvider(str, Enum):
    """LLM provider types."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    COHERE = "cohere"


class ModelConfig(BaseModel):
    """LLM model configuration."""

    provider: ModelProvider
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    api_key: str | None = None
    base_url: str | None = None


class ModelPolicy(BaseModel):
    """Model selection policy with fallbacks."""

    preferred: ModelConfig
    fallbacks: list[ModelConfig] = Field(default_factory=list)


class ToolReference(BaseModel):
    """Reference to a tool."""

    id: str
    type: str = "python"
    entrypoint: str
    config: dict[str, Any] = Field(default_factory=dict)


class AgentMetadata(BaseModel):
    """Agent metadata."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    author: str | None = None


class AgentSpec(BaseModel):
    """Agent specification."""

    api_version: str = "v1"
    kind: str = "Agent"
    metadata: AgentMetadata
    model_policy: ModelPolicy
    prompts: dict[str, str]
    tools: list[ToolReference] = Field(default_factory=list)
    runtime: dict[str, Any] = Field(default_factory=dict)
    role: AgentRole = AgentRole.WORKER
    capabilities: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


# ==================== Tool Models ====================


class ToolCategory(str, Enum):
    """Tool category types."""

    LLM = "llm"
    WEB = "web"
    FILE = "file"
    DATA = "data"
    SYSTEM = "system"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class ToolConfig(BaseModel):
    """Base tool configuration."""

    timeout: int = Field(default=30, gt=0)
    retries: int = Field(default=3, ge=0)


class ToolMetadata(BaseModel):
    """Tool metadata."""

    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    author: str | None = None


class ToolSpec(BaseModel):
    """Tool specification."""

    metadata: ToolMetadata
    config: ToolConfig
    entrypoint: str
    dependencies: list[str] = Field(default_factory=list)


# ==================== Workflow Models ====================


class CoordinationMode(str, Enum):
    """Workflow coordination modes."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEMOCRATIC = "democratic"
    HIERARCHICAL = "hierarchical"


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    id: str
    name: str
    agent: str | None = None
    action: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    output_var: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    timeout: int = Field(default=300, gt=0)
    parallel_group: str | None = None


class ErrorHandling(BaseModel):
    """Error handling configuration."""

    retry_failed_steps: bool = True
    max_retries: int = Field(default=2, ge=0)
    continue_on_error: bool = False


class WorkflowMetadata(BaseModel):
    """Workflow metadata."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class WorkflowSpec(BaseModel):
    """Workflow specification."""

    api_version: str = "v1"
    kind: str = "Workflow"
    metadata: WorkflowMetadata
    coordination: CoordinationMode
    steps: list[WorkflowStep]
    error_handling: ErrorHandling = Field(default_factory=ErrorHandling)
    outputs: dict[str, str] = Field(default_factory=dict)


# ==================== Skill Models ====================


class SkillType(str, Enum):
    """Skill types."""

    COMMAND = "command"
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    TRANSFORMATION = "transformation"


class SkillParameter(BaseModel):
    """Skill parameter definition."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any | None = None


class SkillMetadata(BaseModel):
    """Skill metadata."""

    name: str
    version: str = "1.0.0"
    description: str
    type: SkillType
    tags: list[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    """Skill specification."""

    api_version: str = "v1"
    kind: str = "Skill"
    metadata: SkillMetadata
    parameters: list[SkillParameter] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)
    workflow: str | None = None
    examples: list[dict[str, Any]] = Field(default_factory=list)


# ==================== Execution Models ====================


class ExecutionStatus(str, Enum):
    """Execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionResult(BaseModel):
    """Execution result."""

    status: ExecutionStatus
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: float | None = None


# ==================== Integration Models ====================


class IntegrationType(str, Enum):
    """AI tool integration types."""

    COPILOT = "copilot"
    KILOCODE = "kilocode"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    CURSOR = "cursor"
    CODEIUM = "codeium"


class IntegrationConfig(BaseModel):
    """Integration configuration."""

    type: IntegrationType
    enabled: bool = True
    config_path: str
    tools: list[str] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)


__all__ = [
    "AgentMetadata",
    "AgentRole",
    "AgentSpec",
    "CoordinationMode",
    "ErrorHandling",
    "ExecutionResult",
    "ExecutionStatus",
    "IntegrationConfig",
    "IntegrationType",
    "ModelConfig",
    "ModelPolicy",
    "ModelProvider",
    "SkillMetadata",
    "SkillParameter",
    "SkillSpec",
    "SkillType",
    "ToolCategory",
    "ToolConfig",
    "ToolMetadata",
    "ToolReference",
    "ToolSpec",
    "WorkflowMetadata",
    "WorkflowSpec",
    "WorkflowStep",
]
