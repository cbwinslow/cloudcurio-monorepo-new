#!/usr/bin/env python3
"""
Efficiency Enforcer for Pydantic AI Democratic Swarm

This module implements the efficiency rules and guardrails that prevent the swarm
from creating duplicate files, redundant agents, and inefficient code patterns.

The EfficiencyEnforcer automatically:
- Analyzes proposed actions for duplication
- Enforces consensus requirements for different action types
- Tracks efficiency metrics
- Provides alternatives when duplication is detected
"""

import asyncio
import hashlib
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from agents.pydantic_ai_swarm_orchestrator import PydanticAISwarmOrchestrator


@dataclass
class SwarmAction:
    """Represents a proposed swarm action."""
    action_type: str  # "create_file", "create_agent", "modify_core", "extend_agent"
    description: str
    target: str  # file path, agent name, etc.
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationResult:
    """Result of action validation."""
    approved: bool
    reason: str
    alternatives: List[Dict[str, Any]]
    confidence: float = 0.0
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class EnforcementResult:
    """Result of rule enforcement."""
    approved: bool
    reason: str
    alternatives: List[Dict[str, Any]] = None
    required_consensus: float = 0.0
    efficiency_score: float = 0.0

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class EfficiencyEnforcer:
    """
    Enforces efficiency rules and prevents duplication in the swarm.

    This class automatically analyzes all proposed swarm actions and enforces
    the efficiency rules defined in docs/swarm_efficiency_rules.md.
    """

    def __init__(self, swarm: "PydanticAISwarmOrchestrator"):
        self.swarm = swarm
        self.project_root = Path(__file__).parent.parent

        # Efficiency tracking
        self.prevented_duplicates = 0
        self.total_actions_analyzed = 0
        self.efficiency_metrics = {
            "duplicate_prevention_rate": 0.0,
            "code_reuse_rate": 0.0,
            "consensus_efficiency": 0.0,
        }

        # Agent capability registry to prevent duplicates
        self.agent_capabilities: Dict[str, str] = {}
        self.file_hashes: Dict[str, str] = {}

        # Initialize capability registry
        self._initialize_capability_registry()

    def _initialize_capability_registry(self):
        """Initialize the registry of existing agent capabilities."""
        # Map existing agents to their primary capabilities
        self.agent_capabilities = {
            # Video/Audio agents
            "video_editing": "PydanticVideoEditorAgent",
            "video_analysis": "PydanticVideoEditorAgent",
            "content_editing": "PydanticVideoEditorAgent",

            # Analysis agents
            "content_analysis": "ContentAnalysisAgent",
            "engagement_analysis": "ContentAnalysisAgent",
            "performance_analysis": "ContentAnalysisAgent",

            # GitHub agents
            "github_management": "GitHubAgent",
            "issue_analysis": "GitHubIssueAnalyzerAgent",
            "repository_management": "GitHubAgent",

            # Social media agents
            "social_media": "SocialMediaAgent",
            "posting": "SocialMediaAgent",
            "engagement": "SocialMediaAgent",

            # Content agents
            "content_strategy": "ContentStrategyAgent",
            "content_generation": "ContentStrategyAgent",
            "platform_optimization": "ContentStrategyAgent",
        }

    async def validate_action(self, action: SwarmAction) -> ValidationResult:
        """
        Validate a proposed swarm action against efficiency rules.

        Returns a ValidationResult indicating whether the action should proceed.
        """
        self.total_actions_analyzed += 1

        # Apply different validation based on action type
        if action.action_type == "create_file":
            return await self._validate_file_creation(action)
        elif action.action_type == "create_agent":
            return await self._validate_agent_creation(action)
        elif action.action_type == "modify_core":
            return await self._validate_core_modification(action)
        elif action.action_type == "extend_agent":
            return await self._validate_agent_extension(action)
        else:
            return ValidationResult(
                approved=True,
                reason="Action type not restricted",
                alternatives=[]
            )

    async def _validate_file_creation(self, action: SwarmAction) -> ValidationResult:
        """Validate file creation against duplication rules."""
        if not action.content:
            return ValidationResult(
                approved=False,
                reason="File content required for validation",
                alternatives=[]
            )

        # Check for duplicate files
        duplicates = await self._find_duplicate_files(action.target, action.content)

        if duplicates:
            self.prevented_duplicates += 1
            alternatives = []
            for dup in duplicates[:3]:  # Show top 3 alternatives
                alternatives.append({
                    "type": "modify_existing",
                    "file": dup["file"],
                    "similarity": dup["similarity"],
                    "reason": f"Extend existing {dup['file']} instead"
                })

            return ValidationResult(
                approved=False,
                reason="Duplicate file detected - use existing functionality",
                alternatives=alternatives,
                recommendations=[
                    "Search for existing similar files first",
                    "Consider extending existing agents instead",
                    "Review the codebase for reuse opportunities"
                ]
            )

        # Check if this extends existing functionality appropriately
        extension_check = await self._validate_extension_appropriateness(action)
        if not extension_check["appropriate"]:
            return ValidationResult(
                approved=False,
                reason=extension_check["reason"],
                alternatives=extension_check["alternatives"],
                recommendations=["Consider if this functionality is truly needed"]
            )

        return ValidationResult(
            approved=True,
            reason="File creation approved - no duplicates found",
            alternatives=[]
        )

    async def _validate_agent_creation(self, action: SwarmAction) -> ValidationResult:
        """Validate agent creation against redundancy rules."""
        if not action.metadata:
            return ValidationResult(
                approved=False,
                reason="Agent metadata required for validation",
                alternatives=[]
            )

        # Check for similar existing agents
        capabilities = action.metadata.get("capabilities", [])
        similar_agents = []

        for capability in capabilities:
            if capability in self.agent_capabilities:
                existing_agent = self.agent_capabilities[capability]
                if existing_agent not in [a["agent"] for a in similar_agents]:
                    similar_agents.append({
                        "agent": existing_agent,
                        "capability": capability,
                        "reason": f"Can handle {capability}"
                    })

        if similar_agents:
            alternatives = []
            for agent_info in similar_agents:
                alternatives.append({
                    "type": "extend_existing",
                    "agent": agent_info["agent"],
                    "capability": agent_info["capability"],
                    "reason": f"Extend {agent_info['agent']} for {agent_info['capability']}"
                })

            return ValidationResult(
                approved=False,
                reason="Similar agent capabilities already exist",
                alternatives=alternatives,
                recommendations=[
                    "Extend existing agents instead of creating new ones",
                    "Check agent capability registry first",
                    "Consider if new specialized functionality is truly needed"
                ]
            )

        return ValidationResult(
            approved=True,
            reason="Agent creation approved - unique capabilities",
            alternatives=[]
        )

    async def _validate_core_modification(self, action: SwarmAction) -> ValidationResult:
        """Validate core system modifications."""
        # Core modifications require high consensus
        core_files = [
            "agents/pydantic_ai_swarm_orchestrator.py",
            "agents/base_agent.py",
            "agents/pydantic_ai_agent.py",
            "pyproject.toml",
            "README.md"
        ]

        if any(core_file in action.target for core_file in core_files):
            return ValidationResult(
                approved=True,  # Allow but require high consensus
                reason="Core modification - requires 95% consensus",
                alternatives=[],
                recommendations=[
                    "Core modifications require 95%+ swarm consensus",
                    "Ensure backward compatibility",
                    "Have migration plan ready"
                ]
            )

        return ValidationResult(
            approved=True,
            reason="Non-core modification approved",
            alternatives=[]
        )

    async def _validate_agent_extension(self, action: SwarmAction) -> ValidationResult:
        """Validate agent extensions."""
        # Extensions are generally encouraged over new creation
        return ValidationResult(
            approved=True,
            reason="Agent extensions are encouraged",
            alternatives=[],
            recommendations=[
                "Good practice: extending existing agents",
                "Ensure extension doesn't break existing functionality",
                "Update agent documentation"
            ]
        )

    async def _find_duplicate_files(self, target_path: str, content: str) -> List[Dict[str, Any]]:
        """Find files with similar content."""
        duplicates = []

        # Calculate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Skip if we've seen this exact content before
        if content_hash in self.file_hashes.values():
            for existing_file, existing_hash in self.file_hashes.items():
                if existing_hash == content_hash:
                    duplicates.append({
                        "file": existing_file,
                        "similarity": 1.0,
                        "reason": "Identical content already exists"
                    })
            return duplicates

        # Analyze content for similarity with existing files
        similar_files = await self._analyze_content_similarity(target_path, content)

        # Filter for high similarity matches
        for file_info in similar_files:
            if file_info["similarity"] > 0.7:  # 70% similarity threshold
                duplicates.append(file_info)

        return duplicates

    async def _analyze_content_similarity(self, target_path: str, content: str) -> List[Dict[str, Any]]:
        """Analyze content similarity with existing files."""
        similar_files = []

        # Get all Python files in the project
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if str(file_path).endswith(target_path):
                continue  # Skip self-comparison

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

                # Calculate similarity metrics
                similarity = self._calculate_content_similarity(content, existing_content)

                if similarity > 0.3:  # Any significant similarity
                    similar_files.append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "similarity": similarity,
                        "reason": f"{similarity:.1f} similarity with existing file"
                    })

            except Exception:
                continue  # Skip files that can't be read

        return sorted(similar_files, key=lambda x: x["similarity"], reverse=True)

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings."""
        # Simple similarity based on common lines and functions
        lines1 = set(content1.strip().split('\n'))
        lines2 = set(content2.strip().split('\n'))

        if not lines1 or not lines2:
            return 0.0

        # Jaccard similarity of lines
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)

        if union == 0:
            return 0.0

        similarity = intersection / union

        # Boost similarity if they have similar function/class definitions
        func_pattern = r'def \w+|class \w+'
        funcs1 = set(re.findall(func_pattern, content1))
        funcs2 = set(re.findall(func_pattern, content2))

        if funcs1 and funcs2:
            func_similarity = len(funcs1 & funcs2) / len(funcs1 | funcs2)
            similarity = (similarity + func_similarity) / 2

        return similarity

    async def _validate_extension_appropriateness(self, action: SwarmAction) -> Dict[str, Any]:
        """Validate if a new file is an appropriate extension."""
        # Check if this is truly extending functionality vs duplicating
        content = action.content or ""

        # Look for signs of inappropriate new file creation
        inappropriate_indicators = [
            "class.*Agent.*:",  # New agent classes
            "from agents.base_agent import",  # Importing base agent for new file
            "def __init__.*agent_name",  # Agent initialization pattern
        ]

        for indicator in inappropriate_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                # Check if there's a legitimate reason for this
                if not await self._has_legitimate_extension_reason(action):
                    return {
                        "appropriate": False,
                        "reason": "Appears to create duplicate agent functionality",
                        "alternatives": [
                            {
                                "type": "extend_existing",
                                "reason": "Extend existing agent classes instead of creating new ones"
                            }
                        ]
                    }

        return {
            "appropriate": True,
            "reason": "Extension appears appropriate",
            "alternatives": []
        }

    async def _has_legitimate_extension_reason(self, action: SwarmAction) -> bool:
        """Check if there's a legitimate reason for creating this new file."""
        # This would check if the new file serves a unique purpose
        # For now, be conservative and require explicit justification
        metadata = action.metadata or {}
        justification = metadata.get("justification", "")

        legitimate_reasons = [
            "unique_business_logic",
            "new_domain_expertise",
            "performance_optimization",
            "architectural_separation"
        ]

        return any(reason in justification for reason in legitimate_reasons)

    def get_consensus_requirement(self, action: SwarmAction) -> float:
        """Get the consensus percentage required for an action."""
        requirements = {
            "create_file": 0.8,      # 80% consensus for new files
            "create_agent": 0.9,     # 90% consensus for new agents
            "modify_core": 0.95,     # 95% consensus for core changes
            "extend_agent": 0.6,     # 60% consensus for extensions
            "add_tool": 0.7,         # 70% consensus for new tools
            "update_config": 0.75,   # 75% consensus for config changes
        }

        return requirements.get(action.action_type, 0.5)  # Default 50%

    async def enforce_action(self, action: SwarmAction) -> EnforcementResult:
        """Enforce efficiency rules on a proposed action."""
        # First validate the action
        validation = await self.validate_action(action)

        if not validation.approved:
            return EnforcementResult(
                approved=False,
                reason=validation.reason,
                alternatives=validation.alternatives
            )

        # Get consensus requirement
        required_consensus = self.get_consensus_requirement(action)

        # Calculate efficiency score
        efficiency_score = await self._calculate_efficiency_score(action)

        return EnforcementResult(
            approved=True,
            reason="Action approved with efficiency validation",
            alternatives=[],
            required_consensus=required_consensus,
            efficiency_score=efficiency_score
        )

    async def _calculate_efficiency_score(self, action: SwarmAction) -> float:
        """Calculate efficiency score for an action."""
        score = 0.5  # Base score

        # Reward actions that reuse existing code
        if action.action_type == "extend_agent":
            score += 0.3
        elif action.action_type == "modify_core":
            score -= 0.1  # Slight penalty for core modifications

        # Check if action follows efficiency patterns
        if action.metadata:
            if action.metadata.get("reuses_existing"):
                score += 0.2
            if action.metadata.get("avoids_duplication"):
                score += 0.2
            if action.metadata.get("has_tests"):
                score += 0.1

        return min(1.0, max(0.0, score))

    def update_metrics(self):
        """Update efficiency metrics."""
        if self.total_actions_analyzed > 0:
            self.efficiency_metrics["duplicate_prevention_rate"] = (
                self.prevented_duplicates / self.total_actions_analyzed
            )

    def get_efficiency_report(self) -> Dict[str, Any]:
        """Get comprehensive efficiency report."""
        self.update_metrics()

        return {
            "total_actions_analyzed": self.total_actions_analyzed,
            "duplicates_prevented": self.prevented_duplicates,
            "efficiency_metrics": self.efficiency_metrics,
            "agent_capability_coverage": len(self.agent_capabilities),
            "recommendations": self._generate_efficiency_recommendations()
        }

    def _generate_efficiency_recommendations(self) -> List[str]:
        """Generate efficiency improvement recommendations."""
        recommendations = []

        prevention_rate = self.efficiency_metrics["duplicate_prevention_rate"]

        if prevention_rate < 0.5:
            recommendations.append("Consider strengthening duplicate detection rules")
        elif prevention_rate > 0.8:
            recommendations.append("Excellent duplicate prevention - maintain current rules")

        if self.total_actions_analyzed < 10:
            recommendations.append("Increase swarm activity to gather more efficiency data")

        return recommendations

    async def register_agent_capability(self, agent_name: str, capability: str):
        """Register a new agent capability to prevent future duplication."""
        if capability in self.agent_capabilities:
            existing_agent = self.agent_capabilities[capability]
            print(f"WARNING: Capability '{capability}' already registered to {existing_agent}")
        else:
            self.agent_capabilities[capability] = agent_name
            print(f"Registered capability '{capability}' for agent '{agent_name}'")

    def get_registered_capabilities(self) -> Dict[str, str]:
        """Get all registered agent capabilities."""
        return self.agent_capabilities.copy()

    async def analyze_codebase_efficiency(self) -> Dict[str, Any]:
        """Analyze the overall codebase efficiency."""
        analysis = {
            "total_python_files": len(list(self.project_root.rglob("*.py"))),
            "agent_files": len(list(self.project_root.glob("agents/*.py"))),
            "test_files": len(list(self.project_root.glob("tests/*.py"))),
            "duplicate_risk_areas": await self._identify_duplicate_risk_areas(),
            "reuse_opportunities": await self._find_reuse_opportunities(),
        }

        return analysis

    async def _identify_duplicate_risk_areas(self) -> List[str]:
        """Identify areas with high duplication risk."""
        risk_areas = []

        # Check for multiple agent files with similar names
        agent_files = list(self.project_root.glob("agents/*agent*.py"))
        if len(agent_files) > 5:
            risk_areas.append("Multiple agent files - review for consolidation")

        # Check for similar test files
        test_files = list(self.project_root.glob("tests/test_*.py"))
        if len(test_files) > 10:
            risk_areas.append("Large number of test files - ensure proper organization")

        return risk_areas

    async def _find_reuse_opportunities(self) -> List[str]:
        """Find opportunities for code reuse."""
        opportunities = []

        # Look for similar function names across files
        # This is a simplified version - could be more sophisticated
        opportunities.append("Review utility functions for potential consolidation")
        opportunities.append("Consider creating shared base classes where appropriate")

        return opportunities


