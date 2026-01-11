#!/usr/bin/env python3
"""
Pydantic AI Democratic Swarm Orchestrator

The central coordinator for the Pydantic AI Democratic Agent Swarm system.
This orchestrator manages agent registration, task assignment, democratic voting,
health monitoring, and enforces efficiency rules to prevent duplication.

Key Features:
- Democratic task assignment with agent voting
- Confidence-based decision making
- Real-time health monitoring and diagnostics
- Efficiency enforcement to prevent duplication
- Fault tolerance and automatic recovery
- Performance tracking and analytics
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from agents.diagnostic_system import SwarmDiagnosticSystem

from agents.base_agent import BaseAgent
from agents.efficiency_enforcer import (
    EfficiencyEnforcer,
    SwarmAction,
    get_efficiency_enforcer,
    integrate_with_swarm,
)
from agents.swarm_communication import SwarmCommunication
from agents.swarm_monitoring import SwarmMonitoring


@dataclass
class TaskResult:
    """Result of a swarm task execution."""
    success: bool
    agent_name: str = ""
    data: Any = None
    error: str = ""
    execution_time: float = 0.0
    confidence_score: float = 0.0
    consensus_level: float = 0.0


@dataclass
class SwarmHealth:
    """Swarm health status."""
    overall_health_score: float = 0.0
    agent_health: Dict[str, float] = field(default_factory=dict)
    task_success_rate: float = 0.0
    average_response_time: float = 0.0
    critical_issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    health_status: str = "unknown"
    detailed_analysis: Dict[str, Any] = field(default_factory=dict)


class PydanticAISwarmOrchestrator:
    """
    Enterprise-grade democratic AI agent swarm orchestrator.

    This orchestrator manages a swarm of specialized AI agents that work together
    democratically to accomplish complex tasks. Key features include:

    - Democratic task assignment with agent voting
    - Confidence-based decision making
    - Efficiency enforcement to prevent duplication
    - Real-time health monitoring and diagnostics
    - Fault tolerance and automatic recovery
    - Performance tracking and analytics
    """

    def __init__(
        self,
        swarm_name: str,
        enable_diagnostics: bool = True,
        enable_monitoring: bool = True,
        enable_benchmarking: bool = False,
        voting_timeout_seconds: int = 300,
        max_concurrent_tasks: int = 10
    ):
        """
        Initialize the swarm orchestrator.

        Args:
            swarm_name: Unique name for this swarm
            enable_diagnostics: Enable diagnostic monitoring
            enable_monitoring: Enable performance monitoring
            enable_benchmarking: Enable detailed benchmarking
            voting_timeout_seconds: Timeout for democratic voting
            max_concurrent_tasks: Maximum concurrent tasks
        """
        self.swarm_name = swarm_name
        self.enable_diagnostics = enable_diagnostics
        self.enable_monitoring = enable_monitoring
        self.enable_benchmarking = enable_benchmarking
        self.voting_timeout_seconds = voting_timeout_seconds
        self.max_concurrent_tasks = max_concurrent_tasks

        # Core components
        self.agents: Dict[str, BaseAgent] = {}
        self.active_tasks: Set[str] = set()
        self.task_queue: asyncio.Queue = asyncio.Queue()

        # Communication and monitoring
        self.communication = SwarmCommunication(swarm_name)
        self.monitoring = SwarmMonitoring() if enable_monitoring else None
        self.diagnostics = SwarmDiagnosticSystem(self) if enable_diagnostics else None

        # Efficiency enforcement
        self.efficiency_enforcer: Optional[EfficiencyEnforcer] = None

        # State tracking
        self.is_active = False
        self.start_time = None
        self.task_history: List[Dict[str, Any]] = []

        # Performance metrics
        self.metrics = {
            "total_tasks_processed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "peak_memory_usage_mb": 0.0,
            "recent_errors": [],
        }

        # Setup logging
        self.logger = logging.getLogger(f"SwarmOrchestrator.{swarm_name}")
        self.logger.setLevel(logging.INFO)

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()

    async def start_swarm(self) -> bool:
        """
        Start the swarm orchestrator and all registered agents.

        Returns:
            bool: True if swarm started successfully
        """
        try:
            self.logger.info(f"Starting swarm '{self.swarm_name}'")

            if not self.agents:
                self.logger.warning("No agents registered - starting with empty swarm")
                return False

            # Initialize efficiency enforcer
            if self.efficiency_enforcer is None:
                self.efficiency_enforcer = await integrate_with_swarm(self)

            # Start all agents
            start_tasks = []
            for agent in self.agents.values():
                start_tasks.append(agent.start())

            # Wait for all agents to start
            await asyncio.gather(*start_tasks, return_exceptions=True)

            # Start background tasks
            self._start_background_tasks()

            # Mark as active
            self.is_active = True
            self.start_time = time.time()

            # Start monitoring and diagnostics
            if self.monitoring:
                await self.monitoring.start_monitoring()
            if self.diagnostics:
                await self.diagnostics.start_monitoring()

            self.logger.info(f"Swarm '{self.swarm_name}' started successfully with {len(self.agents)} agents")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start swarm: {e}")
            await self._cleanup_failed_start()
            return False

    async def stop_swarm(self) -> bool:
        """
        Stop the swarm orchestrator and all agents.

        Returns:
            bool: True if swarm stopped successfully
        """
        try:
            self.logger.info(f"Stopping swarm '{self.swarm_name}'")

            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            self._background_tasks.clear()

            # Stop monitoring and diagnostics
            if self.diagnostics:
                await self.diagnostics.stop_monitoring()
            if self.monitoring:
                await self.monitoring.stop_monitoring()

            # Stop all agents
            stop_tasks = []
            for agent in self.agents.values():
                stop_tasks.append(agent.stop())

            # Wait for all agents to stop
            await asyncio.gather(*stop_tasks, return_exceptions=True)

            # Mark as inactive
            self.is_active = False

            self.logger.info(f"Swarm '{self.swarm_name}' stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop swarm: {e}")
            return False

    async def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the swarm.

        Args:
            agent: Agent to register

        Returns:
            bool: True if agent registered successfully
        """
        try:
            agent_name = agent.agent_name

            # Check for efficiency rule violations
            if self.efficiency_enforcer:
                action = SwarmAction(
                    action_type="create_agent",
                    description=f"Register agent {agent_name}",
                    target=agent_name,
                    metadata={
                        "capabilities": getattr(agent, 'domain_expertise', []),
                        "agent_type": type(agent).__name__
                    }
                )

                enforcement = await self.efficiency_enforcer.enforce_action(action)
                if not enforcement.approved:
                    self.logger.warning(f"Agent registration blocked by efficiency rules: {enforcement.reason}")
                    alternatives = enforcement.alternatives
                    if alternatives:
                        self.logger.info("Suggested alternatives:")
                        for alt in alternatives:
                            self.logger.info(f"  - {alt.get('reason', 'Alternative available')}")
                    return False

            # Register the agent
            self.agents[agent_name] = agent
            agent.set_swarm_context(self)

            # Register capabilities with efficiency enforcer
            if self.efficiency_enforcer:
                capabilities = getattr(agent, 'domain_expertise', [])
                for capability in capabilities:
                    await self.efficiency_enforcer.register_agent_capability(agent_name, capability)

            self.logger.info(f"Registered agent '{agent_name}' with capabilities: {capabilities}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_name}: {e}")
            return False

    async def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the swarm.

        Args:
            agent_name: Name of agent to unregister

        Returns:
            bool: True if agent unregistered successfully
        """
        if agent_name not in self.agents:
            self.logger.warning(f"Agent '{agent_name}' not found")
            return False

        try:
            agent = self.agents[agent_name]

            # Stop the agent if swarm is active
            if self.is_active:
                await agent.stop()

            # Remove from registry
            del self.agents[agent_name]

            self.logger.info(f"Unregistered agent '{agent_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_name}: {e}")
            return False

    async def execute_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """
        Execute a task through democratic agent coordination.

        Args:
            task_description: Description of the task
            context: Additional context for task execution

        Returns:
            TaskResult: Result of task execution
        """
        start_time = time.time()
        context = context or {}

        try:
            # Check swarm status
            if not self.is_active:
                return TaskResult(
                    success=False,
                    error="Swarm is not active",
                    execution_time=time.time() - start_time
                )

            # Perform democratic task assignment
            assigned_agent, confidence = await self._assign_task_democratically(
                task_description, context
            )

            if not assigned_agent:
                return TaskResult(
                    success=False,
                    error="No agent available for task",
                    execution_time=time.time() - start_time
                )

            # Execute task through assigned agent
            result = await assigned_agent.execute_task(task_description, context)

            # Update metrics
            execution_time = time.time() - start_time
            self._update_task_metrics(result.success, execution_time)

            # Record in history
            self.task_history.append({
                "timestamp": datetime.now().isoformat(),
                "task": task_description,
                "agent": assigned_agent.agent_name,
                "success": result.success,
                "execution_time": execution_time,
                "confidence": confidence
            })

            return TaskResult(
                success=result.success,
                agent_name=assigned_agent.agent_name,
                data=result.data if hasattr(result, 'data') else None,
                error=result.error if hasattr(result, 'error') else "",
                execution_time=execution_time,
                confidence_score=confidence,
                consensus_level=confidence
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Task execution failed: {str(e)}"

            self.logger.error(error_msg)
            self._update_task_metrics(False, execution_time)

            return TaskResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )

    async def _assign_task_democratically(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> tuple[Optional[BaseAgent], float]:
        """
        Assign task to agent through democratic voting.

        Returns:
            Tuple of (assigned_agent, confidence_score)
        """
        if not self.agents:
            return None, 0.0

        # Have each agent vote on task suitability
        votes = []
        for agent in self.agents.values():
            try:
                # Get agent confidence for this task
                confidence = await agent.calculate_task_confidence(task_description, context)

                # Check if agent abstains
                should_abstain = await agent.should_abstain_from_vote(task_description)

                if not should_abstain and confidence > 0.3:  # Minimum confidence threshold
                    votes.append({
                        "agent": agent,
                        "confidence": confidence,
                        "weight": confidence  # Higher confidence = higher voting weight
                    })

            except Exception as e:
                self.logger.warning(f"Agent {agent.agent_name} failed to vote: {e}")
                continue

        if not votes:
            return None, 0.0

        # Sort by confidence (highest first)
        votes.sort(key=lambda x: x["confidence"], reverse=True)

        # Assign to highest confidence agent
        assigned_agent = votes[0]["agent"]
        confidence = votes[0]["confidence"]

        self.logger.info(f"Democratically assigned task to {assigned_agent.agent_name} "
                        f"(confidence: {confidence:.2f})")

        return assigned_agent, confidence

    def _update_task_metrics(self, success: bool, execution_time: float):
        """Update internal task metrics."""
        self.metrics["total_tasks_processed"] += 1

        if success:
            self.metrics["successful_tasks"] += 1
        else:
            self.metrics["failed_tasks"] += 1

        # Update average execution time
        total_tasks = self.metrics["total_tasks_processed"]
        current_avg = self.metrics["average_execution_time"]
        self.metrics["average_execution_time"] = (
            (current_avg * (total_tasks - 1)) + execution_time
        ) / total_tasks

    async def analyze_swarm_health(self) -> SwarmHealth:
        """
        Analyze overall swarm health and provide recommendations.

        Returns:
            SwarmHealth: Comprehensive health analysis
        """
        try:
            health = SwarmHealth()

            # Calculate overall health score
            agent_health_scores = []
            for agent in self.agents.values():
                try:
                    agent_status = await agent.get_status_async()
                    health_score = agent_status.get("confidence", {}).get("overall", 0.5)
                    agent_health_scores.append(health_score)
                    health.agent_health[agent.agent_name] = health_score
                except Exception:
                    agent_health_scores.append(0.0)
                    health.agent_health[agent.agent_name] = 0.0

            # Overall health is average of agent health
            if agent_health_scores:
                health.overall_health_score = sum(agent_health_scores) / len(agent_health_scores)

                if health.overall_health_score > 0.8:
                    health.health_status = "excellent"
                elif health.overall_health_score > 0.6:
                    health.health_status = "good"
                elif health.overall_health_score > 0.4:
                    health.health_status = "fair"
                else:
                    health.health_status = "poor"

            # Task success rate
            total_tasks = self.metrics["total_tasks_processed"]
            if total_tasks > 0:
                health.task_success_rate = self.metrics["successful_tasks"] / total_tasks

            # Average response time
            health.average_response_time = self.metrics["average_execution_time"]

            # Check for critical issues
            if len(self.agents) == 0:
                health.critical_issues.append({
                    "title": "No Agents Registered",
                    "description": "Swarm has no registered agents",
                    "severity": "critical"
                })

            if health.overall_health_score < 0.3:
                health.critical_issues.append({
                    "title": "Low Agent Health",
                    "description": "Agent health scores are critically low",
                    "severity": "critical"
                })

            if health.task_success_rate < 0.5 and total_tasks > 5:
                health.critical_issues.append({
                    "title": "Low Task Success Rate",
                    "description": f"Only {health.task_success_rate:.1f} of tasks succeed",
                    "severity": "high"
                })

            # Generate recommendations
            if len(self.agents) < 3:
                health.recommendations.append("Consider adding more specialized agents")
            if health.task_success_rate < 0.7:
                health.recommendations.append("Investigate and improve task success rates")
            if health.average_response_time > 30:
                health.recommendations.append("Optimize agent response times")

            # Detailed analysis
            health.detailed_analysis = {
                "agents": {
                    "total": len(self.agents),
                    "active": len([a for a in self.agents.values() if getattr(a, 'is_active', False)]),
                    "health_scores": health.agent_health
                },
                "tasks": {
                    "total_processed": self.metrics["total_tasks_processed"],
                    "success_rate": health.task_success_rate,
                    "average_duration": health.average_response_time
                },
                "performance": {
                    "uptime_seconds": time.time() - (self.start_time or time.time()),
                    "efficiency_metrics": self.efficiency_enforcer.get_efficiency_report() if self.efficiency_enforcer else {}
                }
            }

            return health

        except Exception as e:
            self.logger.error(f"Health analysis failed: {e}")
            return SwarmHealth(
                overall_health_score=0.0,
                health_status="error",
                critical_issues=[{
                    "title": "Health Analysis Failed",
                    "description": f"Error during health check: {str(e)}",
                    "severity": "critical"
                }]
            )

    async def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Returns:
            Dict containing performance metrics and analysis
        """
        try:
            # Gather metrics
            total_tasks = self.metrics["total_tasks_processed"]
            successful_tasks = self.metrics["successful_tasks"]
            failed_tasks = self.metrics["failed_tasks"]
            avg_execution_time = self.metrics["average_execution_time"]

            # Calculate rates
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0

            # Gather agent performance
            agent_performance = {}
            for agent_name, agent in self.agents.items():
                try:
                    status = await agent.get_status_async()
                    agent_performance[agent_name] = {
                        "confidence": status.get("confidence", {}).get("overall", 0.0),
                        "tasks_processed": status.get("tasks_processed", 0),
                        "success_rate": status.get("success_rate", 0.0)
                    }
                except Exception:
                    agent_performance[agent_name] = {"error": "Status unavailable"}

            # Generate recommendations
            recommendations = []
            if success_rate < 0.8:
                recommendations.append("Improve task success rates through better agent selection")
            if avg_execution_time > 10:
                recommendations.append("Optimize agent execution times")
            if len(self.agents) < 3:
                recommendations.append("Consider adding more specialized agents")

            # Efficiency analysis
            efficiency_report = {}
            if self.efficiency_enforcer:
                efficiency_report = self.efficiency_enforcer.get_efficiency_report()

            return {
                "report_id": f"swarm_{self.swarm_name}_{int(time.time())}",
                "time_range": {
                    "start_time": self.start_time,
                    "end_time": time.time(),
                    "duration_hours": (time.time() - (self.start_time or time.time())) / 3600
                },
                "summary_metrics": {
                    "total_tasks": total_tasks,
                    "successful_tasks": successful_tasks,
                    "failed_tasks": failed_tasks,
                    "success_rate": success_rate,
                    "average_task_duration": avg_execution_time,
                    "peak_memory_mb": self.metrics["peak_memory_usage_mb"]
                },
                "agent_performance": agent_performance,
                "recommendations": recommendations,
                "efficiency_analysis": efficiency_report,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Performance report generation failed: {e}")
            return {
                "error": f"Report generation failed: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }

    async def get_swarm_status(self) -> Dict[str, Any]:
        """
        Get current swarm status.

        Returns:
            Dict containing swarm status information
        """
        uptime = time.time() - (self.start_time or time.time())

        # Count active agents
        active_agents = 0
        for agent in self.agents.values():
            try:
                if getattr(agent, 'is_active', False):
                    active_agents += 1
            except Exception:
                continue

        return {
            "swarm_name": self.swarm_name,
            "is_active": self.is_active,
            "uptime_seconds": uptime,
            "agents": {
                "total": len(self.agents),
                "active": active_agents
            },
            "tasks": {
                "total_processed": self.metrics["total_tasks_processed"],
                "successful": self.metrics["successful_tasks"],
                "failed": self.metrics["failed_tasks"]
            },
            "health": {
                "overall_score": (await self.analyze_swarm_health()).overall_health_score
            },
            "efficiency": self.efficiency_enforcer.get_efficiency_report() if self.efficiency_enforcer else {}
        }

    def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks."""
        # Task queue processor
        task_processor = asyncio.create_task(self._process_task_queue())
        self._background_tasks.add(task_processor)
        task_processor.add_done_callback(self._background_tasks.discard)

        # Health checker
        if self.enable_monitoring:
            health_checker = asyncio.create_task(self._periodic_health_check())
            self._background_tasks.add(health_checker)
            health_checker.add_done_callback(self._background_tasks.discard)

    async def _process_task_queue(self):
        """Process tasks from the queue."""
        while self.is_active:
            try:
                # Wait for task with timeout
                task_data = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Process task
                await self._handle_queued_task(task_data)

                self.task_queue.task_done()

            except asyncio.TimeoutError:
                continue  # No tasks, continue loop
            except Exception as e:
                self.logger.error(f"Task queue processing error: {e}")

    async def _handle_queued_task(self, task_data: Dict[str, Any]):
        """Handle a queued task."""
        # Implementation for queued task processing
        # This would handle asynchronous task queuing if needed
        pass

    async def _periodic_health_check(self):
        """Perform periodic health checks."""
        while self.is_active:
            try:
                await asyncio.sleep(60)  # Check every minute

                health = await self.analyze_swarm_health()

                if health.overall_health_score < 0.5:
                    self.logger.warning(f"Swarm health degraded: {health.overall_health_score:.2f}")

                # Log critical issues
                for issue in health.critical_issues:
                    self.logger.error(f"Critical issue: {issue['title']} - {issue['description']}")

            except Exception as e:
                self.logger.error(f"Health check failed: {e}")

    async def _cleanup_failed_start(self):
        """Clean up after a failed swarm start."""
        # Stop any agents that may have started
        for agent in self.agents.values():
            try:
                if getattr(agent, 'is_active', False):
                    await agent.stop()
            except Exception:
                pass

        # Clear state
        self.is_active = False
        self.start_time = None

    def __repr__(self) -> str:
        return f"PydanticAISwarmOrchestrator(name='{self.swarm_name}', agents={len(self.agents)}, active={self.is_active})"
