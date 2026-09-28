#!/usr/bin/env python3
"""Skill System for CloudCurio.

Provides skill registration, discovery, and execution.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SkillParameter:
    """Skill parameter definition."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any | None = None


@dataclass
class Skill:
    """Skill definition."""

    name: str
    command: str
    description: str
    parameters: list[SkillParameter] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    workflow: str | None = None
    handler: Callable | None = None
    examples: list[dict[str, Any]] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """Registry for skills."""

    def __init__(self):
        """Initialize skill registry."""
        self.skills: dict[str, Skill] = {}
        logger.info("Initialized skill registry")

    def register(self, skill: Skill) -> None:
        """Register a skill.

        Args:
            skill: Skill to register
        """
        if skill.command in self.skills:
            logger.warning(f"Overwriting existing skill: {skill.command}")

        self.skills[skill.command] = skill
        logger.info(f"Registered skill: {skill.command}")

    def register_from_yaml(self, yaml_path: str) -> None:
        """Register skill from YAML file.

        Args:
            yaml_path: Path to skill YAML file
        """
        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)

            metadata = data.get("metadata", {})
            spec = data.get("spec", {})

            parameters = [
                SkillParameter(
                    name=p["name"],
                    type=p["type"],
                    description=p.get("description", ""),
                    required=p.get("required", True),
                    default=p.get("default"),
                )
                for p in spec.get("parameters", [])
            ]

            skill = Skill(
                name=metadata.get("name", ""),
                command=spec.get("command", ""),
                description=metadata.get("description", ""),
                parameters=parameters,
                agents=spec.get("agents", []),
                workflow=spec.get("workflow"),
                examples=spec.get("examples", []),
                permissions=spec.get("permissions", []),
                config=spec.get("config", {}),
            )

            self.register(skill)

        except Exception as e:
            logger.error(f"Failed to load skill from {yaml_path}: {e}")

    def discover_skills(self, directory: str) -> None:
        """Discover and register skills from directory.

        Args:
            directory: Directory to search for skill YAML files
        """
        skill_dir = Path(directory)
        if not skill_dir.exists():
            logger.warning(f"Skill directory not found: {directory}")
            return

        for yaml_file in skill_dir.rglob("*.skill.yaml"):
            try:
                self.register_from_yaml(str(yaml_file))
            except Exception as e:
                logger.error(f"Failed to load skill {yaml_file}: {e}")

    def get(self, command: str) -> Skill | None:
        """Get skill by command.

        Args:
            command: Slash command

        Returns:
            Skill if found, None otherwise
        """
        return self.skills.get(command)

    def list_skills(self) -> list[Skill]:
        """List all registered skills.

        Returns:
            List of all skills
        """
        return list(self.skills.values())

    def execute(self, command: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a skill.

        Args:
            command: Slash command
            params: Skill parameters

        Returns:
            Execution result
        """
        skill = self.get(command)
        if not skill:
            return {"status": "error", "error": f"Skill not found: {command}"}

        # Validate parameters
        validation_result = self._validate_parameters(skill, params)
        if not validation_result["valid"]:
            return {
                "status": "error",
                "error": f"Parameter validation failed: {validation_result['error']}",
            }

        # Execute skill
        if skill.handler:
            try:
                result = skill.handler(params)
                return {"status": "success", "result": result}
            except Exception as e:
                logger.error(f"Skill execution failed: {e}")
                return {"status": "error", "error": str(e)}
        else:
            return {"status": "error", "error": "No handler defined for skill"}

    def _validate_parameters(self, skill: Skill, params: dict[str, Any]) -> dict[str, Any]:
        """Validate skill parameters.

        Args:
            skill: Skill to validate against
            params: Parameters to validate

        Returns:
            Validation result
        """
        for param in skill.parameters:
            if param.required and param.name not in params:
                return {"valid": False, "error": f"Required parameter missing: {param.name}"}

        return {"valid": True}


# Global registry instance
_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    """Get global skill registry.

    Returns:
        Global skill registry instance
    """
    return _registry


def register_skill(skill: Skill) -> None:
    """Register a skill in global registry.

    Args:
        skill: Skill to register
    """
    _registry.register(skill)


def discover_skills(directory: str = "skills") -> None:
    """Discover and register skills from directory.

    Args:
        directory: Directory to search for skills
    """
    _registry.discover_skills(directory)


__all__ = [
    "Skill",
    "SkillParameter",
    "SkillRegistry",
    "discover_skills",
    "get_registry",
    "register_skill",
]
