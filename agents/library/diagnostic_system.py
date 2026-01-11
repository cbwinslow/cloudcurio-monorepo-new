#!/usr/bin/env python3
"""
Swarm Diagnostic System

This module provides comprehensive diagnostic capabilities for the Pydantic AI Swarm.
It monitors system health, detects issues, and provides automated remediation suggestions.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from agents.pydantic_ai_swarm_orchestrator import PydanticAISwarmOrchestrator


@dataclass
class DiagnosticIssue:
    """Represents a diagnostic issue found in the swarm."""
    title: str
    description: str
    severity: str  # "critical", "high", "medium", "low", "info"
    category: str  # "performance", "health", "configuration", "agent", "task"
    solutions: List[Dict[str, Any]] = None
    detected_at: datetime = None
    resolved: bool = False

    def __post_init__(self):
        if self.solutions is None:
            self.solutions = []
        if self.detected_at is None:
            self.detected_at = datetime.now()


class SwarmDiagnosticSystem:
    """
    Comprehensive diagnostic system for swarm monitoring and issue detection.

    This system continuously monitors swarm health, detects issues, and provides
    automated remediation suggestions to maintain optimal swarm performance.
    """

    def __init__(self, swarm: "PydanticAISwarmOrchestrator"):
        self.swarm = swarm
        self.logger = logging.getLogger(f"DiagnosticSystem.{swarm.swarm_name}")

        # Diagnostic state
        self.is_monitoring = False
        self.issues: List[DiagnosticIssue] = []
        self.last_health_check = None
        self.monitoring_task: Optional[asyncio.Task] = None

        # Configuration
        self.health_check_interval = 30  # seconds
        self.issue_retention_days = 7

    async def start_monitoring(self) -> bool:
        """Start the diagnostic monitoring system."""
        if self.is_monitoring:
            self.logger.warning("Diagnostic monitoring already running")
            return True

        try:
            self.logger.info("Starting diagnostic monitoring system")
            self.is_monitoring = True

            # Start background monitoring
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

            # Perform initial health check
            await self._perform_health_check()

            self.logger.info("Diagnostic monitoring system started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start diagnostic monitoring: {e}")
            self.is_monitoring = False
            return False

    async def stop_monitoring(self) -> bool:
        """Stop the diagnostic monitoring system."""
        if not self.is_monitoring:
            return True

        try:
            self.logger.info("Stopping diagnostic monitoring system")
            self.is_monitoring = False

            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass

            self.logger.info("Diagnostic monitoring system stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop diagnostic monitoring: {e}")
            return False

    async def run_diagnostics(self) -> List[DiagnosticIssue]:
        """
        Run comprehensive diagnostic checks and return current issues.

        Returns:
            List of current diagnostic issues
        """
        try:
            self.logger.info("Running comprehensive diagnostic checks")

            issues = []

            # Agent health checks
            agent_issues = await self._check_agent_health()
            issues.extend(agent_issues)

            # Performance checks
            performance_issues = await self._check_performance()
            issues.extend(performance_issues)

            # Configuration checks
            config_issues = await self._check_configuration()
            issues.extend(config_issues)

            # Task processing checks
            task_issues = await self._check_task_processing()
            issues.extend(task_issues)

            # Resource checks
            resource_issues = await self._check_resources()
            issues.extend(resource_issues)

            # Update issues list
            self._update_issues_list(issues)

            self.logger.info(f"Diagnostic checks completed - found {len(issues)} issues")
            return self.issues.copy()

        except Exception as e:
            self.logger.error(f"Diagnostic checks failed: {e}")
            return []

    async def _check_agent_health(self) -> List[DiagnosticIssue]:
        """Check health of all registered agents."""
        issues = []

        for agent_name, agent in self.swarm.agents.items():
            try:
                # Get agent status
                status = await agent.get_status_async()

                # Check if agent is active
                if not getattr(agent, 'is_active', True):
                    issues.append(DiagnosticIssue(
                        title=f"Agent {agent_name} is inactive",
                        description=f"Agent {agent_name} is not responding or has stopped",
                        severity="high",
                        category="agent",
                        solutions=[
                            {
                                "description": "Restart the agent",
                                "automated": True,
                                "action": "restart_agent",
                                "target": agent_name
                            }
                        ]
                    ))

                # Check confidence levels
                confidence = status.get("confidence", {}).get("overall", 1.0)
                if confidence < 0.3:
                    issues.append(DiagnosticIssue(
                        title=f"Low confidence for agent {agent_name}",
                        description=f"Agent {agent_name} has low confidence score ({confidence:.2f})",
                        severity="medium",
                        category="agent",
                        solutions=[
                            {
                                "description": "Review agent configuration and recent tasks",
                                "automated": False
                            }
                        ]
                    ))

            except Exception as e:
                issues.append(DiagnosticIssue(
                    title=f"Agent {agent_name} health check failed",
                    description=f"Failed to get status for agent {agent_name}: {str(e)}",
                    severity="high",
                    category="agent"
                ))

        # Check agent count
        if len(self.swarm.agents) < 2:
            issues.append(DiagnosticIssue(
                title="Low agent count",
                description=f"Swarm only has {len(self.swarm.agents)} agents - recommended minimum is 3",
                severity="medium",
                category="configuration",
                solutions=[
                    {
                        "description": "Register additional specialized agents",
                        "automated": False
                    }
                ]
            ))

        return issues

    async def _check_performance(self) -> List[DiagnosticIssue]:
        """Check swarm performance metrics."""
        issues = []

        # Check task success rate
        total_tasks = self.swarm.metrics["total_tasks_processed"]
        if total_tasks > 0:
            success_rate = self.swarm.metrics["successful_tasks"] / total_tasks
            if success_rate < 0.7:
                severity = "critical" if success_rate < 0.5 else "high"
                issues.append(DiagnosticIssue(
                    title="Low task success rate",
                    description=".1f",
                    severity=severity,
                    category="performance",
                    solutions=[
                        {
                            "description": "Review agent task assignments and error patterns",
                            "automated": False
                        },
                        {
                            "description": "Check agent configurations and capabilities",
                            "automated": False
                        }
                    ]
                ))

        # Check average response time
        avg_time = self.swarm.metrics["average_execution_time"]
        if avg_time > 60:  # More than 1 minute
            issues.append(DiagnosticIssue(
                title="High average task execution time",
                description=".1f",
                severity="medium",
                category="performance",
                solutions=[
                    {
                        "description": "Optimize agent execution logic",
                        "automated": False
                    },
                    {
                        "description": "Review task complexity and agent assignments",
                        "automated": False
                    }
                ]
            ))

        return issues

    async def _check_configuration(self) -> List[DiagnosticIssue]:
        """Check swarm configuration for issues."""
        issues = []

        # Check if efficiency enforcer is active
        if not self.swarm.efficiency_enforcer:
            issues.append(DiagnosticIssue(
                title="Efficiency enforcer not active",
                description="Swarm efficiency rules are not being enforced",
                severity="medium",
                category="configuration",
                solutions=[
                    {
                        "description": "Initialize efficiency enforcer",
                        "automated": True,
                        "action": "init_efficiency_enforcer"
                    }
                ]
            ))

        # Check monitoring settings
        if not self.swarm.enable_monitoring:
            issues.append(DiagnosticIssue(
                title="Monitoring disabled",
                description="Swarm performance monitoring is disabled",
                severity="low",
                category="configuration",
                solutions=[
                    {
                        "description": "Enable monitoring for better observability",
                        "automated": False
                    }
                ]
            ))

        return issues

    async def _check_task_processing(self) -> List[DiagnosticIssue]:
        """Check task processing health."""
        issues = []

        # Check for stuck tasks (no recent completions)
        last_completion_time = getattr(self.swarm, '_last_task_completion', time.time())
        time_since_last_task = time.time() - last_completion_time

        if time_since_last_task > 300 and self.swarm.is_active:  # 5 minutes
            issues.append(DiagnosticIssue(
                title="No recent task completions",
                description=".0f",
                severity="medium",
                category="task",
                solutions=[
                    {
                        "description": "Check agent health and task assignments",
                        "automated": False
                    },
                    {
                        "description": "Review task queue and agent availability",
                        "automated": True,
                        "action": "check_task_queue"
                    }
                ]
            ))

        # Check task queue size
        queue_size = self.swarm.task_queue.qsize()
        if queue_size > 10:
            issues.append(DiagnosticIssue(
                title="Large task queue",
                description=f"Task queue has {queue_size} pending tasks",
                severity="medium",
                category="task",
                solutions=[
                    {
                        "description": "Add more agents or optimize task processing",
                        "automated": False
                    }
                ]
            ))

        return issues

    async def _check_resources(self) -> List[DiagnosticIssue]:
        """Check system resource usage."""
        issues = []

        # Check memory usage (if available)
        peak_memory = self.swarm.metrics.get("peak_memory_usage_mb", 0)
        if peak_memory > 500:  # Over 500MB
            issues.append(DiagnosticIssue(
                title="High memory usage",
                description=f"Peak memory usage: {peak_memory} MB",
                severity="low",
                category="performance",
                solutions=[
                    {
                        "description": "Monitor memory usage patterns",
                        "automated": False
                    },
                    {
                        "description": "Consider optimizing data structures",
                        "automated": False
                    }
                ]
            ))

        # Check uptime
        if self.swarm.start_time:
            uptime_hours = (time.time() - self.swarm.start_time) / 3600
            if uptime_hours > 24:  # Over 24 hours
                issues.append(DiagnosticIssue(
                    title="Long uptime",
                    description=".1f",
                    severity="info",
                    category="performance",
                    solutions=[
                        {
                            "description": "Consider periodic restarts for maintenance",
                            "automated": False
                        }
                    ]
                ))

        return issues

    def _update_issues_list(self, new_issues: List[DiagnosticIssue]):
        """Update the issues list with new findings."""
        # Mark existing issues as resolved if not in new list
        existing_titles = {issue.title for issue in new_issues}
        for issue in self.issues:
            if issue.title not in existing_titles and not issue.resolved:
                issue.resolved = True

        # Add new issues
        for issue in new_issues:
            # Check if this issue already exists
            existing = next((i for i in self.issues if i.title == issue.title), None)
            if existing:
                # Update existing issue
                existing.description = issue.description
                existing.severity = issue.severity
                existing.solutions = issue.solutions
                existing.resolved = False
            else:
                # Add new issue
                self.issues.append(issue)

        # Clean up old resolved issues
        cutoff_time = datetime.now().timestamp() - (self.issue_retention_days * 24 * 60 * 60)
        self.issues = [
            issue for issue in self.issues
            if not issue.resolved or issue.detected_at.timestamp() > cutoff_time
        ]

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Wait for next check interval
                await asyncio.sleep(self.health_check_interval)

                # Perform health check
                await self._perform_health_check()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")

    async def _perform_health_check(self):
        """Perform a health check and update status."""
        try:
            # Run diagnostics
            issues = await self.run_diagnostics()

            # Get current health
            health = await self.swarm.analyze_swarm_health()

            # Log critical issues
            critical_issues = [i for i in issues if i.severity == "critical"]
            if critical_issues:
                for issue in critical_issues:
                    self.logger.error(f"CRITICAL: {issue.title} - {issue.description}")

            # Log high severity issues
            high_issues = [i for i in issues if i.severity == "high"]
            if high_issues:
                for issue in high_issues:
                    self.logger.warning(f"HIGH: {issue.title} - {issue.description}")

            self.last_health_check = time.time()

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Get a summary of diagnostic status."""
        active_issues = [i for i in self.issues if not i.resolved]

        return {
            "total_issues": len(self.issues),
            "active_issues": len(active_issues),
            "resolved_issues": len(self.issues) - len(active_issues),
            "critical_issues": len([i for i in active_issues if i.severity == "critical"]),
            "high_issues": len([i for i in active_issues if i.severity == "high"]),
            "last_health_check": self.last_health_check,
            "monitoring_active": self.is_monitoring,
            "issues_by_category": self._issues_by_category(active_issues)
        }

    def _issues_by_category(self, issues: List[DiagnosticIssue]) -> Dict[str, int]:
        """Group issues by category."""
        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        return categories

    async def resolve_issue(self, issue_title: str) -> bool:
        """Mark an issue as resolved."""
        for issue in self.issues:
            if issue.title == issue_title:
                issue.resolved = True
                self.logger.info(f"Marked issue as resolved: {issue_title}")
                return True
        return False

    def get_issues_by_severity(self, severity: str) -> List[DiagnosticIssue]:
        """Get all issues of a specific severity."""
        return [
            issue for issue in self.issues
            if issue.severity == severity and not issue.resolved
        ]

    def get_unresolved_issues(self) -> List[DiagnosticIssue]:
        """Get all unresolved issues."""
        return [issue for issue in self.issues if not issue.resolved]
