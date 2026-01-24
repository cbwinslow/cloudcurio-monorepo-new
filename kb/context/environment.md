---
title: Environment
tags: [context, env, infrastructure]
owner: cbwinslow
last_reviewed: 2026-01-15
---

# Environment Documentation

Comprehensive documentation of machines, operating systems, networking, and infrastructure for CloudCurio Monorepo development and deployment.

## Table of Contents

- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Networking Configuration](#networking-configuration)
- [Infrastructure as Code](#infrastructure-as-code)
- [Environment Variables](#environment-variables)
- [Security Considerations](#security-considerations)

## Development Environment

### Local Development

**Recommended Specifications:**

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| CPU | 4 cores | 8 cores | 12+ cores |
| RAM | 8 GB | 16 GB | 32 GB |
| Disk | 20 GB free | 50 GB free (SSD) | 100 GB+ (NVMe SSD) |
| OS | Ubuntu 20.04, macOS 11 | Ubuntu 22.04, macOS 12+ | Ubuntu 24.04, macOS 14+ |

**Tested Platforms:**

- **Linux**: Ubuntu 22.04 LTS, Debian 12, Fedora 39, Arch Linux
- **macOS**: macOS 12 Monterey, macOS 13 Ventura, macOS 14 Sonoma (Intel & Apple Silicon)
- **Windows**: Windows 10/11 with WSL2 (Ubuntu 22.04)

### Required Software

**Core Requirements:**

```bash
# Python ecosystem
Python 3.10, 3.11, or 3.12
pip 23.0+
venv (Python virtual environments)

# Node.js ecosystem (for MCP servers)
Node.js 18.x or 20.x LTS
npm 9.0+

# Version control
Git 2.30+

# Build tools (Linux)
build-essential (gcc, make, etc.)

# Build tools (macOS)
Xcode Command Line Tools
```

**Optional Software:**

```bash
# Containerization
Docker 20.10+
Docker Compose v2.0+

# Database (for certain agents)
PostgreSQL 14+
MySQL 8+
Redis 7+

# Observability
Prometheus 2.40+
Grafana 9.0+
Jaeger 1.40+
```

### Development Machine Profiles

**Profile 1: Minimal (Budget/Basic Development)**
```
CPU: Intel i5 / AMD Ryzen 5 / Apple M1
RAM: 8 GB
Disk: 256 GB SSD
OS: Ubuntu 22.04 or macOS 12
Network: 10 Mbps+
Use Case: Basic agent development, testing
```

**Profile 2: Standard (Most Developers)**
```
CPU: Intel i7 / AMD Ryzen 7 / Apple M2
RAM: 16 GB
Disk: 512 GB SSD
OS: Ubuntu 22.04 or macOS 13
Network: 50 Mbps+
Use Case: Full development, local testing, Docker
```

**Profile 3: High-Performance (Framework Development)**
```
CPU: Intel i9 / AMD Ryzen 9 / Apple M2 Pro/Max
RAM: 32-64 GB
Disk: 1 TB NVMe SSD
OS: Latest Ubuntu LTS or macOS
Network: 100+ Mbps
Use Case: Large-scale testing, multiple Docker stacks, performance profiling
```

### Environment Setup Scripts

**Linux/macOS Setup:**
```bash
#!/bin/bash
# Automated development environment setup

# Update system
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# or
brew update && brew upgrade  # macOS

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3.10-pip  # Ubuntu
# or
brew install python@3.10  # macOS

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # Linux
sudo apt install -y nodejs
# or
brew install node@18  # macOS

# Install Git
sudo apt install git  # Linux
# or
brew install git  # macOS

# Install Docker (optional)
sudo apt install docker.io docker-compose  # Linux
# or
brew install --cask docker  # macOS

# Clone repository
git clone <repo-url> ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo

# Bootstrap
./scripts/bootstrap.sh
```

## Production Environment

### Cloud Deployment Options

**AWS EC2 Instance Recommendations:**

```yaml
Development/Staging:
  Instance: t3.medium or t3a.medium
  vCPUs: 2
  RAM: 4 GB
  Storage: 30 GB GP3 EBS
  Network: Enhanced networking enabled
  
Production:
  Instance: t3.xlarge or c6i.xlarge
  vCPUs: 4
  RAM: 16 GB
  Storage: 100 GB GP3 EBS (3000 IOPS)
  Network: Enhanced networking enabled
  
High-Scale Production:
  Instance: c6i.2xlarge or c6i.4xlarge
  vCPUs: 8-16
  RAM: 32-64 GB
  Storage: 200 GB GP3 EBS (5000 IOPS)
  Network: Enhanced networking + placement group
```

**GCP Compute Engine Recommendations:**

```yaml
Development/Staging:
  Machine Type: e2-standard-2
  vCPUs: 2
  RAM: 8 GB
  Storage: 30 GB SSD persistent disk
  
Production:
  Machine Type: n2-standard-4
  vCPUs: 4
  RAM: 16 GB
  Storage: 100 GB SSD persistent disk
  
High-Scale Production:
  Machine Type: n2-standard-8 or c2-standard-8
  vCPUs: 8
  RAM: 32 GB
  Storage: 200 GB SSD persistent disk
```

**Azure VM Recommendations:**

```yaml
Development/Staging:
  VM Size: Standard_D2s_v3
  vCPUs: 2
  RAM: 8 GB
  Storage: 30 GB Premium SSD
  
Production:
  VM Size: Standard_D4s_v3
  vCPUs: 4
  RAM: 16 GB
  Storage: 100 GB Premium SSD
  
High-Scale Production:
  VM Size: Standard_D8s_v3
  vCPUs: 8
  RAM: 32 GB
  Storage: 200 GB Premium SSD
```

### Container Orchestration

**Docker Compose (Small Scale):**
```yaml
# docker/compose/production/docker-compose.yml
services:
  cloudcurio-api:
    image: cloudcurio:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  cloudcurio-worker:
    image: cloudcurio:latest
    command: worker
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

**Kubernetes (Large Scale):**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudcurio-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cloudcurio-api
  template:
    metadata:
      labels:
        app: cloudcurio-api
    spec:
      containers:
      - name: api
        image: cloudcurio:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

## Networking Configuration

### Port Allocation

**Development:**
```
8000      - API server
3000-3099 - MCP servers (automation, media, etc.)
9090      - Prometheus
3000      - Grafana (conflicts with MCP, use 3100 for Grafana in dev)
16686     - Jaeger UI
6379      - Redis (if used)
5432      - PostgreSQL (if used)
3306      - MySQL (if used)
```

**Production:**
```
443       - HTTPS (external)
80        - HTTP redirect to HTTPS
8000      - API server (internal)
3000-3099 - MCP servers (internal)
9090      - Prometheus (internal/VPN only)
3100      - Grafana (internal/VPN only)
```

### Firewall Rules

**Development (Local):**
```bash
# No strict firewall needed for local dev
# Ensure loopback (127.0.0.1) is accessible
```

**Production (Cloud):**
```yaml
Inbound Rules:
  - Port 443: HTTPS from 0.0.0.0/0
  - Port 80: HTTP from 0.0.0.0/0 (redirect only)
  - Port 22: SSH from trusted IPs only
  - Port 9090, 3100: Prometheus/Grafana from VPN/internal only

Outbound Rules:
  - All ports: Allow (for LLM API calls, package downloads)
  
Security Groups/NSGs:
  - api-sg: Ports 443, 80
  - admin-sg: Port 22 from admin IPs
  - monitoring-sg: Ports 9090, 3100 from internal
  - worker-sg: No inbound, outbound to LLM APIs
```

### DNS Configuration

**Development:**
```
localhost:8000           - API
localhost:9090           - Prometheus
localhost:3100           - Grafana
localhost:3000-3099      - MCP servers
```

**Production:**
```
api.cloudcurio.com       - API (load balanced)
monitoring.cloudcurio.com - Grafana (internal)
mcp-automation.cloudcurio.com - MCP automation server
mcp-media.cloudcurio.com     - MCP media server
```

### Load Balancing

**AWS Application Load Balancer:**
```yaml
Listeners:
  - Port: 443 (HTTPS)
    Protocol: HTTPS
    SSL Certificate: ACM certificate
    Default Action: Forward to target group
    
  - Port: 80 (HTTP)
    Protocol: HTTP
    Default Action: Redirect to HTTPS

Target Group:
  - Health Check: /health
  - Interval: 30s
  - Timeout: 5s
  - Healthy Threshold: 2
  - Unhealthy Threshold: 3
```

## Infrastructure as Code

### Terraform Example

```hcl
# terraform/main.tf

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "cloudcurio" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 22.04
  instance_type = "t3.xlarge"
  
  root_block_device {
    volume_size = 100
    volume_type = "gp3"
    iops        = 3000
  }
  
  vpc_security_group_ids = [aws_security_group.cloudcurio_sg.id]
  
  user_data = file("scripts/cloud-init.sh")
  
  tags = {
    Name        = "cloudcurio-production"
    Environment = "production"
    Managed     = "terraform"
  }
}

resource "aws_security_group" "cloudcurio_sg" {
  name        = "cloudcurio-sg"
  description = "CloudCurio production security group"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["YOUR_ADMIN_IP/32"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Environment Variables

### Development Environment

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# LLM APIs (optional for local dev)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Runtime
DEFAULT_RUNTIME=local
DEFAULT_MODEL=gpt-4

# Observability
OTEL_ENABLED=false
LOG_FORMAT=text

# MCP Servers
MCP_AUTOMATION_ENABLED=true
MCP_MEDIA_ENABLED=true
MCP_AUTOMATION_URL=http://localhost:3000
MCP_MEDIA_URL=http://localhost:3001

# Timeouts
AGENT_TIMEOUT=300
TOOL_TIMEOUT=60
```

### Production Environment

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# LLM APIs (required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Runtime
DEFAULT_RUNTIME=local
DEFAULT_MODEL=gpt-4

# Observability
OTEL_ENABLED=true
OTEL_ENDPOINT=http://jaeger:4317
LOG_FORMAT=json

# MCP Servers
MCP_AUTOMATION_ENABLED=true
MCP_MEDIA_ENABLED=true
MCP_AUTOMATION_URL=http://mcp-automation:3000
MCP_MEDIA_URL=http://mcp-media:3001

# Timeouts
AGENT_TIMEOUT=600
TOOL_TIMEOUT=120

# Security
API_KEY_REQUIRED=true
ALLOWED_ORIGINS=https://app.cloudcurio.com

# Database (if used)
DATABASE_URL=postgresql://user:pass@db:5432/cloudcurio
REDIS_URL=redis://redis:6379/0
```

## Security Considerations

### Development Security

1. **API Keys**: Use test/development keys, never production
2. **Secrets**: Store in `.env` file (gitignored)
3. **Network**: Local only, firewall not critical
4. **Updates**: Keep dependencies updated weekly

### Production Security

1. **API Keys**: 
   - Use secret management service (AWS Secrets Manager, HashiCorp Vault)
   - Rotate keys regularly (90 days)
   - Use read-only keys where possible

2. **Network Security**:
   - TLS/HTTPS only (no HTTP in production)
   - Restrict admin access (SSH) to known IPs
   - Use VPN for monitoring dashboards
   - Enable DDoS protection

3. **OS Security**:
   - Keep OS patched (automated updates)
   - Disable root SSH login
   - Use SSH keys, not passwords
   - Enable fail2ban or equivalent

4. **Application Security**:
   - Run as non-root user
   - Use virtual environments
   - Validate all inputs
   - Rate limit API endpoints

5. **Monitoring**:
   - Log all access attempts
   - Alert on suspicious activity
   - Regular security audits
   - Monitor for vulnerabilities

### Compliance Considerations

For regulated environments:

- **Data Residency**: Deploy in appropriate regions
- **Encryption**: At rest (disk encryption) and in transit (TLS)
- **Audit Logging**: Enable comprehensive logging
- **Access Control**: Implement RBAC
- **Backup**: Regular automated backups with encryption
- **Disaster Recovery**: Test recovery procedures

---

**Last Updated:** 2026-01-15  
**Maintained By:** @cbwinslow  
**Related:** [Docker Deployment](../../docs/DOCKER_DEPLOYMENT.md), [Observability](../../docs/OBSERVABILITY.md)
