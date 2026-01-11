"""Swarm Monitoring & Alerting - Production Monitoring for Democratic AI Agent Swarm.

This module provides comprehensive monitoring, alerting, and analysis capabilities
for the democratic AI agent swarm, including conversation log persistence,
performance analysis, anomaly detection, and automated alerting.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Set, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from enum import Enum

from swarm_observability import SwarmObservabilityManager, A2AMessage
from swarm_communication import Message, MessageBus, VotingSystem, SwarmCoordinator


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts that can be generated."""
    AGENT_FAILURE = "agent_failure"
    COMMUNICATION_ERROR = "communication_error"
    VOTING_DEADLOCK = "voting_deadlock"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_VIOLATION = "security_violation"
    LOOP_DETECTED = "loop_detected"
    CONSENSUS_FAILURE = "consensus_failure"


@dataclass
class Alert:
    """Represents an alert in the system."""

    alert_id: str = field(default_factory=lambda: f"alert_{int(time.time())}_{os.urandom(4).hex()}")
    timestamp: float = field(default_factory=time.time)
    severity: AlertSeverity = AlertSeverity.INFO
    alert_type: AlertType = AlertType.AGENT_FAILURE
    title: str = ""
    description: str = ""
    agent_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[float] = None
    resolution_note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp,
            'severity': self.severity.value,
            'alert_type': self.alert_type.value,
            'title': self.title,
            'description': self.description,
            'agent_name': self.agent_name,
            'metadata': self.metadata,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at,
            'resolution_note': self.resolution_note
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create alert from dictionary."""
        # Convert string enums back
        data['severity'] = AlertSeverity(data['severity'])
        data['alert_type'] = AlertType(data['alert_type'])
        return cls(**data)


class ConversationLogger:
    """Persistent storage for all agent conversations and communications."""

    def __init__(self, db_path: str = "logs/agent_conversations.db"):
        """Initialize conversation logger with SQLite database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_database()

        # In-memory cache for recent conversations
        self.recent_conversations: deque = deque(maxlen=1000)

    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    message_id TEXT UNIQUE NOT NULL,
                    timestamp REAL NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    correlation_id TEXT,
                    conversation_thread TEXT,
                    metadata TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    weight REAL NOT NULL,
                    confidence REAL NOT NULL,
                    context TEXT,
                    timestamp REAL NOT NULL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    agent_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    success BOOLEAN,
                    result TEXT,
                    started_at REAL,
                    completed_at REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_votes_proposal_id ON votes(proposal_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')

    def log_message(self, message: Union[Message, A2AMessage]) -> None:
        """Log a message to persistent storage.

        Args:
            message: Message to log (internal Message or A2AMessage)
        """
        try:
            if isinstance(message, A2AMessage):
                # Convert A2A message to database format
                conversation_id = message.conversation_id or message.id
                correlation_id = message.correlation_id
                metadata = json.dumps(message.metadata) if message.metadata else None

                # Generate unique message ID if needed
                message_id = message.id
                if not message_id or message_id.startswith('alert_'):
                    message_id = f"msg_{int(time.time() * 1000000)}_{os.urandom(4).hex()}"

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO conversations
                        (conversation_id, message_id, timestamp, sender, recipient,
                         message_type, content, correlation_id, conversation_thread, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        conversation_id,
                        message_id,
                        message.timestamp if isinstance(message.timestamp, (int, float))
                        else datetime.fromisoformat(message.timestamp[:-1] + '+00:00').timestamp(),
                        message.sender,
                        message.recipient,
                        message.message_type.value if hasattr(message.message_type, 'value')
                        else str(message.message_type),
                        json.dumps(message.content),
                        correlation_id,
                        message.in_reply_to,
                        metadata
                    ))

            else:
                # Convert internal Message to database format
                conversation_id = message.correlation_id or message.message_id
                metadata = json.dumps(message.content.get('_a2a_metadata', {})) if '_a2a_metadata' in message.content else None

                # Generate unique message ID if needed
                message_id = message.message_id
                if not message_id or message_id.startswith('alert_'):
                    message_id = f"msg_{int(time.time() * 1000000)}_{os.urandom(4).hex()}"

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO conversations
                        (conversation_id, message_id, timestamp, sender, recipient,
                         message_type, content, correlation_id, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        conversation_id,
                        message_id,
                        message.timestamp,
                        message.sender,
                        message.recipient,
                        message.message_type,
                        json.dumps(message.content),
                        message.correlation_id,
                        metadata
                    ))

            # Add to recent cache
            self.recent_conversations.append(message)

        except Exception as e:
            self.logger.error(f"Failed to log message: {e}")

    def log_vote(self, proposal_id: str, agent_name: str, vote: Dict[str, Any]) -> None:
        """Log a vote to persistent storage.

        Args:
            proposal_id: ID of the voting proposal
            agent_name: Name of the voting agent
            vote: Vote details
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO votes
                    (proposal_id, agent_name, decision, weight, confidence, context, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    proposal_id,
                    agent_name,
                    vote.get('decision', 'unknown'),
                    vote.get('weight', 0.0),
                    vote.get('confidence', 0.0),
                    vote.get('context', ''),
                    time.time()
                ))
        except Exception as e:
            self.logger.error(f"Failed to log vote: {e}")

    def log_task(self, task_id: str, agent_name: str, task_type: str, status: str,
                 success: Optional[bool] = None, result: Optional[Any] = None) -> None:
        """Log a task to persistent storage.

        Args:
            task_id: Unique task identifier
            agent_name: Agent handling the task
            task_type: Type of task
            status: Current status
            success: Success status if completed
            result: Task result if available
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if task already exists
                existing = conn.execute(
                    'SELECT id FROM tasks WHERE task_id = ?', (task_id,)
                ).fetchone()

                if existing:
                    # Update existing task
                    update_fields = ['status = ?']
                    params = [status]

                    if success is not None:
                        update_fields.append('success = ?')
                        params.append(success)

                    if result is not None:
                        update_fields.append('result = ?')
                        params.append(json.dumps(result) if not isinstance(result, str) else result)

                    if status in ['completed', 'failed']:
                        update_fields.append('completed_at = ?')
                        params.append(time.time())

                    params.append(task_id)

                    conn.execute(f'''
                        UPDATE tasks SET {', '.join(update_fields)}
                        WHERE task_id = ?
                    ''', params)
                else:
                    # Insert new task
                    conn.execute('''
                        INSERT INTO tasks
                        (task_id, agent_name, task_type, status, success, result, started_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        task_id,
                        agent_name,
                        task_type,
                        status,
                        success,
                        json.dumps(result) if result is not None and not isinstance(result, str) else result,
                        time.time()
                    ))

        except Exception as e:
            self.logger.error(f"Failed to log task: {e}")

    def get_conversation_history(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation.

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return

        Returns:
            List of conversation messages
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute('''
                    SELECT * FROM conversations
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (conversation_id, limit)).fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []

    def get_agent_communications(self, agent_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get communication statistics for an agent.

        Args:
            agent_name: Name of the agent
            hours: Number of hours to look back

        Returns:
            Communication statistics
        """
        try:
            cutoff_time = time.time() - (hours * 3600)

            with sqlite3.connect(self.db_path) as conn:
                # Messages sent by agent
                sent_count = conn.execute('''
                    SELECT COUNT(*) FROM conversations
                    WHERE sender = ? AND timestamp > ?
                ''', (agent_name, cutoff_time)).fetchone()[0]

                # Messages received by agent
                received_count = conn.execute('''
                    SELECT COUNT(*) FROM conversations
                    WHERE recipient = ? AND timestamp > ?
                ''', (agent_name, cutoff_time)).fetchone()[0]

                # Task statistics
                task_stats = conn.execute('''
                    SELECT status, COUNT(*) as count
                    FROM tasks
                    WHERE agent_name = ? AND created_at > ?
                    GROUP BY status
                ''', (agent_name, cutoff_time)).fetchall()

                task_summary = {row[0]: row[1] for row in task_stats}

                return {
                    'agent_name': agent_name,
                    'time_period_hours': hours,
                    'messages_sent': sent_count,
                    'messages_received': received_count,
                    'tasks_by_status': task_summary,
                    'total_communications': sent_count + received_count
                }

        except Exception as e:
            self.logger.error(f"Failed to get agent communications: {e}")
            return {}

    def get_system_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get overall system communication metrics.

        Args:
            hours: Number of hours to look back

        Returns:
            System-wide metrics
        """
        try:
            cutoff_time = time.time() - (hours * 3600)

            with sqlite3.connect(self.db_path) as conn:
                # Total messages
                total_messages = conn.execute('''
                    SELECT COUNT(*) FROM conversations WHERE timestamp > ?
                ''', (cutoff_time,)).fetchone()[0]

                # Messages by type
                type_stats = conn.execute('''
                    SELECT message_type, COUNT(*) as count
                    FROM conversations
                    WHERE timestamp > ?
                    GROUP BY message_type
                    ORDER BY count DESC
                ''', (cutoff_time,)).fetchall()

                # Active conversations
                active_conversations = conn.execute('''
                    SELECT COUNT(DISTINCT conversation_id) FROM conversations
                    WHERE timestamp > ?
                ''', (cutoff_time,)).fetchone()[0]

                # Task completion rates
                task_completion = conn.execute('''
                    SELECT
                        COUNT(CASE WHEN success = 1 THEN 1 END) as successful,
                        COUNT(CASE WHEN success = 0 THEN 1 END) as failed,
                        COUNT(*) as total
                    FROM tasks
                    WHERE created_at > ?
                ''', (cutoff_time,)).fetchall()[0]

                success_rate = (task_completion[0] / task_completion[2] * 100) if task_completion[2] > 0 else 0

                return {
                    'time_period_hours': hours,
                    'total_messages': total_messages,
                    'messages_by_type': {row[0]: row[1] for row in type_stats},
                    'active_conversations': active_conversations,
                    'task_completion': {
                        'successful': task_completion[0],
                        'failed': task_completion[1],
                        'total': task_completion[2],
                        'success_rate': success_rate
                    }
                }

        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}


