"""Swarm Observability & Telemetry - Production Monitoring for Democratic AI Agent Swarm.

This module provides comprehensive observability, telemetry, and communication protocols
for democratic AI agent swarms, including support for industry standards like OpenTelemetry,
A2A protocol, and persistent message queuing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

# Third-party integrations (optional)
try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.jaeger import JaegerExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

try:
    import pika  # RabbitMQ
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

from base_agent import BaseAgent
from swarm_communication import Message, MessageBus, SwarmCoordinator, VotingSystem


class MessagePriority(Enum):
    """Standardized message priority levels."""
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    DEBUG = 1


class MessageType(Enum):
    """Standardized message types for A2A protocol compliance."""
    # Core agent communication
    AGENT_HANDSHAKE = "agent_handshake"
    AGENT_STATUS = "agent_status"
    AGENT_HEARTBEAT = "agent_heartbeat"

    # Task management
    TASK_ASSIGNMENT = "task_assignment"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"

    # Democratic processes
    VOTE_PROPOSAL = "vote_proposal"
    VOTE_CAST = "vote_cast"
    VOTE_RESULTS = "vote_results"
    CONSENSUS_REACHED = "consensus_reached"

    # Knowledge sharing
    KNOWLEDGE_SHARE = "knowledge_share"
    KNOWLEDGE_REQUEST = "knowledge_request"
    KNOWLEDGE_UPDATE = "knowledge_update"

    # System coordination
    SWARM_STATUS = "swarm_status"
    SWARM_CONFIG = "swarm_config"
    SWARM_TERMINATION = "swarm_termination"

    # Error handling
    ERROR_REPORT = "error_report"
    EXCEPTION_RAISED = "exception_raised"
    RECOVERY_ACTION = "recovery_action"


@dataclass
class A2AMessage:
    """A2A (Agent-to-Agent) protocol compliant message format."""

    # Required A2A fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.AGENT_STATUS

    # Optional A2A fields
    correlation_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    conversation_id: Optional[str] = None

    # Content
    content: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Protocol compliance
    protocol_version: str = "A2A/1.0"
    content_type: str = "application/json"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type.value,
            'correlation_id': self.correlation_id,
            'in_reply_to': self.in_reply_to,
            'conversation_id': self.conversation_id,
            'content': self.content,
            'metadata': self.metadata,
            'protocol_version': self.protocol_version,
            'content_type': self.content_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create from dictionary."""
        # Convert string message_type back to enum
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        return cls(**data)


