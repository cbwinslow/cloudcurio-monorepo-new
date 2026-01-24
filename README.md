# CloudCurio Monorepo (Master Toolbox)

**Goal:** One reusable, industry-grade source of truth for AI agents, tools, workflows, and automation.

**Generated:** 2026-01-11  
**Version:** v0.4.0

## Overview

CloudCurio Monorepo is a comprehensive AI agent framework and tooling ecosystem designed for production-grade automation. It provides a unified platform for:

- **Multi-Framework Agent Support**: CrewAI, PydanticAI, LangChain, and custom swarm systems
- **Declarative Agent Specs**: Define agents in human-friendly YAML, compile to machine-optimized JSON
- **Tool Ecosystem**: Extensive library of pre-built tools for content creation, automation, and system integration
- **Workflow Orchestration**: YAML-based workflow definitions for repeatable automation
- **Observability & Monitoring**: Built-in OpenTelemetry integration and health monitoring
- **Local-First Architecture**: Everything runs locally without external dependencies; paid services are optional

## Table of Contents

- [Quick Start](#quick-start)
- [Common Commands](#common-commands)
- [CLI Reference](#cli-surface)
- [Project Structure](#project-structure)
- [Agent Systems](#agent-systems)
- [Development Workflow](#development-workflow)
- [Philosophy](#philosophy)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Quick Start

### Prerequisites

- Python 3.10+ with pip and venv
- Node.js 18+ (for MCP servers and some tools)
- Docker and Docker Compose (optional, for observability stack)
- Git 2.30+

### Installation

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
```

The bootstrap script will:
1. Create Python virtual environment
2. Install all dependencies via pip
3. Install pre-commit hooks
4. Verify core CLI tools are available
5. Run initial health checks

### Verify Installation

```bash
make doctor        # Comprehensive health check
make index         # Generate registry indexes
```

## Common Commands

### Repository Management

```bash
make doctor        # Check repo health - validates all systems
make index         # Generate registry indexes for agents and tools
```

### Agent Development

```bash
make validate      # Validate all agent YAML specifications
make compile       # Compile agent specs from YAML to JSON
make eval          # Run golden test suites for agent validation
```

### Code Quality

```bash
make test          # Run full Python test suite with pytest
make lint          # Lint code with ruff (Python linter)
make fmt           # Auto-format code with ruff formatter
```

### Advanced Operations

```bash
make clean         # Clean generated artifacts
make install       # Install/reinstall Python package
make pre-commit    # Run all pre-commit hooks manually
```

## CLI Surface

### Health & Registry Commands

```bash
./bin/cbw doctor                                   # Full health check
./bin/cbw index                                    # Update registry
```

### Agent Management

```bash
# Validate agent specifications
./bin/cbw-agent validate agents/specs/**/*.agent.yaml

# Compile YAML specs to JSON artifacts
./bin/cbw-agent compile agents/specs/**/*.agent.yaml --out dist/agents

# Run an agent locally
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local

# Run with different runtimes
./bin/cbw-agent run my_agent.yaml --runtime langchain --input "data"
./bin/cbw-agent run my_agent.yaml --runtime crewai --input "task"
```

### Agent Creation

```bash
# Scaffold a new agent with templates
./bin/cbw-capture agent my_agent                   

# Creates:
# - agents/specs/my_agent.agent.yaml
# - agents/evals/my_agent/golden_test.yaml
# - Basic tool and system prompt templates
```

### Workflow Management

```bash
# Run a workflow
./bin/cbw-workflow run workflows/my_workflow.yaml

# Validate workflow definitions
./bin/cbw-workflow validate workflows/**/*.yaml
```

### Index Management

```bash
# Generate all indexes
./bin/cbw-index generate

# Update specific index
./bin/cbw-index update agents
./bin/cbw-index update tools
```

## Project Structure

### Core Directories

- **`agents/`** - Complete agent ecosystem
  - `specs/` - YAML agent specifications
  - `library/` - Pre-built specialized agents (31+ modules)
  - `orchestrator/` - Multi-agent coordination system
  - `tools/` - Reusable tool implementations
  - `toolsets/` - Domain-specific tool collections
  - `evals/` - Golden test suites for validation
  - `crewai/` - CrewAI framework integrations
  - `specialized/` - Domain-expert agents

- **`src/cbw_foundry/`** - Core Python framework
  - CLI tools (cbw, cbw-agent, cbw-workflow, etc.)
  - Runtime adapters (local, langchain, pydanticai, crewai)
  - Spec compiler (YAML → JSON)
  - Observability integration (OpenTelemetry)
  - Evaluation harness

- **`workflows/`** - Repeatable YAML workflow definitions
  - Multi-step automation sequences
  - Agent composition patterns
  - Integration workflows

- **`kb/`** - Knowledge base and documentation
  - `runbooks/` - Operational procedures
  - `decisions/` - Architecture Decision Records (ADRs)
  - `context/` - Environment and system context
  - `rules/` - Code quality and contribution guidelines

- **`bin/`** - CLI entrypoints
  - Shell wrappers for Python CLI tools
  - System executables

- **`shell/`** - Shell library and init scripts
  - Bash utilities and helper functions
  - Environment setup scripts

- **`docker/`** - Docker compose stacks
  - `compose/observability/` - Prometheus, Grafana, Jaeger
  - Container definitions for deployment

- **`registry/`** - Auto-generated indexes
  - Agent catalog
  - Tool registry
  - Workflow index
  - Generated by `cbw-index` CLI

- **`mcp/` & `mcp-servers/`** - Model Context Protocol servers
  - `automation/` - Automation tools server
  - `media/` - Media processing server
  - MCP integration layer

- **`docs/`** - User-facing documentation
  - Installation guides
  - Quickstart tutorials
  - Upgrade procedures
  - API reference

- **`tests/`** - Python test suite
  - Unit tests
  - Integration tests
  - Test fixtures

- **`prompts/`** - System prompts and templates
  - Default system prompts
  - Prompt engineering templates
  - Agent persona definitions

- **`configs/`** - Global configuration templates
  - Environment variable templates
  - Runtime configurations
  - Tool settings

- **`scripts/`** - Utility scripts
  - `bootstrap.sh` - Initial setup
  - `upgrade_existing_repo.sh` - Version migration
  - Build and deployment utilities

## Agent Systems

### Multi-Framework Support

CloudCurio supports multiple agent frameworks through a unified runtime adapter interface:

**Supported Frameworks:**
- ✅ **Local Runtime** - Built-in, lightweight execution (fully implemented)
- ✅ **CrewAI** - Multi-agent collaboration framework
- ✅ **PydanticAI** - Type-safe agent definitions with Pydantic
- 🔄 **LangChain** - Industry-standard LLM framework (adapter stub)

### Agent Types

**Specialized Domain Agents:**
- Audio Engineer - Professional audio processing and mixing
- Video Editor - Video editing and post-production
- Social Media Manager - Multi-platform social media automation
- Transcription Agent - Audio/video transcription with speaker diarization
- GitHub Agent - Repository management and code operations
- Content Analyst - Content quality and SEO analysis

**System Agents:**
- Testing Agent - Automated test generation and execution
- Quality Agent - Code quality analysis and improvements
- Security Agent - Security vulnerability scanning
- Performance Agent - Performance profiling and optimization
- Documentation Agent - Automated documentation generation
- Refactoring Agent - Code refactoring and modernization

**Orchestration Systems:**
- Mission Control - High-level multi-agent coordination
- Swarm Orchestrator - Distributed agent task management
- Multi-Agent Coordinator - Agent communication and state management

**Monitoring & Diagnostics:**
- Health Check Agent - System health monitoring
- Diagnostic System - Automated troubleshooting
- Telemetry Agent - Metrics collection and reporting
- Observability Agent - Distributed tracing integration

### Tool Ecosystem

**Content Creation Tools:**
- Podcast production toolset (audio engineering, editing, distribution)
- Video editing suite (cutting, transitions, effects)
- Social media automation (scheduling, analytics, engagement)
- Content optimization (SEO, readability, engagement)

**Development Tools:**
- Code analysis and refactoring
- Test generation and execution
- Documentation generation
- Performance profiling

**Integration Tools:**
- GitHub API integration
- MCP server tools (automation, media)
- Database connectors
- API clients

## Development Workflow

### Creating a New Agent

1. **Scaffold the agent structure:**
   ```bash
   ./bin/cbw-capture agent my_new_agent
   ```

2. **Edit the agent specification:**
   ```bash
   # Edit agents/specs/my_new_agent.agent.yaml
   # Define name, description, tools, system_prompt, etc.
   ```

3. **Validate the specification:**
   ```bash
   ./bin/cbw-agent validate agents/specs/my_new_agent.agent.yaml
   ```

4. **Create golden test cases:**
   ```bash
   # Edit agents/evals/my_new_agent/golden_test.yaml
   # Add test inputs and expected outputs
   ```

5. **Run evaluations:**
   ```bash
   make eval
   # Or target specific agent:
   ./bin/cbw-agent eval agents/specs/my_new_agent.agent.yaml
   ```

6. **Compile for production:**
   ```bash
   make compile
   # Generates dist/agents/my_new_agent.agent.json
   ```

7. **Test locally:**
   ```bash
   ./bin/cbw-agent run agents/specs/my_new_agent.agent.yaml \
     --input "test input" \
     --runtime local
   ```

### Adding a Custom Tool

1. **Create tool module:**
   ```python
   # agents/tools/my_tool.py
   from cbw_foundry.tools import BaseTool
   
   class MyTool(BaseTool):
       name = "my_tool"
       description = "Description of what this tool does"
       
       def execute(self, **kwargs):
           # Implementation
           pass
   ```

2. **Register in tool registry:**
   ```python
   # Add to agents/tools/__init__.py
   from .my_tool import MyTool
   
   __all__ = ["MyTool", ...]
   ```

3. **Reference in agent spec:**
   ```yaml
   # agents/specs/my_agent.agent.yaml
   tools:
     - name: my_tool
       config:
         # Tool-specific configuration
   ```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_agent_spec.py

# Run with coverage
pytest --cov=cbw_foundry tests/

# Run linting
make lint

# Auto-fix linting issues
make fmt
```

## Philosophy

### Design Principles

- **Human-First Authoring**: Specs written in YAML for readability and maintainability
- **Machine-Optimized Execution**: Compiled artifacts in JSON for performance
- **Local-First Development**: Everything runs locally without external dependencies
- **Optional Cloud Integration**: Paid services are opt-in via environment variables
- **Production-Grade Tooling**: Built with the standards of internal tooling at a serious AI company
- **Framework Agnostic**: Support multiple agent frameworks through unified interfaces
- **Observability by Default**: Built-in monitoring, tracing, and health checks
- **Test-Driven Quality**: Golden evaluation suites ensure agent reliability

### Core Values

- **Reliability**: Agents should be deterministic and testable
- **Composability**: Tools and agents should compose seamlessly
- **Maintainability**: Clear structure and comprehensive documentation
- **Performance**: Efficient execution with minimal overhead
- **Security**: Security-first approach with vulnerability scanning
- **Extensibility**: Easy to add new agents, tools, and frameworks

## Documentation

### Getting Started
- [Installation Guide](docs/INSTALL.md) - Complete setup instructions
- [Quickstart Tutorial](docs/QUICKSTART.md) - Get running in 5 minutes
- [Upgrade Guide](docs/UPGRADE.md) - Migrate from older versions

### Knowledge Base
- [Using the Repo](kb/runbooks/using_the_repo.md) - Daily workflows and operations
- [Adding New Agents](kb/runbooks/adding_new_agent.md) - Agent development guide
- [Architecture Decisions](kb/decisions/) - ADR documentation
- [Code Quality Rules](kb/rules/code_quality_rules.md) - Coding standards

### Agent Development
- [Agent Specifications](docs/AGENT_DEVELOPMENT.md) - Agent spec format and patterns
- [Tool Development](docs/TOOL_DEVELOPMENT.md) - Creating custom tools
- [Runtime Adapters](docs/RUNTIME_ADAPTERS.md) - Framework integration guide
- [Swarm Architecture](docs/SWARM_ARCHITECTURE.md) - Multi-agent coordination

### Operations
- [Docker Deployment](docs/DOCKER_DEPLOYMENT.md) - Container setup
- [MCP Servers](docs/MCP_SERVERS.md) - Model Context Protocol integration
- [Testing Guide](docs/TESTING_GUIDE.md) - Testing and evaluation
- [Configuration Reference](docs/CONFIGURATION.md) - Environment variables and settings
- [Observability](docs/OBSERVABILITY.md) - Monitoring and telemetry

## Contributing

### Code Quality Standards

All contributions must pass:
- ✅ Pre-commit hooks (ruff, yamllint, trailing whitespace)
- ✅ Test suite (`make test`)
- ✅ Agent validation (`make validate`)
- ✅ Linting (`make lint`)

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code quality rules in `kb/rules/`
4. Run tests and validation: `make test validate lint`
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Review

All PRs require:
- Passing CI checks
- Code review approval
- Documentation updates (if adding features)
- Test coverage for new code

## Support & Community

- **Issues**: Report bugs via [GitHub Issues](https://github.com/cbwinslow/cloudcurio-monorepo-new/issues)
- **Documentation**: Full docs in `docs/` and `kb/`
- **Examples**: See `agents/specs/examples/` for reference implementations

## License

See [LICENSE](LICENSE) file for details.

## Security

See [SECURITY.md](SECURITY.md) for security policy and vulnerability reporting.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

**Version:** v0.4.0  
**Last Updated:** 2026-01-11  
**Maintained by:** @cbwinslow
