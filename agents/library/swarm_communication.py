"""Swarm Communication Infrastructure - Democratic AI Agent Swarm.

This module provides the communication infrastructure for democratic AI agent swarms,
enabling agents to communicate, vote, and coordinate autonomously.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional, Set

from base_agent import BaseAgent


@dataclass
class Message:
    """Represents a message between agents."""

    message_id: str
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: int = 1  # 1=low, 5=high
    ttl: int = 300  # Time to live in seconds
    correlation_id: Optional[str] = None  # For request-response patterns

    def is_expired(self) -> bool:
        """Check if message has expired."""
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp,
            'priority': self.priority,
            'ttl': self.ttl,
            'correlation_id': self.correlation_id
        }


@dataclass
class VoteProposal:
    """Represents a voting proposal with enhanced validation and tracking."""

    proposal_id: str
    proposer: str
    title: str
    description: str
    options: List[str]
    context: str = ""
    required_quorum: float = 0.5  # Fraction of agents needed
    consensus_threshold: float = 0.66  # Fraction (by weight) required for winner to be considered consensus
    min_votes: int = 1  # Absolute minimum number of votes required for consensus
    voting_deadline: Optional[float] = None
    votes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    status: str = "active"  # active, completed, cancelled
    created_at: float = field(default_factory=time.time)
    attendance_log: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Track attendance
    validation_errors: List[str] = field(default_factory=list)  # Validation issues
    conversation_log: List[Dict[str, Any]] = field(default_factory=list)  # Related conversations

    def add_vote(self, agent_name: str, vote: Dict[str, Any]) -> bool:
        """Add a vote to the proposal with validation.

        Args:
            agent_name: Name of the voting agent
            vote: Vote data

        Returns:
            True if vote was added successfully
        """
        # Validate vote
        if not self._validate_vote(agent_name, vote):
            return False

        # Record attendance
        self.attendance_log[agent_name] = {
            'timestamp': time.time(),
            'action': 'voted',
            'vote_decision': vote.get('decision'),
            'confidence': vote.get('confidence', 0.0)
        }

        self.votes[agent_name] = vote
        return True

    def record_attendance(self, agent_name: str, action: str = "present") -> None:
        """Record agent attendance for this proposal.

        Args:
            agent_name: Name of the agent
            action: Attendance action (present, absent, abstained, etc.)
        """
        self.attendance_log[agent_name] = {
            'timestamp': time.time(),
            'action': action,
            'vote_decision': None
        }

    def log_conversation(self, agent_name: str, message: str, message_type: str = "discussion") -> None:
        """Log a conversation related to this proposal.

        Args:
            agent_name: Agent who made the statement
            message: Conversation content
            message_type: Type of conversation (discussion, clarification, objection, etc.)
        """
        conversation_entry = {
            'timestamp': time.time(),
            'agent': agent_name,
            'message': message,
            'type': message_type,
            'proposal_id': self.proposal_id
        }
        self.conversation_log.append(conversation_entry)

    def _validate_vote(self, agent_name: str, vote: Dict[str, Any]) -> bool:
        """Validate a vote before accepting it.

        Args:
            agent_name: Name of the voting agent
            vote: Vote data to validate

        Returns:
            True if vote is valid
        """
        errors = []

        # Check if agent already voted
        if agent_name in self.votes:
            errors.append(f"Agent {agent_name} has already voted on this proposal")

        # Validate decision
        decision = vote.get('decision')
        if decision not in ['abstain'] + self.options:
            errors.append(f"Invalid decision '{decision}'. Must be one of: {['abstain'] + self.options}")

        # Validate weight
        weight = vote.get('weight', 1.0)
        if not isinstance(weight, (int, float)) or weight < 0 or weight > 2.0:
            errors.append(f"Invalid weight {weight}. Must be between 0.0 and 2.0")

        # Validate confidence
        confidence = vote.get('confidence', 0.0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1.0:
            errors.append(f"Invalid confidence {confidence}. Must be between 0.0 and 1.0")

        # Check voting deadline
        if self.voting_deadline and time.time() > self.voting_deadline:
            errors.append("Voting deadline has passed")

        # Check proposal status
        if self.status != 'active':
            errors.append(f"Proposal is not active (status: {self.status})")

        if errors:
            self.validation_errors.extend(errors)
            return False

        return True

    def get_vote_summary(self, total_registered_agents: Optional[int] = None) -> Dict[str, Any]:
        """Get summary of votes with enhanced metrics.

        Args:
            total_registered_agents: Optional explicit total number of registered agents to compute quorum against. 
                                     If None, uses attendance_log length (legacy behavior).
        """
        if not self.votes:
            return {
                'total_votes': 0,
                'total_weight': 0.0,
                'results': {},
                'quorum_reached': False,
                'attendance_rate': 0.0,
                'abstention_rate': 0.0,
                'validation_errors': self.validation_errors
            }

        # Count votes by option
        vote_counts: Dict[str, float] = defaultdict(float)
        total_weight = 0.0
        abstentions = 0

        for agent_name, vote in self.votes.items():
            decision = vote.get('decision', 'abstain')
            weight = vote.get('weight', 1.0)
            if decision == 'abstain':
                abstentions += 1
            else:
                vote_counts[decision] += weight
            total_weight += weight

        # Calculate percentages
        results = {}
        for option, weight in vote_counts.items():
            results[option] = {
                'weight': weight,
                'percentage': (weight / total_weight * 100) if total_weight > 0 else 0
            }

        # Calculate attendance and abstention rates
        total_registered_agents = len(self.attendance_log)
        attendance_rate = len(self.votes) / total_registered_agents if total_registered_agents > 0 else 0
        abstention_rate = abstentions / len(self.votes) if self.votes else 0

        # Determine whether quorum is reached based on registered attendance
        total_registered_agents = len(self.attendance_log)
        required_votes = 0
        if total_registered_agents > 0:
            required_votes = int(self.required_quorum * total_registered_agents + 0.9999)  # ceil-like

        quorum_reached = len(self.votes) >= required_votes if required_votes > 0 else False

        # Compute consensus (winner weight / total_weight) and enforce min_votes
        winner = None
        winner_weight = 0.0
        if vote_counts:
            winner, winner_weight = max(vote_counts.items(), key=lambda kv: kv[1])

        winner_ratio = (winner_weight / total_weight) if total_weight > 0 else 0.0

        consensus_met = False
        if quorum_reached and len(self.votes) >= self.min_votes and winner_weight > 0:
            consensus_met = winner_ratio >= self.consensus_threshold

        return {
            'total_votes': len(self.votes),
            'total_weight': total_weight,
            'results': results,
            'quorum_reached': quorum_reached,
            'consensus_met': consensus_met,
            'consensus_winner': winner,
            'consensus_winner_ratio': winner_ratio,
            'attendance_rate': attendance_rate,
            'abstention_rate': abstention_rate,
            'validation_errors': self.validation_errors,
            'conversation_count': len(self.conversation_log)
        }

    def is_complete(self) -> bool:
        """Check if voting is complete with enhanced logic."""
        if self.status != 'active':
            return True

        if self.voting_deadline and time.time() > self.voting_deadline:
            return True

        # Check if quorum reached
        summary = self.get_vote_summary()
        return summary.get('quorum_reached', False)

    def get_attendance_report(self) -> Dict[str, Any]:
        """Get detailed attendance report.

        Returns:
            Attendance statistics and details
        """
        total_agents = len(self.attendance_log)
        voted_agents = len([a for a in self.attendance_log.values() if a['action'] == 'voted'])
        abstained_agents = len([a for a in self.attendance_log.values() if a.get('vote_decision') == 'abstain' and a['action'] == 'voted'])
        absent_agents = len([a for a in self.attendance_log.values() if a['action'] == 'absent'])

        return {
            'total_registered': total_agents,
            'voted': voted_agents,
            'abstained': abstained_agents,
            'absent': absent_agents,
            'attendance_rate': voted_agents / total_agents if total_agents > 0 else 0,
            'details': dict(self.attendance_log)
        }

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversations related to this proposal.

        Returns:
            Conversation statistics and recent messages
        """
        if not self.conversation_log:
            return {'total_messages': 0, 'message_types': {}, 'recent_messages': []}

        # Count message types
        message_types = defaultdict(int)
        for msg in self.conversation_log:
            message_types[msg['type']] += 1

        # Get recent messages (last 5)
        recent_messages = sorted(self.conversation_log, key=lambda x: x['timestamp'], reverse=True)[:5]

        return {
            'total_messages': len(self.conversation_log),
            'message_types': dict(message_types),
            'recent_messages': recent_messages
        }


