#!/usr/bin/env python3
"""Swarm Orchestrator Agent - Lead coordinator for the democratic agent swarm.

This agent serves as the central intelligence and overseer for the democratic AI agent swarm,
coordinating task assignments, facilitating consensus, and maintaining swarm cohesion.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from base_agent import ToolBasedAgent


class SwarmOrchestratorAgent(ToolBasedAgent):
    """Swarm Orchestrator Agent - Central coordinator for democratic agent swarm."""

    def __init__(self, config_path: str = "agents_config.json"):
        """Initialize the Swarm Orchestrator Agent.

        Args:
            config_path: Path to agent configuration file
        """
        super().__init__("swarm_orchestrator", config_path)
        self.logger = logging.getLogger(__name__)

        # Swarm state tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.swarm_health: Dict[str, Any] = {}
        self.workflow_states: Dict[str, Dict[str, Any]] = {}

        # Coordination metrics
        self.coordination_stats = {
            'tasks_assigned': 0,
            'conflicts_resolved': 0,
            'consensus_reached': 0,
            'workflows_coordinated': 0
        }

        # Initialize domain confidence for orchestration
        self.confidence.domains['orchestration'] = 0.9
        self.confidence.domains['coordination'] = 0.9
        self.confidence.domains['conflict_resolution'] = 0.85
        self.confidence.update_overall_confidence()

        self.logger.info("Swarm Orchestrator Agent initialized")

    def analyze_swarm_health(self, time_window: int = 3600,
                           include_agents: Optional[List[str]] = None,
                           metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze overall swarm health and performance metrics.

        Args:
            time_window: Time window in seconds to analyze
            include_agents: Specific agents to include in analysis
            metrics: Specific metrics to analyze

        Returns:
            Comprehensive swarm health analysis
        """
        try:
            # Get system metrics from monitoring
            if hasattr(self, '_get_system_metrics'):
                system_metrics = self._get_system_metrics(time_window)
            else:
                system_metrics = self._simulate_system_metrics(time_window)

            # Analyze agent health
            agent_health = self._analyze_agent_health(include_agents or [])

            # Calculate swarm-wide metrics
            swarm_metrics = self._calculate_swarm_metrics(system_metrics, agent_health, metrics)

            # Generate recommendations
            recommendations = self._generate_health_recommendations(swarm_metrics)

            health_analysis = {
                'timestamp': time.time(),
                'time_window_seconds': time_window,
                'overall_health_score': swarm_metrics.get('health_score', 0.5),
                'system_metrics': system_metrics,
                'agent_health': agent_health,
                'swarm_metrics': swarm_metrics,
                'recommendations': recommendations,
                'risk_assessment': self._assess_risks(swarm_metrics)
            }

            self.swarm_health = health_analysis
            self.logger.info(f"Swarm health analysis completed: score {health_analysis['overall_health_score']:.2f}")

            return health_analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze swarm health: {e}")
            return {'error': str(e), 'overall_health_score': 0.0}

    def optimize_task_assignment(self, pending_tasks: List[Dict[str, Any]],
                               available_agents: List[str],
                               optimization_criteria: List[str]) -> Dict[str, Any]:
        """Optimize task assignment based on agent capabilities and workload.

        Args:
            pending_tasks: List of tasks waiting to be assigned
            available_agents: List of available agent names
            optimization_criteria: Criteria for optimization

        Returns:
            Optimized task assignment plan
        """
        try:
            # Get agent capabilities and current workloads
            agent_capabilities = self._get_agent_capabilities(available_agents)
            current_workloads = self._get_current_workloads(available_agents)

            # Score task-agent matches
            assignment_scores = {}
            for task in pending_tasks:
                task_scores = {}
                for agent_name in available_agents:
                    score = self._calculate_task_agent_fit(
                        task, agent_name, agent_capabilities, current_workloads, optimization_criteria
                    )
                    task_scores[agent_name] = score
                assignment_scores[task.get('id', str(id(task)))] = task_scores

            # Generate optimal assignment plan
            assignment_plan = self._generate_assignment_plan(assignment_scores, optimization_criteria)

            # Update coordination stats
            self.coordination_stats['tasks_assigned'] += len(assignment_plan.get('assignments', []))

            result = {
                'assignment_plan': assignment_plan,
                'optimization_criteria': optimization_criteria,
                'agent_utilization': self._calculate_agent_utilization(available_agents, current_workloads),
                'estimated_completion_time': assignment_plan.get('estimated_completion', 0)
            }

            self.logger.info(f"Task assignment optimization completed for {len(pending_tasks)} tasks")
            return result

        except Exception as e:
            self.logger.error(f"Failed to optimize task assignment: {e}")
            return {'error': str(e), 'assignment_plan': {'assignments': []}}

    def facilitate_consensus(self, proposal: Dict[str, Any],
                           stakeholders: List[str],
                           deadline: int) -> Dict[str, Any]:
        """Facilitate consensus-building among agents on complex decisions.

        Args:
            proposal: The proposal to build consensus on
            stakeholders: List of stakeholder agent names
            deadline: Deadline for consensus in seconds

        Returns:
            Consensus result and process details
        """
        try:
            proposal_id = proposal.get('id', f"proposal_{int(time.time())}")

            # Initialize voting process
            voting_session = {
                'proposal_id': proposal_id,
                'proposal': proposal,
                'stakeholders': stakeholders,
                'deadline': time.time() + deadline,
                'votes': {},
                'status': 'active'
            }

            # Simulate consensus facilitation (in real implementation, this would coordinate with voting system)
            consensus_result = self._simulate_consensus_process(voting_session)

            # Update coordination stats
            if consensus_result.get('consensus_reached', False):
                self.coordination_stats['consensus_reached'] += 1

            result = {
                'proposal_id': proposal_id,
                'consensus_reached': consensus_result.get('consensus_reached', False),
                'winning_option': consensus_result.get('winning_option'),
                'participation_rate': consensus_result.get('participation_rate', 0),
                'process_details': consensus_result,
                'facilitation_notes': self._generate_facilitation_notes(consensus_result)
            }

            self.logger.info(f"Consensus facilitation completed for proposal {proposal_id}: {result['consensus_reached']}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to facilitate consensus: {e}")
            return {'error': str(e), 'consensus_reached': False}

    def resolve_conflicts(self, conflict_description: str,
                        involved_agents: List[str],
                        resolution_strategy: str) -> Dict[str, Any]:
        """Resolve conflicts and deadlocks in swarm decision-making.

        Args:
            conflict_description: Description of the conflict
            involved_agents: Agents involved in the conflict
            resolution_strategy: Preferred resolution strategy

        Returns:
            Conflict resolution result
        """
        try:
            conflict_id = f"conflict_{int(time.time())}"

            # Analyze conflict
            conflict_analysis = self._analyze_conflict(conflict_description, involved_agents)

            # Apply resolution strategy
            resolution = self._apply_resolution_strategy(
                conflict_analysis, resolution_strategy, involved_agents
            )

            # Update coordination stats
            if resolution.get('resolved', False):
                self.coordination_stats['conflicts_resolved'] += 1

            result = {
                'conflict_id': conflict_id,
                'conflict_analysis': conflict_analysis,
                'resolution_strategy': resolution_strategy,
                'resolution': resolution,
                'resolution_successful': resolution.get('resolved', False),
                'follow_up_actions': resolution.get('follow_up_actions', [])
            }

            self.logger.info(f"Conflict resolution completed for {conflict_id}: {result['resolution_successful']}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to resolve conflict: {e}")
            return {'error': str(e), 'resolution_successful': False}

    def coordinate_workflow(self, workflow_definition: Dict[str, Any],
                          agent_assignments: Dict[str, str],
                          monitoring_points: List[str]) -> Dict[str, Any]:
        """Coordinate complex multi-agent workflows.

        Args:
            workflow_definition: Definition of the workflow
            agent_assignments: Mapping of workflow steps to agents
            monitoring_points: Points in workflow to monitor

        Returns:
            Workflow coordination result
        """
        try:
            workflow_id = workflow_definition.get('id', f"workflow_{int(time.time())}")

            # Initialize workflow tracking
            workflow_state = {
                'workflow_id': workflow_id,
                'definition': workflow_definition,
                'agent_assignments': agent_assignments,
                'monitoring_points': monitoring_points,
                'status': 'initialized',
                'current_step': 0,
                'start_time': time.time(),
                'step_results': []
            }

            self.workflow_states[workflow_id] = workflow_state

            # Simulate workflow coordination (in real implementation, this would manage the workflow execution)
            coordination_result = self._coordinate_workflow_execution(workflow_state)

            # Update coordination stats
            if coordination_result.get('completed', False):
                self.coordination_stats['workflows_coordinated'] += 1

            result = {
                'workflow_id': workflow_id,
                'coordination_result': coordination_result,
                'workflow_status': coordination_result.get('status', 'unknown'),
                'completion_percentage': coordination_result.get('completion_percentage', 0),
                'estimated_completion_time': coordination_result.get('estimated_completion', 0),
                'issues_encountered': coordination_result.get('issues', [])
            }

            self.logger.info(f"Workflow coordination initiated for {workflow_id}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to coordinate workflow: {e}")
            return {'error': str(e), 'workflow_status': 'failed'}

    def _get_system_metrics(self, time_window: int) -> Dict[str, Any]:
        """Get system metrics from monitoring infrastructure."""
        # In real implementation, this would query the monitoring system
        return {
            'total_messages': 1250,
            'active_conversations': 8,
            'task_completion_rate': 0.92,
            'average_response_time': 2.3,
            'error_rate': 0.03
        }

    def _simulate_system_metrics(self, time_window: int) -> Dict[str, Any]:
        """Simulate system metrics for demo purposes."""
        return {
            'total_messages': 850 + (time_window // 3600) * 200,
            'active_conversations': 5 + (time_window // 1800),
            'task_completion_rate': 0.89,
            'average_response_time': 1.8,
            'error_rate': 0.025
        }

    def _analyze_agent_health(self, include_agents: List[str]) -> Dict[str, Any]:
        """Analyze health of individual agents."""
        # In real implementation, this would query agent status
        agent_health = {}
        for agent_name in include_agents or ['video_editor', 'audio_engineer', 'social_media_manager']:
            agent_health[agent_name] = {
                'status': 'healthy',
                'confidence': 0.85,
                'active_tasks': 2,
                'error_rate': 0.02,
                'response_time': 1.5
            }
        return agent_health

    def _calculate_swarm_metrics(self, system_metrics: Dict[str, Any],
                               agent_health: Dict[str, Any],
                               requested_metrics: Optional[List[str]]) -> Dict[str, Any]:
        """Calculate comprehensive swarm metrics."""
        # Calculate health score based on various factors
        health_factors = []

        # Task completion rate (weight: 0.3)
        task_completion = system_metrics.get('task_completion_rate', 0.8)
        health_factors.append(('task_completion', task_completion, 0.3))

        # Error rate (inverse, weight: 0.25)
        error_rate = system_metrics.get('error_rate', 0.05)
        error_health = max(0, 1 - error_rate * 4)  # Convert to health score
        health_factors.append(('error_rate', error_health, 0.25))

        # Response time (inverse, weight: 0.2)
        response_time = system_metrics.get('average_response_time', 2.0)
        response_health = max(0, 1 - (response_time - 1) / 4)  # Convert to health score
        health_factors.append(('response_time', response_health, 0.2))

        # Agent health average (weight: 0.25)
        agent_scores = [agent.get('confidence', 0.5) for agent in agent_health.values()]
        avg_agent_health = sum(agent_scores) / len(agent_scores) if agent_scores else 0.5
        health_factors.append(('agent_health', avg_agent_health, 0.25))

        # Calculate weighted health score
        health_score = sum(score * weight for _, score, weight in health_factors)

        return {
            'health_score': health_score,
            'health_factors': health_factors,
            'performance_indicators': {
                'throughput': system_metrics.get('total_messages', 0) / max(1, system_metrics.get('time_window', 3600) / 3600),
                'efficiency': task_completion / max(0.1, response_time),
                'reliability': 1 - error_rate
            }
        }

    def _generate_health_recommendations(self, swarm_metrics: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on metrics."""
        recommendations = []
        health_score = swarm_metrics.get('health_score', 0.5)

        if health_score < 0.6:
            recommendations.append("Critical: Overall swarm health is low. Consider emergency coordination workflow.")
        elif health_score < 0.75:
            recommendations.append("Warning: Swarm performance could be improved. Review agent workloads and task assignments.")

        health_factors = swarm_metrics.get('health_factors', [])
        for factor_name, score, _ in health_factors:
            if score < 0.7:
                if factor_name == 'task_completion':
                    recommendations.append("Improve task completion rate by reviewing agent capabilities and task complexity.")
                elif factor_name == 'error_rate':
                    recommendations.append("Reduce error rate through better error handling and agent training.")
                elif factor_name == 'response_time':
                    recommendations.append("Optimize response times by improving resource allocation and reducing bottlenecks.")
                elif factor_name == 'agent_health':
                    recommendations.append("Address agent health issues through monitoring and potential agent replacement.")

        return recommendations

    def _assess_risks(self, swarm_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks based on swarm metrics."""
        health_score = swarm_metrics.get('health_score', 0.5)

        if health_score < 0.5:
            risk_level = 'critical'
            risk_description = 'Swarm is at high risk of failure'
        elif health_score < 0.7:
            risk_level = 'high'
            risk_description = 'Swarm has elevated risk of performance issues'
        elif health_score < 0.85:
            risk_level = 'medium'
            risk_description = 'Swarm performance could be more stable'
        else:
            risk_level = 'low'
            risk_description = 'Swarm is operating normally'

        return {
            'risk_level': risk_level,
            'description': risk_description,
            'mitigation_actions': self._get_risk_mitigation_actions(risk_level)
        }

    def _get_risk_mitigation_actions(self, risk_level: str) -> List[str]:
        """Get risk mitigation actions based on risk level."""
        actions = {
            'critical': [
                'Activate emergency coordination workflow immediately',
                'Isolate problematic agents',
                'Implement manual oversight',
                'Prepare contingency plans'
            ],
            'high': [
                'Increase monitoring frequency',
                'Review and optimize task assignments',
                'Consider scaling resources',
                'Prepare crisis management workflow'
            ],
            'medium': [
                'Monitor performance trends closely',
                'Schedule regular health checks',
                'Review agent configurations',
                'Plan optimization improvements'
            ],
            'low': [
                'Continue normal operations',
                'Perform routine maintenance',
                'Monitor for emerging trends'
            ]
        }
        return actions.get(risk_level, [])

    def _get_agent_capabilities(self, agent_names: List[str]) -> Dict[str, Any]:
        """Get capabilities of specified agents."""
        # In real implementation, this would query agent capabilities
        capabilities = {}
        for agent_name in agent_names:
            if 'video' in agent_name:
                capabilities[agent_name] = ['video_editing', 'content_creation', 'media_processing']
            elif 'audio' in agent_name:
                capabilities[agent_name] = ['audio_processing', 'sound_design', 'music_production']
            elif 'social' in agent_name:
                capabilities[agent_name] = ['social_media', 'content_scheduling', 'engagement']
            else:
                capabilities[agent_name] = ['general_tasks', 'coordination']
        return capabilities

    def _get_current_workloads(self, agent_names: List[str]) -> Dict[str, int]:
        """Get current workloads of specified agents."""
        # In real implementation, this would query current workloads
        workloads = {}
        for agent_name in agent_names:
            workloads[agent_name] = len(self.active_tasks.get(agent_name, []))
        return workloads

    def _calculate_task_agent_fit(self, task: Dict[str, Any], agent_name: str,
                                capabilities: Dict[str, Any], workloads: Dict[str, int],
                                criteria: List[str]) -> float:
        """Calculate how well a task fits an agent."""
        score = 0.0

        # Capability match (weight: 0.4)
        task_type = task.get('type', '')
        agent_caps = capabilities.get(agent_name, [])
        cap_match = any(task_type.lower() in cap.lower() for cap in agent_caps)
        score += 0.4 * (1.0 if cap_match else 0.3)

        # Current workload (weight: 0.3) - prefer less busy agents
        current_load = workloads.get(agent_name, 0)
        load_penalty = min(1.0, current_load / 5.0)  # Max 5 tasks
        score += 0.3 * (1.0 - load_penalty)

        # Agent confidence (weight: 0.3) - prefer confident agents
        confidence = self.agent_status.get(agent_name, {}).get('confidence', 0.5)
        score += 0.3 * confidence

        return score

    def _generate_assignment_plan(self, assignment_scores: Dict[str, Dict[str, float]],
                                criteria: List[str]) -> Dict[str, Any]:
        """Generate optimal assignment plan from scores."""
        assignments = []
        estimated_completion = 0

        # Simple greedy assignment - in real implementation, this would use optimization algorithms
        for task_id, agent_scores in assignment_scores.items():
            if agent_scores:
                best_agent = max(agent_scores.items(), key=lambda x: x[1])
                assignments.append({
                    'task_id': task_id,
                    'assigned_agent': best_agent[0],
                    'confidence_score': best_agent[1],
                    'estimated_duration': 120  # 2 minutes default
                })
                estimated_completion = max(estimated_completion, 120)

        return {
            'assignments': assignments,
            'total_tasks': len(assignments),
            'estimated_completion': estimated_completion,
            'optimization_method': 'greedy_assignment'
        }

    def _calculate_agent_utilization(self, agent_names: List[str],
                                   workloads: Dict[str, int]) -> Dict[str, float]:
        """Calculate agent utilization rates."""
        utilization = {}
        for agent_name in agent_names:
            current_load = workloads.get(agent_name, 0)
            max_capacity = 5  # Assume max 5 concurrent tasks
            utilization[agent_name] = min(1.0, current_load / max_capacity)
        return utilization

    def _simulate_consensus_process(self, voting_session: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate consensus building process."""
        # In real implementation, this would coordinate actual voting
        stakeholders = voting_session.get('stakeholders', [])
        votes = {}

        # Simulate agent voting based on confidence
        for agent in stakeholders:
            confidence = self.agent_status.get(agent, {}).get('confidence', 0.5)
            if confidence > 0.6:  # Only confident agents vote
                votes[agent] = 'approve' if confidence > 0.7 else 'reject'

        # Determine consensus
        approve_votes = sum(1 for vote in votes.values() if vote == 'approve')
        total_votes = len(votes)

        consensus_reached = total_votes >= len(stakeholders) * 0.6  # 60% participation
        consensus_reached = consensus_reached and approve_votes > total_votes * 0.5

        return {
            'consensus_reached': consensus_reached,
            'winning_option': 'approve' if consensus_reached else None,
            'participation_rate': total_votes / len(stakeholders) if stakeholders else 0,
            'vote_breakdown': {'approve': approve_votes, 'reject': total_votes - approve_votes},
            'total_participants': len(stakeholders)
        }

    def _generate_facilitation_notes(self, consensus_result: Dict[str, Any]) -> str:
        """Generate notes about the consensus facilitation process."""
        if consensus_result.get('consensus_reached'):
            return "Consensus reached successfully with good participation."
        else:
            participation = consensus_result.get('participation_rate', 0)
            if participation < 0.5:
                return "Low participation may have prevented consensus."
            else:
                return "Consensus not reached due to divided opinions."

    def _analyze_conflict(self, description: str, involved_agents: List[str]) -> Dict[str, Any]:
        """Analyze a conflict situation."""
        return {
            'conflict_type': 'resource_contention' if 'resource' in description.lower() else 'task_priority',
            'severity': 'medium',
            'root_cause': 'competing priorities',
            'impact_assessment': 'moderate impact on workflow efficiency',
            'involved_agents': involved_agents
        }

    def _apply_resolution_strategy(self, conflict_analysis: Dict[str, Any],
                                 strategy: str, agents: List[str]) -> Dict[str, Any]:
        """Apply conflict resolution strategy."""
        if strategy == 'prioritization':
            resolution = {
                'resolved': True,
                'method': 'task prioritization',
                'actions': ['Reorder task queue', 'Notify affected agents'],
                'follow_up_actions': ['Monitor task completion', 'Review prioritization logic']
            }
        elif strategy == 'negotiation':
            resolution = {
                'resolved': True,
                'method': 'agent negotiation',
                'actions': ['Facilitate agent discussion', 'Find compromise solution'],
                'follow_up_actions': ['Document agreement', 'Monitor compliance']
            }
        else:
            resolution = {
                'resolved': False,
                'method': 'escalation_required',
                'actions': ['Escalate to human overseer'],
                'follow_up_actions': ['Wait for human intervention']
            }

        return resolution

    def _coordinate_workflow_execution(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate workflow execution."""
        # Simulate workflow progression
        steps = workflow_state['definition'].get('steps', [])
        completed_steps = min(len(steps), 3)  # Simulate partial completion

        return {
            'status': 'in_progress',
            'completed_steps': completed_steps,
            'total_steps': len(steps),
            'completion_percentage': (completed_steps / len(steps)) * 100,
            'estimated_completion': 300,  # 5 minutes
            'issues': [],
            'next_steps': steps[completed_steps:completed_steps+1]
        }

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status."""
        return {
            'active_tasks': len(self.active_tasks),
            'agent_count': len(self.agent_status),
            'workflow_count': len(self.workflow_states),
            'coordination_stats': self.coordination_stats,
            'swarm_health': self.swarm_health.get('overall_health_score', 0.5)
        }