class TelemetryCollector:
    """Centralized telemetry collection for agent swarm observability."""

    def __init__(self):
        """Initialize telemetry collector."""
        self.logger = logging.getLogger(__name__)

        # Telemetry data
        self.metrics: Dict[str, Any] = defaultdict(dict)
        self.traces: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []

        # Integrations
        self._setup_opentelemetry()
        self._setup_langsmith()
        self._setup_langfuse()

        # Performance tracking
        self.start_time = time.time()
        self.event_counts: Dict[str, int] = defaultdict(int)

    def _setup_opentelemetry(self) -> None:
        """Setup OpenTelemetry integration."""
        if not OPENTELEMETRY_AVAILABLE:
            self.logger.warning("OpenTelemetry not available - install with: pip install opentelemetry-sdk opentelemetry-exporter-jaeger opentelemetry-exporter-prometheus")
            return

        # Setup tracing
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()

        # Jaeger exporter for traces
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=14268,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Prometheus exporter for metrics
        prometheus_reader = PrometheusMetricReader()
        metric_reader = PeriodicExportingMetricReader(
            exporter=prometheus_reader,
            export_interval_millis=10000
        )
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)

        # Define metrics
        self.agent_count = self.meter.create_counter(
            "agent_count",
            description="Number of active agents"
        )
        self.message_count = self.meter.create_counter(
            "message_count",
            description="Number of messages processed"
        )
        self.task_success_rate = self.meter.create_histogram(
            "task_success_rate",
            description="Task success rate distribution"
        )

        self.logger.info("OpenTelemetry initialized")

    def _setup_langsmith(self) -> None:
        """Setup LangSmith integration."""
        if not LANGSMITH_AVAILABLE:
            self.logger.warning("LangSmith not available - install with: pip install langsmith")
            return

        api_key = os.getenv("LANGSMITH_API_KEY")
        if api_key:
            self.langsmith = LangSmithClient(api_key=api_key)
            self.logger.info("LangSmith initialized")
        else:
            self.langsmith = None
            self.logger.warning("LangSmith API key not found")

    def _setup_langfuse(self) -> None:
        """Setup LangFuse integration."""
        if not LANGFUSE_AVAILABLE:
            self.logger.warning("LangFuse not available - install with: pip install langfuse")
            return

        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST")

        if public_key and secret_key:
            self.langfuse = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            )
            self.logger.info("LangFuse initialized")
        else:
            self.langfuse = None
            self.logger.warning("LangFuse credentials not found")

    def record_event(self, event_type: str, data: Dict[str, Any],
                    agent_name: Optional[str] = None) -> None:
        """Record a telemetry event."""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'agent_name': agent_name,
            'data': data
        }

        self.event_counts[event_type] += 1

        # Add to appropriate storage
        if event_type.endswith('_log'):
            self.logs.append(event)
        elif event_type.endswith('_trace'):
            self.traces.append(event)
        else:
            # Store in metrics
            if agent_name:
                if agent_name not in self.metrics:
                    self.metrics[agent_name] = {}
                self.metrics[agent_name][event_type] = data
            else:
                self.metrics['swarm'][event_type] = data

        # Send to integrations
        self._send_to_integrations(event)

    def _send_to_integrations(self, event: Dict[str, Any]) -> None:
        """Send event to configured integrations."""
        try:
            # OpenTelemetry metrics
            if OPENTELEMETRY_AVAILABLE and hasattr(self, 'message_count'):
                if event['event_type'] == 'message_processed':
                    self.message_count.add(1)
                elif event['event_type'] == 'task_completed':
                    success = event['data'].get('success', False)
                    self.task_success_rate.record(1.0 if success else 0.0)

            # LangSmith traces
            if hasattr(self, 'langsmith') and self.langsmith:
                if event['event_type'] in ['agent_action', 'tool_execution']:
                    self.langsmith.create_run(
                        name=f"{event['agent_name']}_{event['event_type']}",
                        inputs=event['data'].get('inputs', {}),
                        outputs=event['data'].get('outputs', {}),
                        run_type="chain"
                    )

            # LangFuse traces
            if hasattr(self, 'langfuse') and self.langfuse:
                if event['event_type'] in ['agent_action', 'tool_execution']:
                    self.langfuse.trace(
                        name=f"{event['agent_name']}_{event['event_type']}",
                        input=event['data'].get('inputs', {}),
                        output=event['data'].get('outputs', {}),
                        metadata={
                            'agent_name': event.get('agent_name'),
                            'timestamp': event['timestamp']
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error sending to integrations: {e}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        runtime = time.time() - self.start_time

        return {
            'runtime_seconds': runtime,
            'total_events': sum(self.event_counts.values()),
            'event_counts': dict(self.event_counts),
            'active_agents': len([k for k in self.metrics.keys() if k != 'swarm']),
            'integrations': {
                'opentelemetry': OPENTELEMETRY_AVAILABLE,
                'langsmith': LANGSMITH_AVAILABLE and hasattr(self, 'langsmith') and self.langsmith is not None,
                'langfuse': LANGFUSE_AVAILABLE and hasattr(self, 'langfuse') and self.langfuse is not None
            }
        }


class PersistentMessageQueue:
    """Persistent message queue using RabbitMQ or Redis."""

    def __init__(self, queue_type: str = "rabbitmq"):
        """Initialize persistent message queue.

        Args:
            queue_type: Type of queue ('rabbitmq', 'redis', or 'memory')
        """
        self.queue_type = queue_type
        self.logger = logging.getLogger(__name__)

        if queue_type == "rabbitmq" and PIKA_AVAILABLE:
            self._setup_rabbitmq()
        elif queue_type == "redis":
            self._setup_redis()
        else:
            self.logger.warning(f"Unsupported queue type {queue_type}, falling back to memory")
            self.queue_type = "memory"
            self._setup_memory()

    def _setup_rabbitmq(self) -> None:
        """Setup RabbitMQ connection."""
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'localhost'),
                    port=int(os.getenv('RABBITMQ_PORT', '5672')),
                    credentials=pika.PlainCredentials(
                        username=os.getenv('RABBITMQ_USER', 'guest'),
                        password=os.getenv('RABBITMQ_PASS', 'guest')
                    )
                )
            )
            self.channel = connection.channel()
            self.channel.queue_declare(queue='agent_messages', durable=True)
            self.logger.info("RabbitMQ connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._setup_memory()

    def _setup_redis(self) -> None:
        """Setup Redis connection."""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                db=int(os.getenv('REDIS_DB', '0'))
            )
            self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self._setup_memory()

    def _setup_memory(self) -> None:
        """Setup in-memory queue as fallback."""
        self.memory_queue: List[A2AMessage] = []
        self.logger.info("Using in-memory message queue")

    def publish_message(self, message: A2AMessage) -> bool:
        """Publish message to queue."""
        try:
            if self.queue_type == "rabbitmq":
                self.channel.basic_publish(
                    exchange='',
                    routing_key='agent_messages',
                    body=json.dumps(message.to_dict()),
                    properties=pika.BasicProperties(delivery_mode=2)  # Persistent
                )
            elif self.queue_type == "redis":
                self.redis_client.lpush('agent_messages', json.dumps(message.to_dict()))
            else:
                self.memory_queue.append(message)
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False

    def consume_messages(self, callback: Callable[[A2AMessage], None]) -> None:
        """Consume messages from queue."""
        try:
            if self.queue_type == "rabbitmq":
                def rabbit_callback(ch, method, properties, body):
                    message_dict = json.loads(body)
                    message = A2AMessage.from_dict(message_dict)
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                self.channel.basic_consume(
                    queue='agent_messages',
                    on_message_callback=rabbit_callback
                )
                self.channel.start_consuming()

            elif self.queue_type == "redis":
                while True:
                    message_data = self.redis_client.brpop('agent_messages', timeout=1)
                    if message_data:
                        message_dict = json.loads(message_data[1])
                        message = A2AMessage.from_dict(message_dict)
                        callback(message)
                    time.sleep(0.1)

            else:
                # Memory queue - just process existing messages
                while self.memory_queue:
                    message = self.memory_queue.pop(0)
                    callback(message)

        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}")