# Global efficiency enforcer instance
_efficiency_enforcer: Optional[EfficiencyEnforcer] = None


def get_efficiency_enforcer(swarm: Optional["PydanticAISwarmOrchestrator"] = None) -> EfficiencyEnforcer:
    """Get or create the global efficiency enforcer."""
    global _efficiency_enforcer

    if _efficiency_enforcer is None and swarm is not None:
        _efficiency_enforcer = EfficiencyEnforcer(swarm)

    return _efficiency_enforcer


async def validate_swarm_action(action: SwarmAction) -> ValidationResult:
    """Convenience function to validate swarm actions."""
    enforcer = get_efficiency_enforcer()
    if enforcer:
        return await enforcer.validate_action(action)
    else:
        # If no enforcer, approve by default but log warning
        print("WARNING: No efficiency enforcer available - approving action")
        return ValidationResult(
            approved=True,
            reason="No enforcer available",
            alternatives=[]
        )


async def enforce_swarm_action(action: SwarmAction) -> EnforcementResult:
    """Convenience function to enforce swarm actions."""
    enforcer = get_efficiency_enforcer()
    if enforcer:
        return await enforcer.enforce_action(action)
    else:
        return EnforcementResult(
            approved=True,
            reason="No enforcer available",
            required_consensus=0.5
        )


# Integration with swarm orchestrator
async def integrate_with_swarm(swarm: "PydanticAISwarmOrchestrator"):
    """Integrate efficiency enforcer with swarm orchestrator."""
    enforcer = EfficiencyEnforcer(swarm)

    # Register existing agent capabilities
    for agent in swarm.agents.values():
        agent_name = agent.agent_name
        # Extract capabilities from agent config or class
        capabilities = getattr(agent, 'domain_expertise', [])
        for capability in capabilities:
            await enforcer.register_agent_capability(agent_name, capability)

    # Store global reference
    global _efficiency_enforcer
    _efficiency_enforcer = enforcer

    print(f"Integrated efficiency enforcer with {len(enforcer.agent_capabilities)} registered capabilities")
    return enforcer
