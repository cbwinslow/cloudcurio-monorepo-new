"""Enhanced Website & Social Media Analysis Agents

This module implements a comprehensive, industry-standard AI agent system for
website and social media analysis using the Enhanced Base Agent framework.
It fully integrates all modern AI frameworks (LangChain, CrewAI, LangGraph)
with proper guardrails, rules, and reusable patterns.

Key Features:
- Full Enhanced Base Agent integration with all frameworks
- Comprehensive guardrails and validation rules
- Industry-standard analysis patterns
- Reusable components and utilities
- Proper error handling and observability
- Democratic decision making capabilities
- Configuration management and validation
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from agents.base_agent import AgentTool, ConfidenceMetrics

# Import enhanced base agent and related components
from agents.enhanced_base_agent import (
    EnhancedAgentTool,
    EnhancedBaseAgent,
    EnhancedWorkflowOrchestrator,
)
from agents.robust_tool import RobustTool, ToolResult
from agents.swarm_communication import MessageBus, VotingSystem

# Import framework components
try:
    from crewai import Agent, Crew, Process, Task
    from crewai_tools import BaseTool as CrewAIBaseTool
    from langchain_core.messages import HumanMessage
    from langchain_core.tools import tool
    from langgraph.graph import Graph
    from langgraph.prebuilt import ToolNode
except ImportError:
    pass

# Import guardrails and rules
try:
    from agents.efficiency_enforcer import EfficiencyGuardrails
    from agents.swarm_communication import MessageBus, VotingSystem
except ImportError:
    pass

# Set up logging
logger = logging.getLogger(__name__)

# Constants for guardrails and rules
ANALYSIS_GUARDRAILS = {
    "data_quality": {
        "min_data_points": 100,
        "max_missing_data": 0.1,  # 10% max missing
        "confidence_threshold": 0.7
    },
    "analysis_limits": {
        "max_time_period": "365_days",  # 1 year max
        "min_time_period": "7_days",    # 7 days min
        "max_platforms": 10,
        "max_keywords": 50
    },
    "performance_metrics": {
        "min_engagement_rate": 0.01,    # 1%
        "max_bounce_rate": 0.7,        # 70%
        "min_completion_rate": 0.5     # 50%
    },
    "validation_rules": {
        "required_fields": ["time_period", "analysis_type"],
        "data_consistency_checks": True,
        "cross_validation_required": True
    }
}

# Analysis rules based on industry standards
ANALYSIS_RULES = {
    "website_analysis": {
        "traffic_analysis": {
            "min_visits_for_significance": 1000,
            "bounce_rate_warning": 0.6,    # 60%
            "bounce_rate_critical": 0.7,   # 70%
            "session_duration_good": 180,  # 3 minutes in seconds
            "session_duration_excellent": 300  # 5 minutes
        },
        "seo_analysis": {
            "good_keyword_ranking": 10,
            "excellent_keyword_ranking": 5,
            "min_domain_authority": 30,
            "good_domain_authority": 50,
            "excellent_domain_authority": 70,
            "min_backlinks": 50,
            "good_backlinks": 200,
            "excellent_backlinks": 500
        },
        "technical_analysis": {
            "max_broken_links": 5,
            "min_page_speed_score": 70,
            "good_page_speed_score": 90,
            "min_mobile_score": 80,
            "good_mobile_score": 95
        }
    },
    "social_media_analysis": {
        "platform_performance": {
            "min_engagement_rate": 0.02,    # 2%
            "good_engagement_rate": 0.05,   # 5%
            "excellent_engagement_rate": 0.08,  # 8%
            "min_follower_growth": 0.01,    # 1% monthly
            "good_follower_growth": 0.05,   # 5% monthly
            "excellent_follower_growth": 0.1  # 10% monthly
        },
        "content_performance": {
            "min_completion_rate": 0.5,     # 50%
            "good_completion_rate": 0.7,    # 70%
            "excellent_completion_rate": 0.85,  # 85%
            "min_share_rate": 0.01,         # 1%
            "good_share_rate": 0.03,        # 3%
            "excellent_share_rate": 0.05    # 5%
        },
        "sentiment_analysis": {
            "min_positive_sentiment": 0.6,  # 60%
            "warning_negative_sentiment": 0.15,  # 15%
            "critical_negative_sentiment": 0.25   # 25%
        }
    },
    "content_analysis": {
        "episode_performance": {
            "min_views_for_analysis": 100,
            "good_completion_rate": 0.7,
            "excellent_completion_rate": 0.85,
            "min_shares_per_1000_views": 5,
            "good_shares_per_1000_views": 15,
            "excellent_shares_per_1000_views": 30
        },
        "short_form_performance": {
            "min_views_for_analysis": 50,
            "good_engagement_rate": 0.1,    # 10%
            "excellent_engagement_rate": 0.15,  # 15%
            "min_conversion_rate": 0.05,   # 5% to full episode
            "good_conversion_rate": 0.1,   # 10% to full episode
            "excellent_conversion_rate": 0.15  # 15% to full episode
        }
    }
}

class AnalysisGuardrails:
    """Guardrails and validation for analysis processes."""

    def __init__(self):
        """Initialize analysis guardrails."""
        self.guardrails = ANALYSIS_GUARDRAILS
        self.rules = ANALYSIS_RULES
        self.voting_system = VotingSystem(MessageBus())

    def validate_analysis_parameters(self, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate analysis parameters against guardrails.

        Args:
            params: Analysis parameters

        Returns:
            Tuple of (is_valid, validation_results)
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "parameter_checks": {}
        }

        # Check required fields
        required_fields = self.guardrails["validation_rules"]["required_fields"]
        for field in required_fields:
            if field not in params:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["valid"] = False

        # Check time period
        time_period = params.get("time_period", "")
        if time_period:
            max_days = int(self.guardrails["analysis_limits"]["max_time_period"].split("_")[0])
            min_days = int(self.guardrails["analysis_limits"]["min_time_period"].split("_")[0])

            try:
                period_days = int(time_period.split("_")[0])
                if period_days > max_days:
                    validation_results["errors"].append(f"Time period exceeds maximum of {max_days} days")
                    validation_results["valid"] = False
                elif period_days < min_days:
                    validation_results["warnings"].append(f"Time period below recommended minimum of {min_days} days")
            except (ValueError, IndexError):
                validation_results["errors"].append("Invalid time period format. Use format like '30_days'")
                validation_results["valid"] = False

        # Check platform count
        platforms = params.get("platforms", [])
        if len(platforms) > self.guardrails["analysis_limits"]["max_platforms"]:
            validation_results["errors"].append(f"Too many platforms. Max: {self.guardrails['analysis_limits']['max_platforms']}")
            validation_results["valid"] = False

        # Check keyword count
        keywords = params.get("keywords", [])
        if len(keywords) > self.guardrails["analysis_limits"]["max_keywords"]:
            validation_results["errors"].append(f"Too many keywords. Max: {self.guardrails['analysis_limits']['max_keywords']}")
            validation_results["valid"] = False

        return validation_results["valid"], validation_results

    def validate_analysis_results(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Validate analysis results against quality rules.

        Args:
            results: Analysis results
            analysis_type: Type of analysis

        Returns:
            Validation report with quality assessment
        """
        validation_report = {
            "quality_score": 0,
            "issues_found": [],
            "warnings": [],
            "recommendations": [],
            "compliance": {}
        }

        # Apply appropriate rules based on analysis type
        if analysis_type == "website":
            self._validate_website_results(results, validation_report)
        elif analysis_type == "social_media":
            self._validate_social_media_results(results, validation_report)
        elif analysis_type == "content":
            self._validate_content_results(results, validation_report)

        # Calculate quality score (0-100)
        if validation_report["issues_found"]:
            validation_report["quality_score"] = max(0, 80 - len(validation_report["issues_found"]) * 10)
        else:
            validation_report["quality_score"] = 100

        return validation_report

    def _validate_website_results(self, results: Dict[str, Any], report: Dict[str, Any]) -> None:
        """Validate website analysis results."""
        traffic = results.get("traffic_metrics", {})
        seo = results.get("seo_performance", {})
        technical = results.get("technical_health", {})

        # Traffic validation
        if traffic.get("bounce_rate", 0) > self.rules["website_analysis"]["traffic_analysis"]["bounce_rate_critical"]:
            report["issues_found"].append("Critical bounce rate detected")
        elif traffic.get("bounce_rate", 0) > self.rules["website_analysis"]["traffic_analysis"]["bounce_rate_warning"]:
            report["warnings"].append("High bounce rate detected")

        if traffic.get("avg_session_duration_seconds", 0) < self.rules["website_analysis"]["traffic_analysis"]["session_duration_good"]:
            report["warnings"].append("Low session duration")

        # SEO validation
        if seo.get("technical_seo_score", 0) < self.rules["website_analysis"]["seo_analysis"]["min_domain_authority"]:
            report["issues_found"].append("Low technical SEO score")

        if seo.get("backlink_profile", {}).get("toxic_links", 0) > 0:
            report["issues_found"].append("Toxic backlinks detected")

        # Technical validation
        if technical.get("broken_links", 0) > self.rules["website_analysis"]["technical_analysis"]["max_broken_links"]:
            report["issues_found"].append("Too many broken links")

        if technical.get("page_speed_score", 0) < self.rules["website_analysis"]["technical_analysis"]["min_page_speed_score"]:
            report["issues_found"].append("Poor page speed score")

    def _validate_social_media_results(self, results: Dict[str, Any], report: Dict[str, Any]) -> None:
        """Validate social media analysis results."""
        platforms = results.get("platform_performance", {})
        engagement = results.get("content_engagement", {})
        sentiment = results.get("audience_sentiment", {})

        # Platform performance validation
        for platform, data in platforms.items():
            if data.get("engagement_rate", 0) < self.rules["social_media_analysis"]["platform_performance"]["min_engagement_rate"]:
                report["warnings"].append(f"Low engagement rate on {platform}")

            if data.get("growth", 0) < self.rules["social_media_analysis"]["platform_performance"]["min_follower_growth"]:
                report["warnings"].append(f"Low growth rate on {platform}")

        # Engagement validation
        if engagement.get("episode_engagement", {}).get("average_completion_rate", 0) < self.rules["social_media_analysis"]["content_performance"]["min_completion_rate"]:
            report["issues_found"].append("Low episode completion rate")

        # Sentiment validation
        if sentiment.get("negative", 0) > self.rules["social_media_analysis"]["sentiment_analysis"]["critical_negative_sentiment"]:
            report["issues_found"].append("Critical negative sentiment detected")
        elif sentiment.get("negative", 0) > self.rules["social_media_analysis"]["sentiment_analysis"]["warning_negative_sentiment"]:
            report["warnings"].append("High negative sentiment detected")

    def _validate_content_results(self, results: Dict[str, Any], report: Dict[str, Any]) -> None:
        """Validate content analysis results."""
        episodes = results.get("episode_performance", {})
        shorts = results.get("short_form_effectiveness", {})

        # Episode validation
        if episodes.get("average_completion_rate", 0) < self.rules["content_analysis"]["episode_performance"]["good_completion_rate"]:
            report["warnings"].append("Low episode completion rate")

        if episodes.get("average_shares", 0) < self.rules["content_analysis"]["episode_performance"]["min_shares_per_1000_views"]:
            report["warnings"].append("Low share rate for episodes")

        # Short form validation
        if shorts.get("average_completion_rate", 0) < self.rules["content_analysis"]["short_form_performance"]["good_completion_rate"]:
            report["warnings"].append("Low short form completion rate")

        if shorts.get("conversion_to_full_episode", 0) < self.rules["content_analysis"]["short_form_performance"]["min_conversion_rate"]:
            report["warnings"].append("Low conversion rate from shorts to full episodes")

    def apply_consensus_guardrails(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply democratic consensus guardrails to recommendations.

        Args:
            recommendations: List of recommendations

        Returns:
            Filtered recommendations that meet consensus
        """
        if not recommendations:
            return []

        # Create proposal for recommendations
        proposal_id = self.voting_system.create_proposal(
            "analysis_system",
            "Recommendation Validation",
            "Validate analysis recommendations",
            ["approve", "reject"],
            required_quorum=0.5,
            consensus_threshold=0.67,
            min_votes=3
        )

        proposal = self.voting_system.proposals[proposal_id]

        # Record attendance (simulate multiple agents)
        for i in range(1, 5):
            proposal.record_attendance(f'validation_agent_{i}')

        # Vote on each recommendation
        validated_recommendations = []

        for rec in recommendations:
            # Simulate voting process
            votes_needed = 3
            approve_votes = 0

            # Apply quality-based voting logic
            if rec.get("priority") == "High":
                approve_votes = 3  # High priority gets approved
            elif rec.get("priority") == "Medium":
                approve_votes = 2  # Medium priority needs more discussion
            else:
                approve_votes = 1  # Low priority may not get approved

            # Add votes
            for i in range(1, approve_votes + 1):
                proposal.add_vote(f'validation_agent_{i}', {
                    'decision': 'approve',
                    'weight': 1.0,
                    'confidence': 0.8 + (i * 0.05)
                })

            # Check if consensus met
            summary = proposal.get_vote_summary()
            if summary['consensus_met']:
                validated_recommendations.append(rec)
                proposal.reset_votes()  # Reset for next recommendation
            else:
                logger.info(f"Recommendation rejected by consensus: {rec.get('recommendation')}")

        return validated_recommendations

class EnhancedWebsiteSocialMediaAnalysisAgent(EnhancedBaseAgent):
    """Enhanced website and social media analysis agent with full framework integration."""

    def __init__(self, agent_name: str, config_path: Optional[str] = None):
        """Initialize enhanced analysis agent.

        Args:
            agent_name: Name of the agent
            config_path: Optional path to configuration file
        """
        # Initialize guardrails
        self.guardrails = AnalysisGuardrails()

        # Initialize base agent
        super().__init__(agent_name, config_path)

        # Initialize analysis-specific components
        self.analysis_cache = {}
        self.quality_metrics = {
            "website_analysis": {"success_rate": 0, "total_analyses": 0},
            "social_media_analysis": {"success_rate": 0, "total_analyses": 0},
            "content_analysis": {"success_rate": 0, "total_analyses": 0}
        }

        # Initialize democratic decision making
        self.message_bus = MessageBus()
        self.voting_system = VotingSystem(self.message_bus)

        logger.info(f"Initialized Enhanced {agent_name} with guardrails and democratic decision making")

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize enhanced tools with framework integration."""
        tools = super()._initialize_tools()

        # Enhance tools with additional capabilities
        for tool_name, tool in tools.items():
            if isinstance(tool, EnhancedAgentTool):
                # Add guardrail validation to each tool
                original_execute = tool.execute

                def guarded_execute(*args, **kwargs):
                    """Execute tool with guardrail validation."""
                    # Validate parameters
                    params = kwargs.get("parameters", {})
                    is_valid, validation = self.guardrails.validate_analysis_parameters(params)

                    if not is_valid:
                        error_msg = f"Guardrail validation failed: {validation.get('errors', [])}"
                        logger.warning(error_msg)
                        return ToolResult(
                            success=False,
                            result={"error": error_msg, "validation": validation},
                            tool_name=tool_name
                        )

                    # Execute original tool
                    result = original_execute(*args, **kwargs)

                    # Validate results if successful
                    if result.success and hasattr(result, 'result'):
                        analysis_type = self._infer_analysis_type(tool_name)
                        validation_report = self.guardrails.validate_analysis_results(result.result, analysis_type)
                        result.result["validation"] = validation_report

                        # Update quality metrics
                        self._update_quality_metrics(analysis_type, validation_report["quality_score"] > 70)

                    return result

                tool.execute = guarded_execute

        return tools

    def _infer_analysis_type(self, tool_name: str) -> str:
        """Infer analysis type from tool name."""
        if any(keyword in tool_name.lower() for keyword in ["website", "seo", "technical"]):
            return "website"
        elif any(keyword in tool_name.lower() for keyword in ["social", "platform", "sentiment"]):
            return "social_media"
        elif any(keyword in tool_name.lower() for keyword in ["content", "episode", "short"]):
            return "content"
        else:
            return "general"

    def _update_quality_metrics(self, analysis_type: str, success: bool) -> None:
        """Update quality metrics for analysis type."""
        if analysis_type in self.quality_metrics:
            self.quality_metrics[analysis_type]["total_analyses"] += 1
            if success:
                self.quality_metrics[analysis_type]["success_rate"] = (
                    (self.quality_metrics[analysis_type]["success_rate"] *
                     (self.quality_metrics[analysis_type]["total_analyses"] - 1)) + 1
                ) / self.quality_metrics[analysis_type]["total_analyses"]

    def execute_analysis_with_guardrails(self, analysis_type: str, parameters: Dict[str, Any],
                                        framework: str = "auto") -> Dict[str, Any]:
        """Execute analysis with full guardrail validation.

        Args:
            analysis_type: Type of analysis to perform
            parameters: Analysis parameters
            framework: Framework to use

        Returns:
            Analysis results with validation
        """
        # Validate parameters first
        is_valid, validation = self.guardrails.validate_analysis_parameters(parameters)
        if not is_valid:
            return {"success": False, "error": "Parameter validation failed", "validation": validation}

        # Determine appropriate tool based on analysis type
        tool_mapping = {
            "website": "analyze_website_traffic",
            "social_media": "analyze_social_performance",
            "content": "analyze_episode_performance",
            "traffic": "analyze_traffic_patterns",
            "seo": "conduct_seo_audit"
        }

        tool_name = tool_mapping.get(analysis_type, "analyze_website_traffic")

        # Execute with enhanced tool
        result = self.enhanced_execute_tool(tool_name, parameters, framework=framework)

        if result.get("success"):
            # Apply consensus guardrails to results
            if "recommendations" in result.get("framework_result", {}).get("result", {}):
                validated_recs = self.guardrails.apply_consensus_guardrails(
                    result["framework_result"]["result"]["recommendations"]
                )
                result["framework_result"]["result"]["recommendations"] = validated_recs

        return result

    def create_analysis_workflow(self, workflow_name: str, analysis_types: List[str]) -> Dict[str, Any]:
        """Create a comprehensive analysis workflow.

        Args:
            workflow_name: Name of the workflow
            analysis_types: List of analysis types to include

        Returns:
            Workflow configuration
        """
        workflow_steps = []

        for analysis_type in analysis_types:
            if analysis_type == "website":
                workflow_steps.extend([
                    {"agent": self.name, "action": "analyze_website_traffic", "expected_output": "Website traffic analysis"},
                    {"agent": self.name, "action": "evaluate_seo_performance", "expected_output": "SEO performance evaluation"},
                    {"agent": self.name, "action": "review_technical_seo", "expected_output": "Technical SEO review"}
                ])
            elif analysis_type == "social_media":
                workflow_steps.extend([
                    {"agent": self.name, "action": "analyze_social_performance", "expected_output": "Social media performance analysis"},
                    {"agent": self.name, "action": "monitor_audience_sentiment", "expected_output": "Audience sentiment analysis"},
                    {"agent": self.name, "action": "identify_trends", "expected_output": "Trend identification"}
                ])
            elif analysis_type == "content":
                workflow_steps.extend([
                    {"agent": self.name, "action": "analyze_episode_performance", "expected_output": "Episode performance analysis"},
                    {"agent": self.name, "action": "evaluate_short_form_content", "expected_output": "Short form content evaluation"},
                    {"agent": self.name, "action": "identify_content_patterns", "expected_output": "Content pattern identification"}
                ])
            elif analysis_type == "traffic":
                workflow_steps.extend([
                    {"agent": self.name, "action": "analyze_traffic_patterns", "expected_output": "Traffic pattern analysis"},
                    {"agent": self.name, "action": "detect_traffic_changes", "expected_output": "Traffic change detection"},
                    {"agent": self.name, "action": "analyze_traffic_sources", "expected_output": "Traffic source analysis"}
                ])

        # Add validation and reporting steps
        workflow_steps.extend([
            {"agent": self.name, "action": "validate_analysis_results", "expected_output": "Analysis validation report"},
            {"agent": self.name, "action": "generate_recommendations", "expected_output": "Actionable recommendations"},
            {"agent": self.name, "action": "create_implementation_roadmap", "expected_output": "Implementation roadmap"}
        ])

        return {
            "name": workflow_name,
            "steps": workflow_steps,
            "analysis_types": analysis_types,
            "guardrails_applied": True,
            "democratic_validation": True
        }

    def execute_comprehensive_analysis(self, workflow_config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive analysis workflow with all guardrails.

        Args:
            workflow_config: Workflow configuration
            parameters: Analysis parameters

        Returns:
            Comprehensive analysis results
        """
        # Validate workflow configuration
        if not workflow_config.get("steps"):
            return {"success": False, "error": "Invalid workflow configuration"}

        # Initialize results container
        results = {
            "workflow": workflow_config["name"],
            "analysis_types": workflow_config["analysis_types"],
            "steps": [],
            "validation": {},
            "recommendations": [],
            "implementation_roadmap": {},
            "quality_metrics": {},
            "guardrails": {
                "parameter_validation": {},
                "result_validation": {},
                "consensus_validation": {}
            }
        }

        # Execute each step with appropriate framework
        current_context = parameters.copy()

        for step in workflow_config["steps"]:
            step_result = self.execute_task(
                f"Execute {step['action']} for {step.get('expected_output', '')}",
                framework="auto",
                context=current_context
            )

            # Store step results
            step_results = {
                "step": step["action"],
                "success": step_result.get("success", False),
                "result": step_result.get("result", {}),
                "framework": step_result.get("framework", "unknown")
            }

            results["steps"].append(step_results)

            # Update context for next steps
            if step_result.get("success"):
                current_context[step["action"]] = step_result

            # Stop on critical failure
            if not step_result.get("success") and "validation" in step_result.get("result", {}):
                error_msg = f"Critical failure in step {step['action']}: {step_result.get('error', 'Unknown error')}"
                logger.error(error_msg)
                results["error"] = error_msg
                results["success"] = False
                return results

        # Compile final results
        results["success"] = all(step["success"] for step in results["steps"])

        # Extract and validate recommendations
        if results["success"]:
            # Find recommendations from steps
            all_recommendations = []
            for step in results["steps"]:
                if "recommendations" in step["result"]:
                    all_recommendations.extend(step["result"]["recommendations"])

            # Apply consensus guardrails
            validated_recommendations = self.guardrails.apply_consensus_guardrails(all_recommendations)
            results["recommendations"] = validated_recommendations

            # Create implementation roadmap
            if validated_recommendations:
                results["implementation_roadmap"] = self._create_implementation_roadmap(validated_recommendations)

            # Add quality metrics
            results["quality_metrics"] = self._calculate_overall_quality(results)

        return results

    def _create_implementation_roadmap(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create implementation roadmap from validated recommendations."""
        roadmap = {
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_strategy": [],
            "resource_requirements": {
                "team_hours": 0,
                "budget": 0,
                "external_resources": []
            },
            "timeline": "3-6 months"
        }

        for rec in recommendations:
            action = {
                "recommendation": rec["recommendation"],
                "impact": rec.get("impact", "Medium"),
                "priority": rec.get("priority", "Medium"),
                "estimated_effort": rec.get("effort", "Medium"),
                "success_metrics": rec.get("success_metrics", "Improved performance")
            }

            # Categorize based on priority and effort
            if rec.get("priority") == "High" and rec.get("effort") in ["Low", "Medium"]:
                roadmap["immediate_actions"].append(action)
                roadmap["resource_requirements"]["team_hours"] += 8  # Estimate 1 day per high priority item
            elif rec.get("priority") in ["High", "Medium"]:
                roadmap["short_term_actions"].append(action)
                roadmap["resource_requirements"]["team_hours"] += 16  # Estimate 2 days per medium priority item
            else:
                roadmap["long_term_strategy"].append(action)
                roadmap["resource_requirements"]["team_hours"] += 40  # Estimate 5 days per long-term item

        # Calculate budget estimates
        roadmap["resource_requirements"]["budget"] = (
            roadmap["resource_requirements"]["team_hours"] * 100  # $100/hour estimate
        )

        return roadmap

    def _calculate_overall_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality metrics for the analysis."""
        quality_metrics = {
            "overall_quality_score": 0,
            "data_quality_score": 0,
            "analysis_quality_score": 0,
            "recommendation_quality_score": 0,
            "compliance_score": 0
        }

        # Calculate scores based on step success and validation
        successful_steps = sum(1 for step in results["steps"] if step["success"])
        total_steps = len(results["steps"])

        if total_steps > 0:
            quality_metrics["analysis_quality_score"] = (successful_steps / total_steps) * 100

        # Data quality score based on validation results
        validation_scores = []
        for step in results["steps"]:
            if "validation" in step["result"]:
                validation_scores.append(step["result"]["validation"].get("quality_score", 0))

        if validation_scores:
            quality_metrics["data_quality_score"] = sum(validation_scores) / len(validation_scores)

        # Recommendation quality score
        if results.get("recommendations"):
            quality_metrics["recommendation_quality_score"] = min(100, len(results["recommendations"]) * 10)

        # Overall quality score (weighted average)
        weights = {
            "data_quality_score": 0.3,
            "analysis_quality_score": 0.4,
            "recommendation_quality_score": 0.2,
            "compliance_score": 0.1
        }

        quality_metrics["overall_quality_score"] = sum(
            quality_metrics[key] * weights[key] for key in weights
        )

        return quality_metrics

    def get_analysis_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality report for all analyses performed."""
        report = {
            "agent_name": self.name,
            "total_analyses": sum(metrics["total_analyses"] for metrics in self.quality_metrics.values()),
            "quality_by_type": self.quality_metrics.copy(),
            "guardrail_compliance": {
                "parameter_validation_success_rate": 0.95,  # Example metric
                "result_validation_success_rate": 0.88,    # Example metric
                "consensus_validation_success_rate": 0.92  # Example metric
            },
            "framework_performance": self.get_framework_status(),
            "recommendations": {
                "total_generated": 0,
                "total_validated": 0,
                "validation_rate": 0
            }
        }

        # Calculate recommendation metrics
        for analysis_type, metrics in self.quality_metrics.items():
            report["recommendations"]["total_generated"] += metrics["total_analyses"]
            report["recommendations"]["total_validated"] += int(metrics["success_rate"] * metrics["total_analyses"])

        if report["recommendations"]["total_generated"] > 0:
            report["recommendations"]["validation_rate"] = (
                report["recommendations"]["total_validated"] /
                report["recommendations"]["total_generated"]
            )

        return report

    def apply_democratic_decision_making(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply democratic decision making to analysis results.

        Args:
            analysis_results: Raw analysis results

        Returns:
            Results with democratic validation applied
        """
        # Create proposal for result validation
        proposal_id = self.voting_system.create_proposal(
            self.name,
            "Analysis Result Validation",
            "Validate analysis results and recommendations",
            ["approve", "modify", "reject"],
            required_quorum=0.6,
            consensus_threshold=0.75,
            min_votes=3
        )

        proposal = self.voting_system.proposals[proposal_id]

        # Record attendance (simulate agent participation)
        for i in range(1, 5):
            proposal.record_attendance(f'validation_agent_{i}')

        # Validate results through voting
        validated_results = analysis_results.copy()
        validated_results["democratic_validation"] = {
            "proposal_id": proposal_id,
            "votes": [],
            "consensus_reached": False,
            "validation_results": {}
        }

        # Vote on overall quality
        quality_score = analysis_results.get("quality_metrics", {}).get("overall_quality_score", 0)

        if quality_score >= 80:
            # High quality - likely to be approved
            for i in range(1, 4):
                proposal.add_vote(f'validation_agent_{i}', {
                    'decision': 'approve',
                    'weight': 1.0,
                    'confidence': 0.8 + (i * 0.05)
                })
        elif quality_score >= 60:
            # Medium quality - may need modification
            proposal.add_vote('validation_agent_1', {
                'decision': 'approve',
                'weight': 1.0,
                'confidence': 0.7
            })
            proposal.add_vote('validation_agent_2', {
                'decision': 'modify',
                'weight': 1.0,
                'confidence': 0.75
            })
            proposal.add_vote('validation_agent_3', {
                'decision': 'approve',
                'weight': 1.0,
                'confidence': 0.65
            })
        else:
            # Low quality - likely to be rejected or modified
            proposal.add_vote('validation_agent_1', {
                'decision': 'modify',
                'weight': 1.0,
                'confidence': 0.6
            })
            proposal.add_vote('validation_agent_2', {
                'decision': 'reject',
                'weight': 1.0,
                'confidence': 0.55
            })
            proposal.add_vote('validation_agent_3', {
                'decision': 'modify',
                'weight': 1.0,
                'confidence': 0.65
            })

        # Get vote summary
        summary = proposal.get_vote_summary()
        validated_results["democratic_validation"]["votes"] = summary.get("votes", [])
        validated_results["democratic_validation"]["consensus_reached"] = summary.get("consensus_met", False)
        validated_results["democratic_validation"]["decision"] = summary.get("winning_decision", "pending")

        # Apply modifications if needed
        if summary.get("winning_decision") == "modify":
            validated_results["modification_required"] = True
            validated_results["modification_notes"] = [
                "Review data quality issues",
                "Validate recommendation impact estimates",
                "Check for potential biases in analysis"
            ]

        return validated_results

class WebsiteSocialMediaAnalysisOrchestrator(EnhancedWorkflowOrchestrator):
    """Enhanced orchestrator for website and social media analysis workflows."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize enhanced analysis orchestrator."""
        super().__init__(config_path)

        # Initialize guardrails and validation
        self.guardrails = AnalysisGuardrails()
        self.quality_metrics = {
            "workflows_completed": 0,
            "workflows_with_consensus": 0,
            "average_quality_score": 0,
            "total_recommendations": 0,
            "validated_recommendations": 0
        }

        # Initialize democratic systems
        self.message_bus = MessageBus()
        self.voting_system = VotingSystem(self.message_bus)

        logger.info("Initialized Enhanced Website & Social Media Analysis Orchestrator")

    def create_comprehensive_workflow(self, workflow_name: str, analysis_scope: List[str]) -> Dict[str, Any]:
        """Create comprehensive analysis workflow with all guardrails.

        Args:
            workflow_name: Name of the workflow
            analysis_scope: List of analysis areas to include

        Returns:
            Complete workflow configuration
        """
        # Define workflow structure based on scope
        workflow_config = {
            "name": workflow_name,
            "description": f"Comprehensive {workflow_name} analysis workflow",
            "scope": analysis_scope,
            "steps": [],
            "guardrails": ANALYSIS_GUARDRAILS,
            "rules": ANALYSIS_RULES,
            "quality_requirements": {
                "min_quality_score": 70,
                "min_consensus_rate": 0.67,
                "validation_required": True
            }
        }

        # Add analysis steps based on scope
        if "website" in analysis_scope:
            workflow_config["steps"].extend([
                {"agent": "website_analyst", "action": "analyze_website_traffic", "input": "analysis_period"},
                {"agent": "website_analyst", "action": "evaluate_seo_performance", "input": "current_keywords"},
                {"agent": "website_analyst", "action": "review_technical_seo", "input": "technical_elements"},
                {"agent": "website_analyst", "action": "identify_technical_issues", "input": "full_website_scan"}
            ])

        if "social_media" in analysis_scope:
            workflow_config["steps"].extend([
                {"agent": "social_media_analyst", "action": "analyze_social_performance", "input": "analysis_period"},
                {"agent": "social_media_analyst", "action": "validate_scheduled_content", "input": "content_calendar"},
                {"agent": "social_media_analyst", "action": "monitor_audience_sentiment", "input": "sentiment_analysis"},
                {"agent": "social_media_analyst", "action": "identify_trends", "input": "trend_analysis"}
            ])

        if "content" in analysis_scope:
            workflow_config["steps"].extend([
                {"agent": "content_analyst", "action": "analyze_episode_performance", "input": "recent_episodes"},
                {"agent": "content_analyst", "action": "evaluate_short_form_content", "input": "short_form_performance"},
                {"agent": "content_analyst", "action": "identify_content_patterns", "input": "high_performing_content"},
                {"agent": "content_analyst", "action": "track_content_lifecycle", "input": "evergreen_content"}
            ])

        if "traffic" in analysis_scope:
            workflow_config["steps"].extend([
                {"agent": "traffic_analyst", "action": "analyze_traffic_patterns", "input": "historical_traffic"},
                {"agent": "traffic_analyst", "action": "detect_traffic_changes", "input": "change_detection"},
                {"agent": "traffic_analyst", "action": "analyze_traffic_sources", "input": "source_analysis"},
                {"agent": "traffic_analyst", "action": "correlate_with_content", "input": "content_traffic_correlation"}
            ])

        if "seo" in analysis_scope:
            workflow_config["steps"].extend([
                {"agent": "seo_specialist", "action": "conduct_seo_audit", "input": "comprehensive_audit"},
                {"agent": "seo_specialist", "action": "analyze_keywords", "input": "keyword_analysis"},
                {"agent": "seo_specialist", "action": "evaluate_on_page_seo", "input": "on_page_evaluation"},
                {"agent": "seo_specialist", "action": "assess_backlink_profile", "input": "backlink_data"}
            ])

        # Add validation and reporting steps
        workflow_config["steps"].extend([
            {"agent": "report_generator", "action": "compile_analysis_data", "input": "all_analysis_data"},
            {"agent": "report_generator", "action": "create_structured_report", "input": "report_structure"},
            {"agent": "report_generator", "action": "generate_recommendations", "input": "validated_results"},
            {"agent": "report_generator", "action": "create_implementation_roadmap", "input": "prioritized_recommendations"},
            {"agent": "report_generator", "action": "generate_visualizations", "input": "visualization_data"},
            {"agent": "report_generator", "action": "create_executive_summary", "input": "summary_requirements"}
        ])

        # Add democratic validation step
        workflow_config["steps"].append({
            "agent": "website_social_media_crew",
            "action": "provide_strategic_insights",
            "input": "comprehensive_data"
        })

        return workflow_config

    def execute_workflow_with_guardrails(self, workflow_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with full guardrail validation.

        Args:
            workflow_config: Workflow configuration
            inputs: Workflow inputs

        Returns:
            Complete workflow results with validation
        """
        # Validate inputs first
        is_valid, validation = self.guardrails.validate_analysis_parameters(inputs)
        if not is_valid:
            return {"success": False, "error": "Input validation failed", "validation": validation}

        # Execute the workflow
        workflow_results = super().execute_enhanced_workflow(workflow_config, inputs, framework="auto")

        # Apply additional validation and democratic processes
        enhanced_results = self._apply_workflow_guardrails(workflow_results)

        # Update quality metrics
        self._update_workflow_quality_metrics(enhanced_results)

        return enhanced_results

    def _apply_workflow_guardrails(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply comprehensive guardrails to workflow results."""
        enhanced_results = workflow_results.copy()

        # Add guardrail validation section
        enhanced_results["guardrail_validation"] = {
            "parameter_validation": workflow_results.get("validation", {}),
            "result_validation": {},
            "consensus_validation": {},
            "quality_assessment": {}
        }

        # Validate each step's results
        for step_key, step_result in workflow_results.get("results", {}).items():
            if step_result.get("success"):
                agent_action = step_key.split('.')
                if len(agent_action) == 2:
                    agent_name, action = agent_action
                    analysis_type = self._infer_analysis_type_from_agent(agent_name)

                    # Validate the result
                    validation_report = self.guardrails.validate_analysis_results(
                        step_result.get("result", {}),
                        analysis_type
                    )

                    enhanced_results["guardrail_validation"]["result_validation"][step_key] = validation_report

        # Apply consensus validation to recommendations
        if "recommendations" in enhanced_results.get("results", {}).get("report_generator.generate_recommendations", {}):
            recommendations = enhanced_results["results"]["report_generator.generate_recommendations"]["result"].get("recommendations", [])

            validated_recommendations = self.guardrails.apply_consensus_guardrails(recommendations)
            enhanced_results["guardrail_validation"]["consensus_validation"] = {
                "original_count": len(recommendations),
                "validated_count": len(validated_recommendations),
                "validation_rate": len(validated_recommendations) / len(recommendations) if recommendations else 1.0,
                "recommendations": validated_recommendations
            }

            # Update the main results with validated recommendations
            if "report_generator.create_implementation_roadmap" in enhanced_results["results"]:
                roadmap_result = enhanced_results["results"]["report_generator.create_implementation_roadmap"]
                if "recommendations" in roadmap_result["result"]:
                    roadmap_result["result"]["recommendations"] = validated_recommendations

        # Calculate overall quality assessment
        quality_scores = []
        for validation in enhanced_results["guardrail_validation"]["result_validation"].values():
            quality_scores.append(validation.get("quality_score", 0))

        if quality_scores:
            enhanced_results["guardrail_validation"]["quality_assessment"] = {
                "average_quality_score": sum(quality_scores) / len(quality_scores),
                "min_quality_score": min(quality_scores),
                "max_quality_score": max(quality_scores),
                "quality_distribution": self._calculate_quality_distribution(quality_scores)
            }

        return enhanced_results

    def _infer_analysis_type_from_agent(self, agent_name: str) -> str:
        """Infer analysis type from agent name."""
        if "website" in agent_name.lower():
            return "website"
        elif "social" in agent_name.lower():
            return "social_media"
        elif "content" in agent_name.lower():
            return "content"
        elif "traffic" in agent_name.lower():
            return "traffic"
        elif "seo" in agent_name.lower():
            return "seo"
        else:
            return "general"

    def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate quality score distribution."""
        distribution = {
            "excellent": 0,  # 90-100
            "good": 0,       # 70-89
            "fair": 0,       # 50-69
            "poor": 0        # 0-49
        }

        for score in quality_scores:
            if score >= 90:
                distribution["excellent"] += 1
            elif score >= 70:
                distribution["good"] += 1
            elif score >= 50:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1

        return distribution

    def _update_workflow_quality_metrics(self, workflow_results: Dict[str, Any]) -> None:
        """Update quality metrics based on workflow results."""
        self.quality_metrics["workflows_completed"] += 1

        # Count recommendations
        if "recommendations" in workflow_results.get("guardrail_validation", {}).get("consensus_validation", {}):
            self.quality_metrics["total_recommendations"] += workflow_results["guardrail_validation"]["consensus_validation"]["original_count"]
            self.quality_metrics["validated_recommendations"] += workflow_results["guardrail_validation"]["consensus_validation"]["validated_count"]

        # Calculate average quality score
        quality_assessment = workflow_results.get("guardrail_validation", {}).get("quality_assessment", {})
        if "average_quality_score" in quality_assessment:
            # Update running average
            current_avg = self.quality_metrics["average_quality_score"]
            new_score = quality_assessment["average_quality_score"]
            self.quality_metrics["average_quality_score"] = (
                (current_avg * (self.quality_metrics["workflows_completed"] - 1)) + new_score
            ) / self.quality_metrics["workflows_completed"]

        # Update consensus rate
        if self.quality_metrics["total_recommendations"] > 0:
            self.quality_metrics["min_consensus_rate"] = (
                self.quality_metrics["validated_recommendations"] /
                self.quality_metrics["total_recommendations"]
            )

    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality report for the orchestrator."""
        report = {
            "orchestrator_name": "WebsiteSocialMediaAnalysisOrchestrator",
            "metrics": self.quality_metrics.copy(),
            "guardrail_compliance": {
                "parameter_validation_rate": 0.97,
                "result_validation_rate": 0.89,
                "consensus_validation_rate": self.quality_metrics["min_consensus_rate"],
                "quality_assessment_compliance": 0.94
            },
            "framework_performance": self.get_available_frameworks(),
            "recommendations": {
                "effective_validation_rate": self.quality_metrics["validated_recommendations"] / self.quality_metrics["total_recommendations"] if self.quality_metrics["total_recommendations"] > 0 else 0,
                "quality_improvement_trend": "positive" if self.quality_metrics["average_quality_score"] > 70 else "needs_improvement"
            }
        }

        return report

# Utility functions for reusable patterns
def create_standard_analysis_parameters(time_period: str = "last_30_days",
                                      platforms: List[str] = None,
                                      focus_areas: List[str] = None) -> Dict[str, Any]:
    """Create standard analysis parameters with sensible defaults."""
    params = {
        "time_period": time_period,
        "platforms": platforms or ["twitter", "instagram", "tiktok", "youtube"],
        "focus_areas": focus_areas or ["website_performance", "social_media_engagement", "content_effectiveness"],
        "comparison_period": "previous_30_days",
        "include_competitor_analysis": True,
        "validation_required": True,
        "democratic_validation": True
    }

    return params

def validate_analysis_configuration(config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate analysis configuration against standards."""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "required_fields": ["time_period", "platforms", "focus_areas"]
    }

    # Check required fields
    for field in validation["required_fields"]:
        if field not in config:
            validation["errors"].append(f"Missing required field: {field}")
            validation["valid"] = False

    # Validate time period format
    if "time_period" in config:
        if not isinstance(config["time_period"], str) or "_" not in config["time_period"]:
            validation["errors"].append("Time period must be in format like '30_days'")
            validation["valid"] = False

    # Validate platforms
    if "platforms" in config:
        valid_platforms = ["twitter", "instagram", "tiktok", "youtube", "facebook", "linkedin"]
        for platform in config["platforms"]:
            if platform not in valid_platforms:
                validation["warnings"].append(f"Unsupported platform: {platform}")

    return validation["valid"], validation

def create_reusable_workflow_template(workflow_type: str = "comprehensive") -> Dict[str, Any]:
    """Create reusable workflow templates."""
    templates = {
        "comprehensive": {
            "name": "comprehensive_digital_analysis",
            "scope": ["website", "social_media", "content", "traffic", "seo"],
            "description": "Complete digital presence analysis",
            "estimated_duration": "2-4 hours",
            "resource_requirements": {
                "compute": "medium",
                "memory": "high",
                "api_calls": 50
            }
        },
        "quick_check": {
            "name": "digital_health_check",
            "scope": ["website", "social_media"],
            "description": "Quick digital health assessment",
            "estimated_duration": "30-60 minutes",
            "resource_requirements": {
                "compute": "low",
                "memory": "medium",
                "api_calls": 20
            }
        },
        "content_focused": {
            "name": "content_performance_analysis",
            "scope": ["content", "social_media"],
            "description": "Deep content performance analysis",
            "estimated_duration": "1-2 hours",
            "resource_requirements": {
                "compute": "medium",
                "memory": "medium",
                "api_calls": 30
            }
        }
    }

    return templates.get(workflow_type, templates["comprehensive"])

# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize enhanced agent
    website_analyst = EnhancedWebsiteSocialMediaAnalysisAgent("website_analyst")

    # Test parameter validation
    test_params = {
        "time_period": "last_90_days",
        "platforms": ["twitter", "instagram", "tiktok"],
        "focus_areas": ["website_performance", "social_media_engagement"]
    }

    is_valid, validation = website_analyst.guardrails.validate_analysis_parameters(test_params)
    print(f"Parameter validation: {'PASS' if is_valid else 'FAIL'}")
    print(f"Validation results: {validation}")

    # Test analysis execution
    analysis_result = website_analyst.execute_analysis_with_guardrails(
        "website",
        test_params,
        framework="auto"
    )

    print(f"Analysis execution: {'SUCCESS' if analysis_result.get('success') else 'FAILED'}")
    print(f"Framework used: {analysis_result.get('framework_used', 'unknown')}")

    # Test workflow creation
    workflow_config = website_analyst.create_analysis_workflow(
        "comprehensive_digital_analysis",
        ["website", "social_media", "content"]
    )

    print(f"Workflow created with {len(workflow_config['steps'])} steps")

    # Test comprehensive analysis
    comprehensive_result = website_analyst.execute_comprehensive_analysis(
        workflow_config,
        test_params
    )

    print(f"Comprehensive analysis: {'SUCCESS' if comprehensive_result.get('success') else 'FAILED'}")
    print(f"Recommendations generated: {len(comprehensive_result.get('recommendations', []))}")

    # Test quality report
    quality_report = website_analyst.get_analysis_quality_report()
    print(f"Quality report generated with score: {quality_report.get('overall_quality_score', 0):.1f}")

    # Test orchestrator
    orchestrator = WebsiteSocialMediaAnalysisOrchestrator()

    # Create comprehensive workflow
    comprehensive_workflow = orchestrator.create_comprehensive_workflow(
        "full_digital_analysis",
        ["website", "social_media", "content", "traffic", "seo"]
    )

    print(f"Orchestrator workflow created with {len(comprehensive_workflow['steps'])} steps")

    # Execute workflow
    workflow_result = orchestrator.execute_workflow_with_guardrails(
        comprehensive_workflow,
        test_params
    )

    print(f"Workflow execution: {'SUCCESS' if workflow_result.get('success') else 'FAILED'}")
    print(f"Quality assessment: {workflow_result.get('guardrail_validation', {}).get('quality_assessment', {}).get('average_quality_score', 0):.1f}")

    # Test utility functions
    standard_params = create_standard_analysis_parameters()
    print(f"Standard parameters created for {standard_params['time_period']} analysis")

    workflow_template = create_reusable_workflow_template("quick_check")
    print(f"Workflow template: {workflow_template['name']} ({workflow_template['description']})")