class A2AProtocolHandler:
    """Handler for Google A2A (Agent-to-Agent) protocol compliance."""

    def __init__(self, message_bus: MessageBus, telemetry: TelemetryCollector):
        """Initialize A2A protocol handler.

        Args:
            message_bus: Message bus for communication
            telemetry: Telemetry collector
        """
        self.message_bus = message_bus
        self.telemetry = telemetry
        self.logger = logging.getLogger(__name__)

        # A2A protocol state
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[A2AMessage]] = defaultdict(list)

        # Protocol compliance
        self.supported_protocols = ["A2A/1.0", "A2A/1.1"]
        self.capabilities = {
            "messaging": True,
            "voting": True,
            "task_coordination": True,
            "knowledge_sharing": True,
            "telemetry": True
        }

    def register_agent(self, agent: BaseAgent) -> None:
        """Register agent with A2A protocol."""
        agent_info = {
            'id': agent.agent_name,
            'name': agent.name,
            'role': agent.role,
            'capabilities': self.capabilities.copy(),
            'supported_protocols': self.supported_protocols.copy(),
            'registered_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'active'
        }

        self.agent_registry[agent.agent_name] = agent_info

        # Send handshake message
        handshake = A2AMessage(
            sender="a2a_protocol_handler",
            recipient=agent.agent_name,
            message_type=MessageType.AGENT_HANDSHAKE,
            content={
                'agent_info': agent_info,
                'protocol_requirements': {
                    'heartbeat_interval': 30,  # seconds
                    'status_update_interval': 60,
                    'message_ack_timeout': 10
                }
            }
        )

        self.send_a2a_message(handshake)
        self.telemetry.record_event('agent_registered', agent_info, agent.agent_name)

    def send_a2a_message(self, message: A2AMessage) -> bool:
        """Send A2A protocol compliant message."""
        # Validate protocol compliance
        if message.protocol_version not in self.supported_protocols:
            self.logger.warning(f"Unsupported protocol version: {message.protocol_version}")
            return False

        # Convert to internal message format
        internal_message = Message(
            message_id=message.id,
            sender=message.sender,
            recipient=message.recipient,
            message_type=message.message_type.value,
            content=message.content,
            priority=3,  # Default priority
            correlation_id=message.correlation_id
        )

        # Add metadata
        internal_message.content['_a2a_metadata'] = {
            'protocol_version': message.protocol_version,
            'conversation_id': message.conversation_id,
            'in_reply_to': message.in_reply_to
        }

        success = self.message_bus.send_message(internal_message)

        if success:
            # Track conversation
            if message.conversation_id:
                self.conversations[message.conversation_id].append(message)

            self.telemetry.record_event('a2a_message_sent', {
                'message_type': message.message_type.value,
                'recipient': message.recipient,
                'conversation_id': message.conversation_id
            }, message.sender)

        return success

    def receive_a2a_message(self, message: Message) -> None:
        """Process received A2A message."""
        # Check if this is an A2A message
        if '_a2a_metadata' not in message.content:
            return  # Not an A2A message

        metadata = message.content.pop('_a2a_metadata')

        # Reconstruct A2A message
        a2a_message = A2AMessage(
            id=message.message_id,
            timestamp=datetime.fromtimestamp(message.timestamp).isoformat() + 'Z',
            sender=message.sender,
            recipient=message.recipient,
            message_type=MessageType(message.message_type),
            content=message.content,
            correlation_id=message.correlation_id,
            protocol_version=metadata.get('protocol_version', 'A2A/1.0'),
            conversation_id=metadata.get('conversation_id'),
            in_reply_to=metadata.get('in_reply_to')
        )

        # Handle based on message type
        self._handle_a2a_message(a2a_message)

    def _handle_a2a_message(self, message: A2AMessage) -> None:
        """Handle incoming A2A message."""
        handler_name = f"_handle_{message.message_type.value}"
        handler = getattr(self, handler_name, self._handle_unknown_message)

        try:
            handler(message)
        except Exception as e:
            self.logger.error(f"Error handling A2A message {message.message_type}: {e}")

        self.telemetry.record_event('a2a_message_received', {
            'message_type': message.message_type.value,
            'sender': message.sender,
            'conversation_id': message.conversation_id
        }, message.recipient)

    def _handle_agent_handshake(self, message: A2AMessage) -> None:
        """Handle agent handshake."""
        agent_info = message.content.get('agent_info', {})
        agent_id = agent_info.get('id')

        if agent_id:
            self.agent_registry[agent_id] = agent_info
            self.logger.info(f"A2A handshake completed for agent {agent_id}")

    def _handle_agent_status(self, message: A2AMessage) -> None:
        """Handle agent status update."""
        # Update agent registry with latest status
        agent_id = message.sender
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id].update(message.content)

    def _handle_vote_proposal(self, message: A2AMessage) -> None:
        """Handle voting proposal."""
        # Forward to voting system
        proposal_data = message.content.get('proposal', {})
        # Implementation would integrate with VotingSystem

    def _handle_unknown_message(self, message: A2AMessage) -> None:
        """Handle unknown message type."""
        self.logger.warning(f"Unknown A2A message type: {message.message_type}")

    def get_protocol_status(self) -> Dict[str, Any]:
        """Get A2A protocol status."""
        return {
            'registered_agents': len(self.agent_registry),
            'active_conversations': len(self.conversations),
            'supported_protocols': self.supported_protocols,
            'capabilities': self.capabilities
        }


