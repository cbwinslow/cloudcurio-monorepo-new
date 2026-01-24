# Docker Deployment Guide

Container deployment guide for CloudCurio framework.

## Table of Contents

- [Overview](#overview)
- [Docker Setup](#docker-setup)
- [Observability Stack](#observability-stack)
- [Production Deployment](#production-deployment)
- [Best Practices](#best-practices)

## Overview

CloudCurio provides Docker configurations for:
- Observability stack (Prometheus, Grafana, Jaeger)
- Agent runtime containers
- Development environments
- Production deployments

## Docker Setup

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Project Structure

```
docker/
├── compose/
│   ├── observability/
│   │   ├── docker-compose.yml
│   │   ├── prometheus/
│   │   │   └── prometheus.yml
│   │   └── grafana/
│   │       └── dashboards/
│   └── agents/
│       └── docker-compose.yml
└── Dockerfile
```

## Observability Stack

### Starting the Stack

```bash
cd docker/compose/observability
docker-compose up -d
```

Services available:
- **Prometheus**: http://localhost:9090 - Metrics collection
- **Grafana**: http://localhost:3000 - Visualization (admin/admin)
- **Jaeger**: http://localhost:16686 - Distributed tracing

### Docker Compose Configuration

`docker/compose/observability/docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: cloudcurio-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - cloudcurio

  grafana:
    image: grafana/grafana:latest
    container_name: cloudcurio-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - cloudcurio
    depends_on:
      - prometheus

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: cloudcurio-jaeger
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    restart: unless-stopped
    networks:
      - cloudcurio

volumes:
  prometheus_data:
  grafana_data:

networks:
  cloudcurio:
    driver: bridge
```

### Prometheus Configuration

`docker/compose/observability/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cloudcurio-agents'
    static_configs:
      - targets: ['host.docker.internal:8000']
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

## Production Deployment

### Agent Container

`Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY agents/ agents/
COPY configs/ configs/
COPY prompts/ prompts/
COPY bin/ bin/

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import cbw_foundry; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "cbw_foundry.cli"]
```

### Building the Image

```bash
# Build image
docker build -t cloudcurio-agent:latest .

# Tag for registry
docker tag cloudcurio-agent:latest registry.example.com/cloudcurio-agent:latest

# Push to registry
docker push registry.example.com/cloudcurio-agent:latest
```

### Running Agent Container

```bash
# Run single agent
docker run -d \
  --name cloudcurio-agent-1 \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -v $(pwd)/agents:/app/agents \
  -v $(pwd)/configs:/app/configs \
  cloudcurio-agent:latest

# Run with observability
docker run -d \
  --name cloudcurio-agent-1 \
  --network cloudcurio \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317 \
  cloudcurio-agent:latest
```

### Agent Deployment Compose

`docker/compose/agents/docker-compose.yml`:

```yaml
version: '3.8'

services:
  agent-coordinator:
    image: cloudcurio-agent:latest
    container_name: cloudcurio-coordinator
    environment:
      - AGENT_ROLE=coordinator
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
    volumes:
      - ../../agents:/app/agents
      - ../../configs:/app/configs
    networks:
      - cloudcurio
    restart: unless-stopped
    
  agent-worker-1:
    image: cloudcurio-agent:latest
    container_name: cloudcurio-worker-1
    environment:
      - AGENT_ROLE=worker
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
    volumes:
      - ../../agents:/app/agents
      - ../../configs:/app/configs
    networks:
      - cloudcurio
    restart: unless-stopped
    deploy:
      replicas: 3

networks:
  cloudcurio:
    external: true
```

## Best Practices

### 1. Environment Variables

Use `.env` file for configuration:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://ollama:11434
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
LOG_LEVEL=INFO
```

Load with compose:

```yaml
services:
  agent:
    env_file:
      - .env
```

### 2. Volume Management

Mount essential directories:

```yaml
volumes:
  - ./agents:/app/agents:ro          # Read-only agent specs
  - ./configs:/app/configs:ro        # Read-only configs
  - agent_data:/app/data             # Persistent data
  - agent_logs:/app/logs             # Logs
```

### 3. Networking

Use dedicated network:

```bash
# Create network
docker network create cloudcurio

# Connect containers
docker network connect cloudcurio cloudcurio-agent-1
```

### 4. Resource Limits

Set container resource limits:

```yaml
services:
  agent:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 5. Health Checks

Implement health checks:

```yaml
services:
  agent:
    healthcheck:
      test: ["CMD", "python", "-c", "import cbw_foundry; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

### 6. Logging

Configure logging:

```yaml
services:
  agent:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 7. Security

Follow security best practices:

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Remove sensitive data
RUN rm -rf /root/.cache /var/cache/apt/*

# Use read-only root filesystem
services:
  agent:
    read_only: true
    tmpfs:
      - /tmp
```

## Scaling

### Horizontal Scaling

```bash
# Scale workers
docker-compose up -d --scale agent-worker=5

# Or in compose file
services:
  agent-worker:
    deploy:
      replicas: 5
```

### Load Balancing

Use nginx for load balancing:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agent-worker
```

`nginx.conf`:

```nginx
upstream agent_backend {
    least_conn;
    server agent-worker-1:8000;
    server agent-worker-2:8000;
    server agent-worker-3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://agent_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Container Metrics

Monitor with cAdvisor:

```yaml
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
```

Add to Prometheus:

```yaml
scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

## Troubleshooting

### Common Issues

**Container won't start:**

```bash
# Check logs
docker logs cloudcurio-agent-1

# Inspect container
docker inspect cloudcurio-agent-1

# Check resource usage
docker stats cloudcurio-agent-1
```

**Network issues:**

```bash
# Test connectivity
docker exec cloudcurio-agent-1 ping jaeger

# Check network
docker network inspect cloudcurio
```

**Permission issues:**

```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./data

# Or run as root (not recommended)
docker run --user root ...
```

## Additional Resources

- [Configuration Guide](CONFIGURATION.md)
- [Observability Guide](OBSERVABILITY.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
