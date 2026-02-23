#!/usr/bin/env python3
"""Base Models for CloudCurio Framework.

Pydantic base models for agents, tools, workflows, and skills.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime


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
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class ModelPolicy(BaseModel):
    """Model selection policy with fallbacks."""
    preferred: ModelConfig
    fallbacks: List[ModelConfig] = Field(default_factory=list)


class ToolReference(BaseModel):
    """Reference to a tool."""
    id: str
    type: str = "python"
    entrypoint: str
    config: Dict[str, Any] = Field(default_factory=dict)


class AgentMetadata(BaseModel):
    """Agent metadata."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None


class AgentSpec(BaseModel):
    """Agent specification."""
    api_version: str = "v1"
    kind: str = "Agent"
    metadata: AgentMetadata
    model_policy: ModelPolicy
    prompts: Dict[str, str]
    tools: List[ToolReference] = Field(default_factory=list)
    runtime: Dict[str, Any] = Field(default_factory=dict)
    role: AgentRole = AgentRole.WORKER
    capabilities: List[str] = Field(default_factory=list)
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
    author: Optional[str] = None


class ToolSpec(BaseModel):
    """Tool specification."""
    metadata: ToolMetadata
    config: ToolConfig
    entrypoint: str
    dependencies: List[str] = Field(default_factory=list)


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
    agent: Optional[str] = None
    action: Optional[str] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    output_var: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    timeout: int = Field(default=300, gt=0)
    parallel_group: Optional[str] = None


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
    tags: List[str] = Field(default_factory=list)


class WorkflowSpec(BaseModel):
    """Workflow specification."""
    api_version: str = "v1"
    kind: str = "Workflow"
    metadata: WorkflowMetadata
    coordination: CoordinationMode
    steps: List[WorkflowStep]
    error_handling: ErrorHandling = Field(default_factory=ErrorHandling)
    outputs: Dict[str, str] = Field(default_factory=dict)


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
    default: Optional[Any] = None


class SkillMetadata(BaseModel):
    """Skill metadata."""
    name: str
    version: str = "1.0.0"
    description: str
    type: SkillType
    tags: List[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    """Skill specification."""
    api_version: str = "v1"
    kind: str = "Skill"
    metadata: SkillMetadata
    parameters: List[SkillParameter] = Field(default_factory=list)
    agents: List[str] = Field(default_factory=list)
    workflow: Optional[str] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)


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
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None


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
    tools: List[str] = Field(default_factory=list)
    agents: List[str] = Field(default_factory=list)


__all__ = [
    "AgentRole",
    "ModelProvider",
    "ModelConfig",
    "ModelPolicy",
    "ToolReference",
    "AgentMetadata",
    "AgentSpec",
    "ToolCategory",
    "ToolConfig",
    "ToolMetadata",
    "ToolSpec",
    "CoordinationMode",
    "WorkflowStep",
    "ErrorHandling",
    "WorkflowMetadata",
    "WorkflowSpec",
    "SkillType",
    "SkillParameter",
    "SkillMetadata",
    "SkillSpec",
    "ExecutionStatus",
    "ExecutionResult",
    "IntegrationType",
    "IntegrationConfig",
]
