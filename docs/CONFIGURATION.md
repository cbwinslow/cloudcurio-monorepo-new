# Configuration Guide

Complete configuration reference for CloudCurio framework.

## Table of Contents

- [Overview](#overview)
- [Environment Variables](#environment-variables)
- [Configuration Files](#configuration-files)
- [Model Configuration](#model-configuration)
- [Runtime Configuration](#runtime-configuration)
- [Tool Configuration](#tool-configuration)

## Overview

CloudCurio uses a layered configuration system:

1. **Environment Variables**: System-level configuration
2. **Config Files**: Repository-level settings
3. **Agent Specs**: Agent-specific configuration
4. **Runtime Overrides**: Command-line overrides

### Configuration Priority

```
CLI Args > Agent Spec > Config Files > Environment Variables > Defaults
  (highest priority)                                     (lowest priority)
```

## Environment Variables

### Model Provider API Keys

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Optional

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."

# Google AI
export GOOGLE_API_KEY="..."

# Mistral
export MISTRAL_API_KEY="..."
```

### Ollama Configuration

```bash
# Ollama base URL
export OLLAMA_BASE_URL="http://localhost:11434"

# Default model
export OLLAMA_DEFAULT_MODEL="qwen2.5-coder"
```

### Framework Configuration

```bash
# CrewAI
export CREWAI_VERBOSE="true"
export CREWAI_ALLOW_DELEGATION="false"

# LangChain
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="..."
export LANGCHAIN_PROJECT="cloudcurio"

# PydanticAI
export PYDANTIC_AI_LOG_LEVEL="INFO"
```

### Observability

```bash
# OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="cloudcurio-agents"
export OTEL_LOG_LEVEL="info"

# Prometheus
export PROMETHEUS_PORT="9090"
export PROMETHEUS_SCRAPE_INTERVAL="15s"

# Jaeger
export JAEGER_AGENT_HOST="localhost"
export JAEGER_AGENT_PORT="6831"
```

### Application Settings

```bash
# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FORMAT="json"  # json or text

# Paths
export CLOUDCURIO_HOME="${HOME}/.cloudcurio"
export AGENTS_PATH="${HOME}/cloudcurio/agents"
export CONFIGS_PATH="${HOME}/cloudcurio/configs"

# Performance
export MAX_CONCURRENT_AGENTS="10"
export AGENT_TIMEOUT="300"  # seconds
export RATE_LIMIT="100"  # requests per minute

# Features
export ENABLE_CACHING="true"
export ENABLE_TELEMETRY="true"
export ENABLE_ASYNC_EXECUTION="true"
```

### MCP Server Configuration

```bash
# MCP servers
export MCP_SERVER_AUTOMATION="mcp-servers/automation"
export MCP_SERVER_MEDIA="mcp-servers/media"

# Tool paths
export FFMPEG_PATH="/usr/bin/ffmpeg"
export IMAGEMAGICK_PATH="/usr/bin/convert"
```

## Configuration Files

### Main Configuration

`configs/config.yaml`:

```yaml
# CloudCurio Configuration
version: "1.0"

# Application settings
app:
  name: "cloudcurio"
  environment: "production"  # development, staging, production
  log_level: "INFO"
  log_format: "json"

# Model providers
models:
  default_provider: "ollama"
  default_model: "qwen2.5-coder"
  
  providers:
    ollama:
      base_url: "http://localhost:11434"
      timeout: 30
      
    openai:
      api_key: "${OPENAI_API_KEY}"
      organization: "${OPENAI_ORG_ID}"
      timeout: 60
      
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      timeout: 60

# Runtime settings
runtime:
  default: "local"
  
  local:
    max_concurrent: 10
    timeout: 300
    
  crewai:
    verbose: true
    allow_delegation: false
    
  langchain:
    verbose: true
    max_iterations: 10
    
  pydanticai:
    retry_attempts: 3
    timeout: 300

# Agent settings
agents:
  specs_dir: "agents/specs"
  evals_dir: "agents/evals"
  tools_dir: "agents/tools"
  default_tags: ["production"]

# Workflow settings
workflows:
  workflows_dir: "workflows"
  max_steps: 50
  timeout: 600

# Tool settings
tools:
  timeout: 30
  retry_attempts: 3
  enable_caching: true
  cache_ttl: 300  # seconds

# Observability
observability:
  enabled: true
  
  opentelemetry:
    endpoint: "http://localhost:4317"
    service_name: "cloudcurio-agents"
    
  prometheus:
    enabled: true
    port: 9090
    
  jaeger:
    enabled: true
    agent_host: "localhost"
    agent_port: 6831

# Security
security:
  enable_api_key_validation: true
  rate_limit: 100  # requests per minute
  max_request_size: "10MB"

# Performance
performance:
  enable_caching: true
  cache_backend: "memory"  # memory, redis
  enable_async: true
  worker_threads: 4
```

### Environment-Specific Configs

`configs/development.yaml`:

```yaml
app:
  environment: "development"
  log_level: "DEBUG"

models:
  default_provider: "ollama"  # Use local for dev

runtime:
  local:
    max_concurrent: 5  # Lower for dev

observability:
  enabled: true
  opentelemetry:
    endpoint: "http://localhost:4317"
```

`configs/production.yaml`:

```yaml
app:
  environment: "production"
  log_level: "INFO"

models:
  default_provider: "openai"  # Use cloud for prod

runtime:
  local:
    max_concurrent: 20  # Higher for prod

security:
  enable_api_key_validation: true
  rate_limit: 1000

performance:
  enable_caching: true
  cache_backend: "redis"
```

### Loading Configuration

```python
from cbw_foundry.config import load_config

# Load default config
config = load_config()

# Load environment-specific config
config = load_config(env="production")

# Access configuration
api_key = config.models.providers.openai.api_key
timeout = config.runtime.local.timeout
```

## Model Configuration

### Provider Configuration

Each provider has specific configuration:

**OpenAI:**

```yaml
models:
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      organization: "${OPENAI_ORG_ID}"
      base_url: "https://api.openai.com/v1"  # Optional
      timeout: 60
      max_retries: 3
      models:
        - gpt-4-turbo
        - gpt-4
        - gpt-3.5-turbo
```

**Anthropic:**

```yaml
models:
  providers:
    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      timeout: 60
      max_retries: 3
      models:
        - claude-3-opus-20240229
        - claude-3-sonnet-20240229
        - claude-3-haiku-20240307
```

**Ollama:**

```yaml
models:
  providers:
    ollama:
      base_url: "http://localhost:11434"
      timeout: 30
      models:
        - qwen2.5-coder
        - llama3.1
        - mistral
```

### Model Fallback Strategy

```yaml
models:
  fallback_strategy:
    enabled: true
    max_fallbacks: 3
    fallback_order:
      - provider: ollama
        model: qwen2.5-coder
      - provider: openai
        model: gpt-4-turbo
      - provider: anthropic
        model: claude-3-sonnet
```

## Runtime Configuration

### Local Runtime

```yaml
runtime:
  local:
    enabled: true
    max_concurrent: 10
    timeout: 300
    enable_async: true
    worker_threads: 4
```

### CrewAI Runtime

```yaml
runtime:
  crewai:
    enabled: true
    verbose: true
    allow_delegation: false
    max_iterations: 10
    timeout: 600
```

### LangChain Runtime

```yaml
runtime:
  langchain:
    enabled: true
    verbose: true
    max_iterations: 15
    enable_tracing: true
    timeout: 600
    tools:
      search_enabled: true
      calculator_enabled: true
```

### PydanticAI Runtime

```yaml
runtime:
  pydanticai:
    enabled: true
    retry_attempts: 3
    timeout: 300
    enable_validation: true
```

## Tool Configuration

### Tool Registry

`configs/tools.yaml`:

```yaml
tools:
  # Global tool settings
  global:
    timeout: 30
    retry_attempts: 3
    enable_caching: true
    cache_ttl: 300
  
  # Python tools
  python:
    enabled: true
    max_execution_time: 30
    
  # Shell tools
  shell:
    enabled: true
    allowed_commands:
      - ls
      - echo
      - cat
      - grep
    max_execution_time: 60
    
  # MCP tools
  mcp:
    enabled: true
    servers:
      automation:
        enabled: true
        command: "node"
        args: ["mcp-servers/automation/index.js"]
      media:
        enabled: true
        command: "node"
        args: ["mcp-servers/media/index.js"]
        
  # HTTP tools
  http:
    enabled: true
    timeout: 30
    max_retries: 3
    rate_limit: 100
```

### Tool-Specific Configuration

```yaml
tools:
  data_processor:
    max_records: 1000
    output_format: "json"
    
  api_client:
    timeout: 30
    max_retries: 3
    base_url: "https://api.example.com"
    
  file_handler:
    max_file_size: "10MB"
    allowed_extensions:
      - .txt
      - .json
      - .yaml
```

## Agent-Specific Configuration

### In Agent Specs

```yaml
api_version: v1
kind: Agent
metadata:
  name: custom_agent
  version: 1.0.0
spec:
  model_policy:
    preferred:
      provider: ollama
      model: qwen2.5-coder
    fallbacks:
      - provider: openai
        model: gpt-4-turbo
  
  runtime:
    supported: [local, pydanticai]
    config:
      timeout: 600
      max_retries: 5
  
  tools:
    - id: data_processor
      type: python
      entrypoint: agents/tools/python/data_processor.py:process_data
      config:
        max_records: 500
        output_format: json
```

## Command-Line Overrides

Override configuration via CLI:

```bash
# Override model
./bin/cbw-agent run my_agent.yaml \
  --input "test" \
  --model openai/gpt-4

# Override runtime
./bin/cbw-agent run my_agent.yaml \
  --input "test" \
  --runtime crewai

# Override timeout
./bin/cbw-agent run my_agent.yaml \
  --input "test" \
  --timeout 600

# Multiple overrides
./bin/cbw-agent run my_agent.yaml \
  --input "test" \
  --model openai/gpt-4 \
  --runtime pydanticai \
  --timeout 300 \
  --verbose
```

## Best Practices

### 1. Environment Variables

- Use `.env` files for local development
- Never commit API keys to git
- Use secret management in production
- Document all required variables

### 2. Configuration Files

- Keep sensitive data out of config files
- Use environment variable substitution
- Version control configuration templates
- Maintain separate configs per environment

### 3. Security

- Rotate API keys regularly
- Use least privilege access
- Enable rate limiting
- Validate all configuration values

### 4. Performance

- Tune timeouts appropriately
- Enable caching where beneficial
- Monitor resource usage
- Adjust concurrency limits

### 5. Observability

- Enable telemetry in production
- Configure appropriate log levels
- Set up monitoring alerts
- Track configuration changes

## Additional Resources

- [Agent Development Guide](AGENT_DEVELOPMENT.md)
- [Tool Development Guide](TOOL_DEVELOPMENT.md)
- [Observability Guide](OBSERVABILITY.md)

---

**Last Updated:** 2026-01-24  
**Version:** 1.0.0  
**Maintained By:** @cbwinslow
