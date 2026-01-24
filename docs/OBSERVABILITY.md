# Observability Guide

Monitoring, telemetry, and observability for CloudCurio agents.

## Table of Contents

- [Overview](#overview)
- [OpenTelemetry Integration](#opentelemetry-integration)
- [Metrics](#metrics)
- [Distributed Tracing](#distributed-tracing)
- [Logging](#logging)
- [Dashboards](#dashboards)

## Overview

CloudCurio provides comprehensive observability through:

- **Metrics**: Performance and operational metrics via Prometheus
- **Tracing**: Distributed tracing via Jaeger/OpenTelemetry
- **Logging**: Structured logging with context
- **Dashboards**: Pre-built Grafana dashboards

### Architecture

```
Agent → OpenTelemetry SDK → OTLP Exporter → Collector
  ↓           ↓                   ↓              ↓
Spans     Metrics              HTTP/gRPC    Prometheus
Logs      Events               Protocol      Jaeger
                                             Grafana
```

## OpenTelemetry Integration

### Setup

```python
from cbw_foundry.observability.otel import setup_observability

# Initialize observability
setup_observability(
    service_name="cloudcurio-agents",
    endpoint="http://localhost:4317"
)
```

### Configuration

```python
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource


def setup_observability(
    service_name: str = "cloudcurio",
    endpoint: str = None
):
    """Setup OpenTelemetry observability."""
    
    # Get configuration
    endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.4.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Setup tracing
    trace_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=endpoint)
    trace_provider.add_span_processor(
        BatchSpanProcessor(trace_exporter)
    )
    trace.set_tracer_provider(trace_provider)
    
    # Setup metrics
    metric_provider = MeterProvider(resource=resource)
    metric_exporter = OTLPMetricExporter(endpoint=endpoint)
    metric_provider.add_metric_reader(
        PeriodicExportingMetricReader(metric_exporter)
    )
    metrics.set_meter_provider(metric_provider)
```

### Instrumenting Code

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def execute_agent(agent_spec, user_input):
    """Execute agent with tracing."""
    
    with tracer.start_as_current_span("agent.execute") as span:
        # Add attributes
        span.set_attribute("agent.name", agent_spec.metadata.name)
        span.set_attribute("agent.version", agent_spec.metadata.version)
        span.set_attribute("input.length", len(user_input))
        
        try:
            # Execute
            result = runtime.run(agent_spec, user_input)
            
            # Record success
            span.set_attribute("execution.status", "success")
            span.set_attribute("output.length", len(str(result)))
            
            return result
            
        except Exception as e:
            # Record failure
            span.set_attribute("execution.status", "failure")
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

## Metrics

### Collecting Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

# Counter
agent_executions = meter.create_counter(
    "agent.executions.total",
    description="Total number of agent executions"
)

# Histogram
execution_duration = meter.create_histogram(
    "agent.execution.duration",
    description="Agent execution duration in seconds"
)

# UpDown Counter
active_agents = meter.create_up_down_counter(
    "agent.active.count",
    description="Number of currently active agents"
)


def execute_with_metrics(agent, input_data):
    """Execute agent with metric collection."""
    
    # Increment counter
    agent_executions.add(1, {"agent": agent.name})
    
    # Track active agents
    active_agents.add(1, {"agent": agent.name})
    
    try:
        # Time execution
        start_time = time.time()
        result = agent.run(input_data)
        duration = time.time() - start_time
        
        # Record duration
        execution_duration.record(
            duration,
            {"agent": agent.name, "status": "success"}
        )
        
        return result
        
    except Exception as e:
        execution_duration.record(
            time.time() - start_time,
            {"agent": agent.name, "status": "failure"}
        )
        raise
        
    finally:
        active_agents.add(-1, {"agent": agent.name})
```

### Key Metrics

**Agent Metrics:**
- `agent.executions.total` - Total executions
- `agent.execution.duration` - Execution time
- `agent.active.count` - Active agents
- `agent.errors.total` - Error count
- `agent.retries.total` - Retry count

**Tool Metrics:**
- `tool.invocations.total` - Tool calls
- `tool.execution.duration` - Tool execution time
- `tool.errors.total` - Tool errors

**Model Metrics:**
- `model.requests.total` - Model API calls
- `model.tokens.total` - Tokens used
- `model.latency` - Model response time
- `model.errors.total` - Model errors

**System Metrics:**
- `system.cpu.usage` - CPU usage
- `system.memory.usage` - Memory usage
- `system.disk.usage` - Disk usage

## Distributed Tracing

### Creating Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class TracedAgent:
    """Agent with distributed tracing."""
    
    def execute(self, user_input: str):
        """Execute with tracing."""
        
        with tracer.start_as_current_span("agent.execute") as span:
            span.set_attribute("input", user_input)
            
            # Span for LLM call
            with tracer.start_as_current_span("llm.call") as llm_span:
                llm_span.set_attribute("model", self.model)
                response = self._call_llm(user_input)
                llm_span.set_attribute("tokens", response.tokens)
            
            # Span for tool execution
            if self.has_tools():
                with tracer.start_as_current_span("tools.execute") as tool_span:
                    result = self._execute_tools(response)
                    tool_span.set_attribute("tools_used", len(result))
            
            return result
```

### Span Attributes

Common attributes to track:

```python
span.set_attribute("agent.name", "content_generator")
span.set_attribute("agent.version", "1.0.0")
span.set_attribute("runtime", "local")
span.set_attribute("model.provider", "openai")
span.set_attribute("model.name", "gpt-4")
span.set_attribute("input.length", 150)
span.set_attribute("output.length", 500)
span.set_attribute("tools.count", 3)
span.set_attribute("execution.status", "success")
```

### Trace Context Propagation

```python
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def call_remote_agent(agent_id: str, input_data: str):
    """Call remote agent with trace context."""
    
    # Get current context
    ctx = trace.get_current_span().get_span_context()
    
    # Inject context into headers
    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    
    # Make request with context
    response = requests.post(
        f"http://agent-service/{agent_id}/execute",
        json={"input": input_data},
        headers=carrier
    )
    
    return response.json()
```

## Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime


class StructuredLogger:
    """Structured JSON logger."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)
    
    def _json_formatter(self):
        """Create JSON formatter."""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add extra fields
                if hasattr(record, 'agent_name'):
                    log_data['agent_name'] = record.agent_name
                if hasattr(record, 'trace_id'):
                    log_data['trace_id'] = record.trace_id
                
                return json.dumps(log_data)
        
        return JsonFormatter()
    
    def info(self, message: str, **kwargs):
        """Log info with context."""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error with context."""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.error(message, extra=extra, exc_info=True)


# Usage
logger = StructuredLogger(__name__)

logger.info(
    "Agent execution started",
    agent_name="content_generator",
    input_length=150
)

logger.error(
    "Agent execution failed",
    agent_name="content_generator",
    error_type="TimeoutError"
)
```

### Log Correlation

Correlate logs with traces:

```python
from opentelemetry import trace
import logging


def log_with_trace_context(logger, level, message, **kwargs):
    """Log with trace context."""
    
    # Get current span
    span = trace.get_current_span()
    span_context = span.get_span_context()
    
    # Add trace IDs to log
    extra = {
        'trace_id': format(span_context.trace_id, '032x'),
        'span_id': format(span_context.span_id, '016x'),
        **kwargs
    }
    
    logger.log(level, message, extra=extra)
```

## Dashboards

### Grafana Dashboard

Create dashboard for agent metrics:

`docker/compose/observability/grafana/dashboards/agents.json`:

```json
{
  "dashboard": {
    "title": "CloudCurio Agents",
    "panels": [
      {
        "title": "Agent Executions",
        "targets": [
          {
            "expr": "rate(agent_executions_total[5m])"
          }
        ]
      },
      {
        "title": "Execution Duration (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, agent_execution_duration_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(agent_errors_total[5m])"
          }
        ]
      },
      {
        "title": "Active Agents",
        "targets": [
          {
            "expr": "agent_active_count"
          }
        ]
      }
    ]
  }
}
```

### Prometheus Queries

Useful queries for monitoring:

```promql
# Agent execution rate
rate(agent_executions_total[5m])

# P95 execution duration
histogram_quantile(0.95, rate(agent_execution_duration_bucket[5m]))

# Error rate
rate(agent_errors_total[5m]) / rate(agent_executions_total[5m])

# Active agents
agent_active_count

# Token usage
rate(model_tokens_total[1h])
```

## Best Practices

### 1. Tracing

- Create spans for significant operations
- Add meaningful attributes
- Propagate context across services
- Limit span count to avoid overhead

### 2. Metrics

- Use appropriate metric types
- Add relevant labels
- Aggregate at query time
- Set reasonable cardinality

### 3. Logging

- Use structured logging
- Include correlation IDs
- Log at appropriate levels
- Avoid logging sensitive data

### 4. Performance

- Sample traces if needed
- Batch metric exports
- Use async exporters
- Monitor collector performance

### 5. Alerts

Set up alerts for key metrics:

```yaml
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(agent_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High agent error rate"
      
      - alert: SlowExecution
        expr: histogram_quantile(0.95, agent_execution_duration_bucket) > 60
        for: 10m
        annotations:
          summary: "Slow agent execution"
```

## Additional Resources

- [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Configuration Guide](CONFIGURATION.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
