"""Telemetry and OpenTelemetry Integration for Agents.

Provides comprehensive monitoring, tracing, and metrics for agent operations.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.metrics import get_meter

    # Setup OpenTelemetry tracing
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Setup span processor with console exporter
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Setup metrics
    meter_provider = MeterProvider()
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    meter_provider.add_metric_reader(metric_reader)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Global meter
    meter = get_meter(__name__)

    # Create metrics
    agent_execution_counter = meter.create_counter(
        name="agent_execution_count",
        description="Number of agent executions",
        unit="executions"
    )

    tool_execution_counter = meter.create_counter(
        name="tool_execution_count",
        description="Number of tool executions",
        unit="executions"
    )

    execution_duration_histogram = meter.create_histogram(
        name="execution_duration_ms",
        description="Duration of agent/tool executions in milliseconds",
        unit="ms"
    )

    error_counter = meter.create_counter(
        name="execution_errors",
        description="Number of execution errors",
        unit="errors"
    )

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Create dummy functions for when OpenTelemetry is not available
    class DummyTracer:
        def start_as_current_span(self, name, **kwargs):
            return DummySpan()

    class DummySpan:
        def set_attribute(self, key, value):
            pass

        def set_status(self, status):
            pass

        def record_exception(self, exception):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class DummyMeter:
        def create_counter(self, **kwargs):
            return DummyCounter()

        def create_histogram(self, **kwargs):
            return DummyHistogram()

    class DummyCounter:
        def add(self, value, attributes=None):
            pass

    class DummyHistogram:
        def record(self, value, attributes=None):
            pass

    tracer = DummyTracer()
    meter = DummyMeter()
    agent_execution_counter = DummyCounter()
    tool_execution_counter = DummyCounter()
    execution_duration_histogram = DummyHistogram()
    error_counter = DummyCounter()


class TelemetryManager:
    """Manages telemetry for agents and tools."""

    def __init__(self, agent_name: str):
        """Initialize telemetry manager."""
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"telemetry.{agent_name}")
        self.logger.setLevel(logging.INFO)

    def trace_agent_execution(self, agent_method: Callable) -> Callable:
        """Decorator to trace agent method executions."""
        @wraps(agent_method)
        def wrapper(*args, **kwargs):
            method_name = agent_method.__name__
            span_name = f"{self.agent_name}.{method_name}"

            start_time = time.time()

            # Start OpenTelemetry span
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("agent", self.agent_name)
                span.set_attribute("method", method_name)

                # Add method parameters as attributes (excluding sensitive data)
                safe_params = {k: str(v) for k, v in kwargs.items() if not k.endswith('_secret') and not k.endswith('_token')}
                for key, value in safe_params.items():
                    span.set_attribute(f"param.{key}", value)

                try:
                    # Execute the method
                    result = agent_method(*args, **kwargs)

                    # Record success metrics
                    duration_ms = (time.time() - start_time) * 1000

                    agent_execution_counter.add(1, {
                        "agent": self.agent_name,
                        "method": method_name,
                        "status": "success"
                    })

                    execution_duration_histogram.record(duration_ms, {
                        "agent": self.agent_name,
                        "method": method_name
                    })

                    span.set_attribute("duration_ms", duration_ms)
                    span.set_attribute("success", True)
                    span.set_status(Status(StatusCode.OK))

                    self.logger.info(f"Agent {self.agent_name}.{method_name} executed successfully in {duration_ms:.2f}ms")

                    return result

                except Exception as e:
                    # Record error metrics
                    duration_ms = (time.time() - start_time) * 1000

                    agent_execution_counter.add(1, {
                        "agent": self.agent_name,
                        "method": method_name,
                        "status": "error"
                    })

                    error_counter.add(1, {
                        "agent": self.agent_name,
                        "method": method_name,
                        "error_type": type(e).__name__
                    })

                    execution_duration_histogram.record(duration_ms, {
                        "agent": self.agent_name,
                        "method": method_name,
                        "error": True
                    })

                    span.set_attribute("duration_ms", duration_ms)
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    span.set_attribute("error_type", type(e).__name__)
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)

                    self.logger.error(f"Agent {self.agent_name}.{method_name} failed after {duration_ms:.2f}ms: {str(e)}")

                    raise

        return wrapper

    def trace_tool_execution(self, tool_name: str) -> Callable:
        """Decorator factory for tracing tool executions."""
        def decorator(tool_method: Callable) -> Callable:
            @wraps(tool_method)
            def wrapper(*args, **kwargs):
                span_name = f"{self.agent_name}.{tool_name}"

                start_time = time.time()

                # Start OpenTelemetry span
                with tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("agent", self.agent_name)
                    span.set_attribute("tool", tool_name)

                    # Add tool parameters as attributes (excluding sensitive data)
                    safe_params = {k: str(v) for k, v in kwargs.items() if not k.endswith('_secret') and not k.endswith('_token')}
                    for key, value in safe_params.items():
                        span.set_attribute(f"param.{key}", value)

                    try:
                        # Execute the tool
                        result = tool_method(*args, **kwargs)

                        # Record success metrics
                        duration_ms = (time.time() - start_time) * 1000

                        tool_execution_counter.add(1, {
                            "agent": self.agent_name,
                            "tool": tool_name,
                            "status": "success"
                        })

                        execution_duration_histogram.record(duration_ms, {
                            "agent": self.agent_name,
                            "tool": tool_name
                        })

                        span.set_attribute("duration_ms", duration_ms)
                        span.set_attribute("success", True)
                        span.set_status(Status(StatusCode.OK))

                        self.logger.info(f"Tool {self.agent_name}.{tool_name} executed successfully in {duration_ms:.2f}ms")

                        return result

                    except Exception as e:
                        # Record error metrics
                        duration_ms = (time.time() - start_time) * 1000

                        tool_execution_counter.add(1, {
                            "agent": self.agent_name,
                            "tool": tool_name,
                            "status": "error"
                        })

                        error_counter.add(1, {
                            "agent": self.agent_name,
                            "tool": tool_name,
                            "error_type": type(e).__name__
                        })

                        execution_duration_histogram.record(duration_ms, {
                            "agent": self.agent_name,
                            "tool": tool_name,
                            "error": True
                        })

                        span.set_attribute("duration_ms", duration_ms)
                        span.set_attribute("success", False)
                        span.set_attribute("error", str(e))
                        span.set_attribute("error_type", type(e).__name__)
                        span.set_status(Status(StatusCode.ERROR))
                        span.record_exception(e)

                        self.logger.error(f"Tool {self.agent_name}.{tool_name} failed after {duration_ms:.2f}ms: {str(e)}")

                        raise

            return wrapper

        return decorator

    def log_metric(self, metric_name: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Log a custom metric."""
        if attributes is None:
            attributes = {}

        attributes["agent"] = self.agent_name

        # For now, just log the metric
        # In a real implementation, this would be sent to a metrics backend
        self.logger.info(f"Metric {metric_name}: {value} (attributes: {attributes})")

    def get_telemetry_status(self) -> Dict[str, Any]:
        """Get current telemetry status."""
        return {
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "agent_name": self.agent_name,
            "tracing_enabled": True,
            "metrics_enabled": True,
            "logging_enabled": True
        }


def create_telemetry_manager(agent_name: str) -> TelemetryManager:
    """Factory function to create a telemetry manager."""
    return TelemetryManager(agent_name)


# Global telemetry functions for convenience

def trace_agent_method(agent_name: str, method_name: str):
    """Decorator for tracing agent methods."""
    telemetry = create_telemetry_manager(agent_name)

    def decorator(method):
        return telemetry.trace_agent_execution(method)

    return decorator


def trace_tool_method(agent_name: str, tool_name: str):
    """Decorator for tracing tool methods."""
    telemetry = create_telemetry_manager(agent_name)

    def decorator(method):
        return telemetry.trace_tool_execution(tool_name)(method)

    return decorator