class MessageBus:
    """Central message bus for inter-agent communication."""

    def __init__(self):
        """Initialize the message bus."""
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queues: Dict[str, Queue] = {}
        self.broadcast_channels: Dict[str, Set[str]] = defaultdict(set)
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Message processing
        self.message_history: List[Message] = []
        self.max_history = 1000

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the message bus.

        Args:
            agent: Agent to register
        """
        agent_name = agent.agent_name
        self.agents[agent_name] = agent
        self.message_queues[agent_name] = Queue()
        self.logger.info(f"Registered agent: {agent_name}")

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from the message bus.

        Args:
            agent_name: Name of agent to unregister
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.message_queues[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")

    def subscribe_to_channel(self, agent_name: str, channel: str) -> None:
        """Subscribe agent to a broadcast channel.

        Args:
            agent_name: Name of the agent
            channel: Channel name
        """
        self.broadcast_channels[channel].add(agent_name)
        self.logger.debug(f"Agent {agent_name} subscribed to channel {channel}")

    def unsubscribe_from_channel(self, agent_name: str, channel: str) -> None:
        """Unsubscribe agent from a broadcast channel.

        Args:
            agent_name: Name of the agent
            channel: Channel name
        """
        if channel in self.broadcast_channels:
            self.broadcast_channels[channel].discard(agent_name)
            self.logger.debug(f"Agent {agent_name} unsubscribed from channel {channel}")

    def send_message(self, message: Message) -> bool:
        """Send a message to its recipient.

        Args:
            message: Message to send

        Returns:
            True if message was delivered
        """
        if message.is_expired():
            self.logger.warning(f"Message {message.message_id} has expired")
            return False

        recipient = message.recipient

        if recipient == "broadcast":
            # Broadcast to all agents
            delivered = 0
            for agent_name, queue in self.message_queues.items():
                try:
                    queue.put(message, timeout=1.0)
                    delivered += 1
                except:
                    self.logger.warning(f"Failed to deliver broadcast message to {agent_name}")
            return delivered > 0

        elif recipient.startswith("channel:"):
            # Broadcast to channel subscribers
            channel = recipient[8:]  # Remove "channel:" prefix
            subscribers = self.broadcast_channels.get(channel, set())
            delivered = 0
            for agent_name in subscribers:
                if agent_name in self.message_queues:
                    try:
                        self.message_queues[agent_name].put(message, timeout=1.0)
                        delivered += 1
                    except:
                        self.logger.warning(f"Failed to deliver channel message to {agent_name}")
            return delivered > 0

        elif recipient in self.message_queues:
            # Direct message
            try:
                self.message_queues[recipient].put(message, timeout=1.0)
                # Store in history
                self.message_history.append(message)
                if len(self.message_history) > self.max_history:
                    self.message_history.pop(0)
                return True
            except:
                self.logger.warning(f"Failed to deliver message to {recipient}")
                return False

        else:
            self.logger.warning(f"Unknown recipient: {recipient}")
            return False

    def get_messages(self, agent_name: str, timeout: float = 0.1) -> List[Message]:
        """Get pending messages for an agent.

        Args:
            agent_name: Name of the agent
            timeout: Timeout for getting messages

        Returns:
            List of messages
        """
        messages = []
        if agent_name not in self.message_queues:
            return messages

        queue = self.message_queues[agent_name]

        # Get all available messages
        while True:
            try:
                message = queue.get_nowait()
                if not message.is_expired():
                    messages.append(message)
                queue.task_done()
            except Empty:
                break

        return messages

    def start_message_processing(self) -> None:
        """Start the message processing loop."""
        self.running = True
        self.executor.submit(self._process_messages_loop)

    def stop_message_processing(self) -> None:
        """Stop the message processing loop."""
        self.running = False
        self.executor.shutdown(wait=True)

    def _process_messages_loop(self) -> None:
        """Main message processing loop."""
        while self.running:
            try:
                # Process expired messages
                current_time = time.time()
                expired_count = 0
                for message in self.message_history[:]:
                    if message.is_expired():
                        self.message_history.remove(message)
                        expired_count += 1

                if expired_count > 0:
                    self.logger.debug(f"Cleaned up {expired_count} expired messages")

                time.sleep(1.0)  # Check every second

            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                time.sleep(5.0)  # Wait longer on error


class VotingSystem:
    """Democratic voting system for agent swarms."""

    def __init__(self, message_bus: MessageBus):
        """Initialize the voting system.

        Args:
            message_bus: Message bus for communication
        """
        self.message_bus = message_bus
        self.logger = logging.getLogger(__name__)
        self.proposals: Dict[str, VoteProposal] = {}
        self.completed_proposals: Dict[str, VoteProposal] = {}

    def create_proposal(self, proposer: str, title: str, description: str,
                       options: List[str], context: str = "",
                       required_quorum: float = 0.5,
                       consensus_threshold: float = 0.66,
                       min_votes: int = 1,
                       voting_deadline: Optional[float] = None) -> str:
        """Create a new voting proposal.

        Args:
            proposer: Name of the proposing agent
            title: Proposal title
            description: Proposal description
            options: List of voting options
            context: Domain context
            required_quorum: Required quorum (0-1)
            voting_deadline: Optional deadline timestamp

        Returns:
            Proposal ID
        """
        import uuid
        proposal_id = str(uuid.uuid4())

        proposal = VoteProposal(
            proposal_id=proposal_id,
            proposer=proposer,
            title=title,
            description=description,
            options=options,
            context=context,
            required_quorum=required_quorum,
            consensus_threshold=consensus_threshold,
            min_votes=min_votes,
            voting_deadline=voting_deadline
        )

        self.proposals[proposal_id] = proposal

        # Broadcast proposal to all agents
        message = Message(
            message_id=str(uuid.uuid4()),
            sender="voting_system",
            recipient="broadcast",
            message_type="vote_proposal",
            content={
                'proposal': {
                    'id': proposal_id,
                    'title': title,
                    'description': description,
                    'options': options,
                    'context': context,
                    'proposer': proposer,
                    'deadline': voting_deadline
                }
            },
            priority=3
        )

        self.message_bus.send_message(message)
        self.logger.info(f"Created proposal: {title} (ID: {proposal_id})")

        return proposal_id

    def cast_vote(self, proposal_id: str, agent: BaseAgent, option: str) -> bool:
        """Cast a vote on a proposal with enhanced validation and tracking.

        Args:
            proposal_id: ID of the proposal
            agent: Agent casting the vote
            option: Chosen option

        Returns:
            True if vote was cast successfully
        """
        if proposal_id not in self.proposals:
            self.logger.warning(f"Proposal {proposal_id} not found")
            return False

        proposal = self.proposals[proposal_id]

        # Record attendance if not already recorded
        if agent.agent_name not in proposal.attendance_log:
            proposal.record_attendance(agent.agent_name, "voting")

        # Get agent's vote using their confidence system
        vote = agent.cast_vote(option, proposal.context)

        # Add vote to proposal with validation
        success = proposal.add_vote(agent.agent_name, vote)

        if success:
            self.logger.info(f"Agent {agent.agent_name} voted on proposal {proposal_id}: {vote['decision']} (weight: {vote.get('weight', 1.0):.2f})")

            # Check if voting is complete
            if proposal.is_complete():
                self._finalize_proposal(proposal_id)
        else:
            self.logger.warning(f"Vote validation failed for agent {agent.agent_name} on proposal {proposal_id}: {proposal.validation_errors[-1] if proposal.validation_errors else 'Unknown error'}")

        return success

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a proposal.

        Args:
            proposal_id: ID of the proposal

        Returns:
            Proposal status or None if not found
        """
        proposal = self.proposals.get(proposal_id) or self.completed_proposals.get(proposal_id)
        if not proposal:
            return None

        summary = proposal.get_vote_summary(total_registered_agents=len(self.message_bus.agents))

        return {
            'proposal_id': proposal.proposal_id,
            'title': proposal.title,
            'status': proposal.status,
            'proposer': proposal.proposer,
            'context': proposal.context,
            'options': proposal.options,
            'vote_summary': summary,
            'deadline': proposal.voting_deadline,
            'time_remaining': (
                max(0, proposal.voting_deadline - time.time())
                if proposal.voting_deadline else None
            )
        }

    def _finalize_proposal(self, proposal_id: str) -> None:
        """Finalize a completed proposal.

        Args:
            proposal_id: ID of the proposal to finalize
        """
        if proposal_id not in self.proposals:
            return

        proposal = self.proposals[proposal_id]

        # Determine winner (use full swarm size for quorum calculations)
        summary = proposal.get_vote_summary(total_registered_agents=len(self.message_bus.agents))
        results = summary['results']

        winner = None
        max_weight = 0
        for option, stats in results.items():
            if stats['weight'] > max_weight:
                max_weight = stats['weight']
                winner = option

        proposal.status = "completed"

        # Move to completed proposals
        self.completed_proposals[proposal_id] = proposal
        del self.proposals[proposal_id]

        # Compute consensus_met (already available in summary)
        consensus_met = summary.get('consensus_met', False)

        # Broadcast results
        message = Message(
            message_id=str(uuid.uuid4()),
            sender="voting_system",
            recipient="broadcast",
            message_type="vote_results",
            content={
                'proposal_id': proposal_id,
                'title': proposal.title,
                'winner': winner,
                'results': summary,
                'consensus_met': consensus_met,
                'finalized_at': time.time()
            },
            priority=3
        )

        self.message_bus.send_message(message)
        if consensus_met:
            self.logger.info(f"Finalized proposal {proposal_id}: Winner = {winner} (consensus met)")
        else:
            self.logger.info(f"Finalized proposal {proposal_id}: Winner = {winner} (NO consensus)")

    def log_conversation(self, proposal_id: str, agent_name: str, message: str, message_type: str = "discussion") -> bool:
        """Log a conversation related to a proposal.

        Args:
            proposal_id: ID of the proposal
            agent_name: Agent making the statement
            message: Conversation content
            message_type: Type of conversation

        Returns:
            True if logged successfully
        """
        proposal = self.proposals.get(proposal_id) or self.completed_proposals.get(proposal_id)
        if not proposal:
            self.logger.warning(f"Proposal {proposal_id} not found for conversation logging")
            return False

        proposal.log_conversation(agent_name, message, message_type)
        self.logger.debug(f"Logged conversation for proposal {proposal_id}: {agent_name} - {message_type}")
        return True

    def get_enhanced_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced status of a proposal including attendance and conversations.

        Args:
            proposal_id: ID of the proposal

        Returns:
            Enhanced proposal status or None if not found
        """
        proposal = self.proposals.get(proposal_id) or self.completed_proposals.get(proposal_id)
        if not proposal:
            return None

        basic_status = self.get_proposal_status(proposal_id)
        if not basic_status:
            return None

        # Add enhanced information
        basic_status.update({
            'attendance_report': proposal.get_attendance_report(),
            'conversation_summary': proposal.get_conversation_summary(),
            'validation_errors': proposal.validation_errors,
            'created_at': proposal.created_at,
            'age_seconds': time.time() - proposal.created_at
        })

        return basic_status


class SwarmCoordinator:
    """Coordinates autonomous operation of agent swarms."""

    def __init__(self, message_bus: MessageBus, voting_system: VotingSystem):
        """Initialize the swarm coordinator.

        Args:
            message_bus: Message bus for communication
            voting_system: Voting system for decisions
        """
        self.message_bus = message_bus
        self.voting_system = voting_system
        self.logger = logging.getLogger(__name__)

        # Swarm state
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_name

        # Termination conditions
        self.max_runtime = 3600  # 1 hour default
        self.max_iterations = 100
        self.loop_detection_window = 10
        self.start_time = time.time()
        self.iteration_count = 0

        # Performance tracking
        self.task_history: List[Dict[str, Any]] = []

    def should_terminate(self) -> tuple[bool, str]:
        """Check if swarm should terminate.

        Returns:
            Tuple of (should_terminate, reason)
        """
        # Check runtime
        if time.time() - self.start_time > self.max_runtime:
            return True, "maximum runtime exceeded"

        # Check iteration limit
        if self.iteration_count > self.max_iterations:
            return True, "maximum iterations exceeded"

        # Check for infinite loops
        if self._detect_loop():
            return True, "infinite loop detected"

        # Check if all tasks completed
        if not self.active_tasks and self.completed_tasks:
            return True, "all tasks completed"

        return False, ""

    def _detect_loop(self) -> bool:
        """Detect if the swarm is in an infinite loop.

        Returns:
            True if loop detected
        """
        if len(self.task_history) < self.loop_detection_window * 2:
            return False

        # Check recent task patterns
        recent_tasks = self.task_history[-self.loop_detection_window:]
        previous_tasks = self.task_history[-(self.loop_detection_window * 2):-self.loop_detection_window]

        # Simple loop detection: same sequence repeating
        if recent_tasks == previous_tasks:
            return True

        return False

    def assign_task(self, task: Dict[str, Any]) -> Optional[str]:
        """Assign a task to the most suitable agent.

        Args:
            task: Task description

        Returns:
            Name of assigned agent or None if no suitable agent
        """
        task_id = task.get('id', str(time.time()))
        task_type = task.get('type', 'general')
        context = task.get('context', '')

        best_agent = None
        best_score = 0

        # Find best agent for task
        for agent_name, agent in self.message_bus.agents.items():
            # Skip if agent is busy (simplified - could be more sophisticated)
            if agent_name in self.task_assignments.values():
                continue

            # Calculate suitability score
            score = self._calculate_agent_suitability(agent, task_type, context)

            if score > best_score:
                best_score = score
                best_agent = agent_name

        if best_agent:
            self.active_tasks[task_id] = task
            self.task_assignments[task_id] = best_agent

            # Send task assignment message
            message = Message(
                message_id=str(uuid.uuid4()),
                sender="coordinator",
                recipient=best_agent,
                message_type="task_assignment",
                content={'task': task},
                priority=4
            )
            self.message_bus.send_message(message)

            self.logger.info(f"Assigned task {task_id} to agent {best_agent}")
            return best_agent

        return None

    def _calculate_agent_suitability(self, agent: BaseAgent, task_type: str, context: str) -> float:
        """Calculate how suitable an agent is for a task.

        Args:
            agent: Agent to evaluate
            task_type: Type of task
            context: Task context

        Returns:
            Suitability score (0-1)
        """
        # Base score from confidence
        base_score = agent.confidence.overall

        # Boost for domain expertise
        domain_boost = agent.confidence.get_domain_confidence(context) * 0.3
        base_score += domain_boost

        # Boost for relevant tools
        tool_boost = 0
        for tool_name in agent.get_available_tools():
            if task_type.lower() in tool_name.lower():
                tool_boost += agent.confidence.get_tool_confidence(tool_name) * 0.2

        base_score += min(tool_boost, 0.3)  # Cap tool boost

        return min(base_score, 1.0)

    def report_task_completion(self, task_id: str, agent_name: str, success: bool,
                             result: Any = None) -> None:
        """Report task completion.

        Args:
            task_id: ID of completed task
            agent_name: Name of agent that completed task
            success: Whether task was successful
            result: Task result
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task['completed_at'] = time.time()
            task['success'] = success
            task['result'] = result
            task['agent'] = agent_name

            # Move to completed
            self.completed_tasks[task_id] = task
            del self.active_tasks[task_id]
            del self.task_assignments[task_id]

            # Update agent's confidence
            agent = self.message_bus.agents.get(agent_name)
            if agent:
                agent.record_vote_outcome(success)  # Treat as vote outcome

            # Record in history
            self.task_history.append({
                'task_id': task_id,
                'agent': agent_name,
                'type': task.get('type'),
                'success': success,
                'timestamp': task['completed_at']
            })

            self.logger.info(f"Task {task_id} completed by {agent_name}: {'success' if success else 'failed'}")

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get overall swarm status.

        Returns:
            Status dictionary
        """
        total_tasks = len(self.active_tasks) + len(self.completed_tasks)
        completed_tasks = len(self.completed_tasks)
        success_rate = (
            sum(1 for t in self.completed_tasks.values() if t.get('success'))
            / completed_tasks * 100
        ) if completed_tasks > 0 else 0

        should_term, reason = self.should_terminate()

        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'success_rate': success_rate,
            'runtime': time.time() - self.start_time,
            'iterations': self.iteration_count,
            'should_terminate': should_term,
            'termination_reason': reason,
            'agents': len(self.message_bus.agents)
        }


# Import here to avoid circular imports
import uuid