class SwarmObservabilityManager:
    """Comprehensive observability manager for the agent swarm."""

    def __init__(self):
        """Initialize observability manager."""
        self.logger = logging.getLogger(__name__)

        # Core components
        self.telemetry = TelemetryCollector()
        self.message_bus = MessageBus()
        self.voting_system = VotingSystem(self.message_bus)
        self.coordinator = SwarmCoordinator(self.message_bus, self.voting_system)

        # Advanced features
        self.a2a_handler = A2AProtocolHandler(self.message_bus, self.telemetry)
        self.persistent_queue = PersistentMessageQueue()

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with full observability."""
        # Register with message bus
        self.message_bus.register_agent(agent)

        # Register with A2A protocol
        self.a2a_handler.register_agent(agent)

        # Setup agent monitoring
        self._setup_agent_monitoring(agent)

        self.logger.info(f"Agent {agent.agent_name} registered with full observability")

    def _setup_agent_monitoring(self, agent: BaseAgent) -> None:
        """Setup comprehensive monitoring for an agent."""
        agent_name = agent.agent_name

        # Subscribe to relevant channels
        self.message_bus.subscribe_to_channel(agent_name, "system")
        self.message_bus.subscribe_to_channel(agent_name, "voting")
        self.message_bus.subscribe_to_channel(agent_name, agent.role.lower())

        # Setup telemetry tracking
        original_execute_tool = agent.execute_tool

        def monitored_execute_tool(tool_name: str, parameters: Dict[str, Any]):
            start_time = time.time()

            # Pre-execution telemetry
            self.telemetry.record_event('tool_execution_start', {
                'tool_name': tool_name,
                'parameters': parameters
            }, agent_name)

            try:
                result = original_execute_tool(tool_name, parameters)
                execution_time = time.time() - start_time

                # Post-execution telemetry
                self.telemetry.record_event('tool_execution_complete', {
                    'tool_name': tool_name,
                    'success': result.success,
                    'execution_time': execution_time,
                    'error': result.error if not result.success else None
                }, agent_name)

                # Update confidence metrics
                agent.update_confidence_after_execution(tool_name, result.success)

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                self.telemetry.record_event('tool_execution_error', {
                    'tool_name': tool_name,
                    'error': str(e),
                    'execution_time': execution_time
                }, agent_name)
                raise

        # Monkey patch the method
        agent.execute_tool = monitored_execute_tool

    def start_monitoring(self) -> None:
        """Start comprehensive monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # Start message processing
        self.message_bus.start_message_processing()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        # Setup persistent queue consumer
        def queue_callback(message: A2AMessage):
            self.a2a_handler.receive_a2a_message(
                Message(
                    message_id=message.id,
                    sender=message.sender,
                    recipient=message.recipient,
                    message_type=message.message_type.value,
                    content=message.content,
                    timestamp=datetime.fromisoformat(message.timestamp[:-1]).timestamp()
                )
            )

        queue_thread = threading.Thread(target=self.persistent_queue.consume_messages,
                                       args=(queue_callback,), daemon=True)
        queue_thread.start()

        self.logger.info("Swarm observability monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.monitoring_active = False
        self.message_bus.stop_message_processing()

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        self.logger.info("Swarm observability monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Send heartbeats
                self._send_heartbeats()

                # Check swarm health
                self._check_swarm_health()

                # Process pending messages
                self._process_pending_messages()

                time.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30.0)

    def _send_heartbeats(self) -> None:
        """Send heartbeat messages to all agents."""
        for agent_name in self.message_bus.agents.keys():
            heartbeat = A2AMessage(
                sender="observability_manager",
                recipient=agent_name,
                message_type=MessageType.AGENT_HEARTBEAT,
                content={
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'system_status': 'healthy'
                }
            )
            self.a2a_handler.send_a2a_message(heartbeat)

    def _check_swarm_health(self) -> None:
        """Check overall swarm health."""
        swarm_status = self.coordinator.get_swarm_status()

        # Record health metrics
        self.telemetry.record_event('swarm_health_check', swarm_status)

        # Alert on issues
        if swarm_status['should_terminate']:
            self.logger.warning(f"Swarm termination recommended: {swarm_status['termination_reason']}")

    def _process_pending_messages(self) -> None:
        """Process any pending messages for observability."""
        # This would handle any observability-specific message processing
        pass

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status."""
        return {
            'telemetry': self.telemetry.get_metrics_summary(),
            'message_bus': {
                'registered_agents': len(self.message_bus.agents),
                'active_channels': len(self.message_bus.broadcast_channels),
                'message_history_size': len(self.message_bus.message_history)
            },
            'voting_system': {
                'active_proposals': len(self.voting_system.proposals),
                'completed_proposals': len(self.voting_system.completed_proposals)
            },
            'coordinator': self.coordinator.get_swarm_status(),
            'a2a_protocol': self.a2a_handler.get_protocol_status(),
            'persistent_queue': {
                'type': self.persistent_queue.queue_type,
                'status': 'active'
            }
        }

    def create_vote_proposal(self, proposer: str, title: str, description: str,
                           options: List[str], context: str = "",
                           required_quorum: float = 0.5,
                           consensus_threshold: float = 0.66,
                           min_votes: int = 1) -> str:
        """Create a voting proposal with full observability.

        Accepts optional guardrail parameters that will be applied to the proposal:
        - required_quorum: fraction of registered agents needed
        - consensus_threshold: fraction of weight required for winner to be consensus
        - min_votes: minimum absolute vote count required for consensus
        """
        proposal_id = self.voting_system.create_proposal(
            proposer, title, description, options, context,
            required_quorum=required_quorum,
            consensus_threshold=consensus_threshold,
            min_votes=min_votes
        )

        self.telemetry.record_event('vote_proposal_created', {
            'proposal_id': proposal_id,
            'title': title,
            'proposer': proposer,
            'options': options,
            'required_quorum': required_quorum,
            'consensus_threshold': consensus_threshold,
            'min_votes': min_votes
        }, proposer)

        return proposal_id

    def assign_task(self, task: Dict[str, Any]) -> Optional[str]:
        """Assign task with observability."""
        agent_name = self.coordinator.assign_task(task)

        if agent_name:
            self.telemetry.record_event('task_assigned', {
                'task': task,
                'assigned_agent': agent_name
            })

        return agent_name

    def report_task_completion(self, task_id: str, agent_name: str,
                             success: bool, result: Any = None) -> None:
        """Report task completion with telemetry."""
        self.coordinator.report_task_completion(task_id, agent_name, success, result)

        self.telemetry.record_event('task_completed', {
            'task_id': task_id,
            'agent': agent_name,
            'success': success,
            'result': result
        }, agent_name)