class PerformanceAnalyzer:
    """Analyzes swarm performance and detects anomalies."""

    def __init__(self, conversation_logger: ConversationLogger):
        """Initialize performance analyzer.

        Args:
            conversation_logger: Logger for accessing historical data
        """
        self.logger = logging.getLogger(__name__)
        self.conversation_logger = conversation_logger

        # Performance baselines
        self.baselines: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            'message_rate_drop': 0.5,  # 50% drop in message rate
            'task_failure_rate': 0.3,  # 30% task failure rate
            'response_time_increase': 2.0,  # 2x increase in response time
            'confidence_drop': 0.2  # 20% drop in average confidence
        }

    def analyze_performance(self, hours: int = 1) -> Dict[str, Any]:
        """Analyze recent performance metrics.

        Args:
            hours: Hours to analyze

        Returns:
            Performance analysis results
        """
        metrics = self.conversation_logger.get_system_metrics(hours)

        analysis = {
            'time_period_hours': hours,
            'overall_health': 'healthy',
            'issues': [],
            'recommendations': [],
            'metrics': metrics
        }

        # Analyze message patterns
        message_analysis = self._analyze_message_patterns(metrics)
        analysis.update(message_analysis)

        # Analyze task performance
        task_analysis = self._analyze_task_performance(metrics)
        analysis.update(task_analysis)

        # Update baselines
        self._update_baselines(metrics)

        # Determine overall health
        if analysis['issues']:
            issue_severities = [issue.get('severity', 'low') for issue in analysis['issues']]
            if 'critical' in issue_severities:
                analysis['overall_health'] = 'critical'
            elif 'high' in issue_severities:
                analysis['overall_health'] = 'unhealthy'
            else:
                analysis['overall_health'] = 'warning'

        return analysis

    def _analyze_message_patterns(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze message communication patterns."""
        issues = []
        recommendations = []

        total_messages = metrics.get('total_messages', 0)
        expected_rate = self.baselines.get('message_rate', {}).get('average', 10)  # messages per hour

        if expected_rate > 0:
            actual_rate = total_messages / metrics.get('time_period_hours', 1)
            rate_ratio = actual_rate / expected_rate

            if rate_ratio < self.anomaly_thresholds['message_rate_drop']:
                issues.append({
                    'type': 'communication_drop',
                    'severity': 'high',
                    'description': f'Message rate dropped to {rate_ratio:.2f}x of expected ({actual_rate:.1f} vs {expected_rate:.1f} msg/hour)'
                })
                recommendations.append('Check agent connectivity and message bus health')

        return {'communication_issues': issues, 'communication_recommendations': recommendations}

    def _analyze_task_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task completion performance."""
        issues = []
        recommendations = []

        task_completion = metrics.get('task_completion', {})
        success_rate = task_completion.get('success_rate', 0)

        if success_rate < (1 - self.anomaly_thresholds['task_failure_rate']) * 100:
            issues.append({
                'type': 'high_failure_rate',
                'severity': 'high',
                'description': f'Task success rate is {success_rate:.1f}%, below acceptable threshold'
            })
            recommendations.append('Investigate failing tasks and agent performance')

        return {'task_issues': issues, 'task_recommendations': recommendations}

    def _update_baselines(self, metrics: Dict[str, Any]) -> None:
        """Update performance baselines with recent data."""
        # Simple moving average for baselines
        alpha = 0.1  # Learning rate

        # Message rate baseline
        current_rate = metrics.get('total_messages', 0) / metrics.get('time_period_hours', 1)
        existing_avg = self.baselines['message_rate'].get('average', current_rate)
        self.baselines['message_rate']['average'] = existing_avg + alpha * (current_rate - existing_avg)

    def detect_anomalies(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect performance anomalies.

        Args:
            current_metrics: Current performance metrics

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check for sudden changes in key metrics
        for metric_name, current_value in current_metrics.items():
            if isinstance(current_value, (int, float)):
                baseline = self.baselines.get(metric_name, {}).get('average')
                if baseline and baseline > 0:
                    change_ratio = current_value / baseline
                    if change_ratio < 0.5 or change_ratio > 2.0:  # 50% change threshold
                        anomalies.append({
                            'metric': metric_name,
                            'baseline': baseline,
                            'current': current_value,
                            'change_ratio': change_ratio,
                            'severity': 'high' if abs(change_ratio - 1) > 1 else 'medium'
                        })

        return anomalies


class AlertManager:
    """Manages alerts and notifications for the swarm system."""

    def __init__(self, conversation_logger: ConversationLogger):
        """Initialize alert manager.

        Args:
            conversation_logger: Logger for alert persistence
        """
        self.logger = logging.getLogger(__name__)
        self.conversation_logger = conversation_logger

        # Active alerts
        self.active_alerts: Dict[str, Alert] = {}

        # Alert handlers
        self.alert_handlers: Dict[AlertType, List[Callable]] = defaultdict(list)

        # Alert persistence
        self._init_alert_storage()

    def _init_alert_storage(self) -> None:
        """Initialize alert storage in the conversation database."""
        try:
            with sqlite3.connect(self.conversation_logger.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id TEXT PRIMARY KEY,
                        timestamp REAL NOT NULL,
                        severity TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        agent_name TEXT,
                        metadata TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        resolved_at REAL,
                        resolution_note TEXT,
                        created_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
        except Exception as e:
            self.logger.error(f"Failed to initialize alert storage: {e}")

    def raise_alert(self, severity: AlertSeverity, alert_type: AlertType,
                   title: str, description: str, agent_name: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Raise a new alert.

        Args:
            severity: Alert severity level
            alert_type: Type of alert
            title: Alert title
            description: Alert description
            agent_name: Name of affected agent (if applicable)
            metadata: Additional alert metadata

        Returns:
            Alert ID
        """
        alert = Alert(
            severity=severity,
            alert_type=alert_type,
            title=title,
            description=description,
            agent_name=agent_name,
            metadata=metadata or {}
        )

        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self._persist_alert(alert)

        # Trigger handlers
        self._trigger_handlers(alert)

        self.logger.warning(f"Alert raised: {title} (severity: {severity.value})")

        return alert.alert_id

    def resolve_alert(self, alert_id: str, resolution_note: Optional[str] = None) -> bool:
        """Resolve an active alert.

        Args:
            alert_id: ID of the alert to resolve
            resolution_note: Optional note about the resolution

        Returns:
            True if alert was resolved
        """
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = time.time()
        alert.resolution_note = resolution_note

        # Update persistence
        self._update_alert(alert)

        # Remove from active alerts
        del self.active_alerts[alert_id]

        self.logger.info(f"Alert resolved: {alert.title}")

        return True

    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity.

        Args:
            severity_filter: Only return alerts of this severity

        Returns:
            List of active alerts
        """
        alerts = list(self.active_alerts.values())

        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def register_alert_handler(self, alert_type: AlertType, handler: Callable[[Alert], None]) -> None:
        """Register a handler for a specific alert type.

        Args:
            alert_type: Type of alert to handle
            handler: Handler function that takes an Alert object
        """
        self.alert_handlers[alert_type].append(handler)

    def _trigger_handlers(self, alert: Alert) -> None:
        """Trigger all handlers for an alert type."""
        for handler in self.alert_handlers[alert.alert_type]:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")

    def _persist_alert(self, alert: Alert) -> None:
        """Persist alert to database."""
        try:
            with sqlite3.connect(self.conversation_logger.db_path) as conn:
                conn.execute('''
                    INSERT INTO alerts
                    (alert_id, timestamp, severity, alert_type, title, description,
                     agent_name, metadata, resolved, resolved_at, resolution_note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    alert.timestamp,
                    alert.severity.value,
                    alert.alert_type.value,
                    alert.title,
                    alert.description,
                    alert.agent_name,
                    json.dumps(alert.metadata),
                    alert.resolved,
                    alert.resolved_at,
                    alert.resolution_note
                ))
        except Exception as e:
            self.logger.error(f"Failed to persist alert: {e}")

    def _update_alert(self, alert: Alert) -> None:
        """Update alert in database."""
        try:
            with sqlite3.connect(self.conversation_logger.db_path) as conn:
                conn.execute('''
                    UPDATE alerts SET
                        resolved = ?, resolved_at = ?, resolution_note = ?
                    WHERE alert_id = ?
                ''', (
                    alert.resolved,
                    alert.resolved_at,
                    alert.resolution_note,
                    alert.alert_id
                ))
        except Exception as e:
            self.logger.error(f"Failed to update alert: {e}")

    def get_alert_history(self, hours: int = 24,
                         severity_filter: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """Get alert history from database.

        Args:
            hours: Hours to look back
            severity_filter: Filter by severity

        Returns:
            List of historical alerts
        """
        try:
            cutoff_time = time.time() - (hours * 3600)

            with sqlite3.connect(self.conversation_logger.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = 'SELECT * FROM alerts WHERE timestamp > ?'
                params = [cutoff_time]

                if severity_filter:
                    query += ' AND severity = ?'
                    params.append(severity_filter.value)

                query += ' ORDER BY timestamp DESC'

                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Failed to get alert history: {e}")
            return []


class SwarmMonitor:
    """Comprehensive monitoring system for the democratic agent swarm."""

    def __init__(self, observability_manager: SwarmObservabilityManager):
        """Initialize swarm monitor.

        Args:
            observability_manager: The observability manager to monitor
        """
        self.observability = observability_manager
        self.logger = logging.getLogger(__name__)

        # Monitoring components
        self.conversation_logger = ConversationLogger()
        self.performance_analyzer = PerformanceAnalyzer(self.conversation_logger)
        self.alert_manager = AlertManager(self.conversation_logger)

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds

        # Setup default alert handlers
        self._setup_default_alert_handlers()

        # Integrate with observability system
        self._integrate_with_observability()

    def _integrate_with_observability(self) -> None:
        """Integrate monitoring with the observability system."""
        # Override message sending to log conversations
        original_send_message = self.observability.message_bus.send_message

        def monitored_send_message(message: Message) -> bool:
            success = original_send_message(message)
            if success:
                self.conversation_logger.log_message(message)
            return success

        self.observability.message_bus.send_message = monitored_send_message

        # Override A2A message sending
        original_send_a2a = self.observability.a2a_handler.send_a2a_message

        def monitored_send_a2a(message: A2AMessage) -> bool:
            success = original_send_a2a(message)
            if success:
                self.conversation_logger.log_message(message)
            return success

        self.observability.a2a_handler.send_a2a_message = monitored_send_a2a

        # Override task reporting
        original_report_task = self.observability.coordinator.report_task_completion

        def monitored_report_task(task_id: str, agent_name: str, success: bool, result: Any = None):
            # Log task
            status = 'completed' if success else 'failed'
            self.conversation_logger.log_task(task_id, agent_name, 'unknown', status, success, result)

            # Call original
            original_report_task(task_id, agent_name, success, result)

        self.observability.coordinator.report_task_completion = monitored_report_task

    def _setup_default_alert_handlers(self) -> None:
        """Setup default alert handlers for common issues."""

        # Agent failure handler
        def handle_agent_failure(alert: Alert):
            agent_name = alert.agent_name
            if agent_name:
                self.logger.error(f"Agent {agent_name} failure detected: {alert.description}")
                # Could implement automatic agent restart, failover, etc.

        self.alert_manager.register_alert_handler(AlertType.AGENT_FAILURE, handle_agent_failure)

        # Performance degradation handler
        def handle_performance_alert(alert: Alert):
            self.logger.warning(f"Performance issue detected: {alert.description}")
            # Could implement automatic scaling, resource allocation, etc.

        self.alert_manager.register_alert_handler(AlertType.PERFORMANCE_DEGRADATION, handle_performance_alert)

        # Communication error handler
        def handle_communication_error(alert: Alert):
            self.logger.error(f"Communication error: {alert.description}")
            # Could implement retry logic, alternative communication paths, etc.

        self.alert_manager.register_alert_handler(AlertType.COMMUNICATION_ERROR, handle_communication_error)

    def start_monitoring(self) -> None:
        """Start comprehensive monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Swarm monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Swarm monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                current_time = time.time()

                # Periodic health check
                if current_time - self.last_health_check > self.health_check_interval:
                    self._perform_health_check()
                    self.last_health_check = current_time

                # Check for anomalies
                self._check_for_anomalies()

                # Process active alerts
                self._process_alerts()

                time.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30.0)

    def _perform_health_check(self) -> None:
        """Perform comprehensive health check."""
        try:
            # Get current status
            status = self.observability.get_comprehensive_status()

            # Check agent health
            coordinator_status = status.get('coordinator', {})
            agents_active = coordinator_status.get('agents', 0)

            if agents_active == 0:
                self.alert_manager.raise_alert(
                    AlertSeverity.CRITICAL,
                    AlertType.AGENT_FAILURE,
                    "No Active Agents",
                    "No agents are currently active in the swarm",
                    metadata={'agents_count': agents_active}
                )

            # Check message bus health
            message_bus_status = status.get('message_bus', {})
            registered_agents = message_bus_status.get('registered_agents', 0)

            if registered_agents < agents_active:
                self.alert_manager.raise_alert(
                    AlertSeverity.WARNING,
                    AlertType.COMMUNICATION_ERROR,
                    "Message Bus Registration Mismatch",
                    f"Message bus shows {registered_agents} registered agents but coordinator shows {agents_active}",
                    metadata={'registered': registered_agents, 'coordinator': agents_active}
                )

            # Check task performance
            completed_tasks = coordinator_status.get('completed_tasks', 0)
            if completed_tasks > 0:
                success_rate = coordinator_status.get('success_rate', 0)
                if success_rate < 50:  # Less than 50% success rate
                    self.alert_manager.raise_alert(
                        AlertSeverity.ERROR,
                        AlertType.PERFORMANCE_DEGRADATION,
                        "Low Task Success Rate",
                        f"Task success rate is {success_rate:.1f}%, below acceptable threshold",
                        metadata={'success_rate': success_rate, 'completed_tasks': completed_tasks}
                    )

            # Check for termination conditions
            if coordinator_status.get('should_terminate', False):
                reason = coordinator_status.get('termination_reason', 'unknown')
                self.alert_manager.raise_alert(
                    AlertSeverity.WARNING,
                    AlertType.AGENT_FAILURE,
                    "Swarm Termination Recommended",
                    f"Coordinator recommends swarm termination: {reason}",
                    metadata={'reason': reason}
                )

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    def _check_for_anomalies(self) -> None:
        """Check for performance anomalies."""
        try:
            # Analyze recent performance
            analysis = self.performance_analyzer.analyze_performance(hours=1)

            # Raise alerts for issues
            for issue in analysis.get('issues', []):
                severity_map = {
                    'low': AlertSeverity.INFO,
                    'medium': AlertSeverity.WARNING,
                    'high': AlertSeverity.ERROR,
                    'critical': AlertSeverity.CRITICAL
                }

                alert_severity = severity_map.get(issue.get('severity', 'low'), AlertSeverity.INFO)

                self.alert_manager.raise_alert(
                    alert_severity,
                    AlertType.PERFORMANCE_DEGRADATION,
                    f"Performance Issue: {issue.get('type', 'unknown')}",
                    issue.get('description', ''),
                    metadata={'analysis': analysis, 'issue': issue}
                )

        except Exception as e:
            self.logger.error(f"Anomaly check failed: {e}")

    def _process_alerts(self) -> None:
        """Process active alerts and check for auto-resolution."""
        # This could implement auto-resolution logic for certain alert types
        pass

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status."""
        active_alerts = self.alert_manager.get_active_alerts()
        alert_counts = defaultdict(int)
        for alert in active_alerts:
            alert_counts[alert.severity.value] += 1

        return {
            'monitoring_active': self.monitoring_active,
            'conversation_logs': len(self.conversation_logger.recent_conversations),
            'active_alerts': {
                'total': len(active_alerts),
                'by_severity': dict(alert_counts)
            },
            'performance_analysis': self.performance_analyzer.analyze_performance(hours=1),
            'system_metrics': self.conversation_logger.get_system_metrics(hours=1),
            'alert_history': self.alert_manager.get_alert_history(hours=24)
        }
