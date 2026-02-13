# CloudCurio Monorepo Context

## Project Identity

- **Name**: CloudCurio Monorepo (Master Toolbox)
- **Version**: v0.4.0
- **Purpose**: Production-grade AI agent framework and automation ecosystem
- **Created**: 2026-01-11
- **Maintainer**: @cbwinslow

## Architecture Overview

### Core Philosophy

1. **Local-First**: Everything runs locally without external dependencies; paid services are opt-in
2. **Human-First Authoring**: Write specs in YAML for readability
3. **Machine-Optimized Execution**: Compile to JSON for performance
4. **Framework Agnostic**: Support multiple agent frameworks (CrewAI, LangChain, PydanticAI, Local)
5. **Production-Grade**: Built with standards of internal tooling at serious AI companies

### Key Components

#### 1. Agent Framework
- **Multi-framework support**: Local runtime (fully implemented), CrewAI/LangChain/PydanticAI (adapter stubs)
- **Declarative specs**: YAML → JSON compilation pipeline
- **30+ specialized agents**: Audio, video, social media, GitHub, transcription, testing, quality, security, etc.
- **Agent lifecycle**: Author → Validate → Compile → Execute → Evaluate

#### 2. Tool Ecosystem
- **Content creation tools**: Podcast production, video editing, social media automation
- **Development tools**: Code analysis, refactoring, test generation
- **Integration tools**: GitHub API, MCP servers, database connectors

#### 3. Workflow Orchestration
- **YAML-based workflows**: Multi-step automation sequences
- **Agent composition**: Coordinate multiple agents for complex tasks
- **Dependency management**: Define step dependencies and data flow

#### 4. MCP (Model Context Protocol) Servers
- **Automation server**: System commands, file operations, process management
- **Media server**: Audio/video processing, transcription, format conversion
- **Content optimizer server**: SEO, readability, engagement optimization

#### 5. Observability
- **OpenTelemetry integration**: Distributed tracing and metrics
- **Health monitoring**: Comprehensive system health checks
- **Docker observability stack**: Prometheus, Grafana, Jaeger

## Technology Stack

### Primary Languages
- **Python 3.11+**: Core framework, agents, tools, CLI
- **Bash**: Shell utilities, bootstrap scripts, init scripts
- **YAML**: Agent specs, workflows, configurations
- **JSON**: Compiled agent artifacts, runtime configurations

### Key Dependencies
- **pydantic**: Data validation and configuration
- **PyYAML**: YAML parsing and generation
- **rich**: Terminal UI and formatting
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **mypy**: Static type checking

### Optional Dependencies
- **langchain**: LangChain framework support
- **crewai**: CrewAI framework support
- **pydantic-ai**: PydanticAI framework support
- **opentelemetry-api/sdk**: Observability stack

## Development Environment

### Prerequisites
- Python 3.10+ with pip and venv
- Node.js 18+ (for MCP servers and some tools)
- Docker and Docker Compose (optional, for observability)
- Git 2.30+

### Setup Commands
```bash
./scripts/bootstrap.sh   # Initial setup
make doctor             # Health check
make index              # Generate registries
```

### Common Workflows
```bash
make test               # Run test suite
make lint               # Lint code
make fmt                # Format code
make validate           # Validate agent specs
make compile            # Compile specs to JSON
make eval               # Run golden tests
```

## Current State

### ✅ Well-Implemented
- Comprehensive agent library (30+ modules)
- Declarative YAML spec system with validation
- Multi-framework runtime adapters (architecture in place)
- Extensive documentation (installation, quickstart, development guides)
- Pre-commit hooks and code quality gates
- CI/CD with GitHub Actions (testing, linting, validation)
- Security scanning (gitleaks weekly)
- MCP server implementations
- OpenTelemetry observability integration
- Docker deployment stack

### 🔄 Partially Implemented
- Runtime adapters: Only Local fully implemented; CrewAI/LangChain/PydanticAI are stubs
- Agent evaluations: Golden test infrastructure exists but limited coverage
- Workflow orchestration: Framework exists but limited workflow library
- Performance monitoring: Infrastructure present but not extensively used

### ❌ Gaps/Missing
- Comprehensive integration tests
- Performance benchmarking suite
- Automated release workflows
- Documentation deployment automation
- Windows-specific setup guides
- Agent capability discovery API

## Code Organization

### Directory Structure
```
agents/          - Agent ecosystem (library, specs, evals, tools, toolsets)
src/cbw_foundry/ - Core Python framework (CLI, runtime, spec compiler)
workflows/       - YAML workflow definitions
mcp-servers/     - Model Context Protocol servers
kb/              - Knowledge base (runbooks, decisions, rules)
docs/            - User-facing documentation
tests/           - Python test suite
scripts/         - Utility scripts
bin/             - CLI entrypoints
shell/           - Shell library and init scripts
```

### Important Files
- `pyproject.toml`: Python project configuration, dependencies, tool settings
- `Makefile`: Common development commands
- `README.md`: Project overview and quick reference
- `CHANGELOG.md`: Version history and release notes
- `.pre-commit-config.yaml`: Pre-commit hook configuration

## Naming Conventions

### Files
- Python modules: `lowercase_with_underscores.py`
- Agent specs: `agent_name.agent.yaml`
- Workflow definitions: `workflow_name.yaml`
- Test files: `test_module_name.py`

### Code
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

### Agents
- Agent names: `lowercase_snake_case` (e.g., `transcription_agent`)
- Agent files: `agent_name.agent.yaml`
- Agent modules: `agent_name_agent.py`

## Testing Strategy

### Test Types
1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Golden Tests**: Validate agent behavior with expected outputs
4. **Evaluation Tests**: Measure agent quality and performance

### Test Locations
- `tests/python/`: Unit and integration tests
- `agents/evals/golden/`: Golden test suites for agents
- `agents/evals/`: Agent-specific evaluation suites

### Coverage Requirements
- Minimum 80% code coverage for new code
- 100% coverage for security-sensitive code
- All public APIs must have tests

## Agent Development Patterns

### Agent Types

1. **Specialized Domain Agents**: Audio, video, social media, transcription, GitHub
2. **System Agents**: Testing, quality, security, performance, documentation, refactoring
3. **Orchestration Agents**: Mission control, swarm orchestrator, multi-agent coordinator
4. **Utility Modules**: Health check, telemetry, diagnostics, monitoring

### Agent Lifecycle

1. **Create**: Scaffold with `./bin/cbw-capture agent name`
2. **Author**: Write YAML spec in `agents/specs/`
3. **Validate**: Run `./bin/cbw-agent validate`
4. **Test**: Create golden tests in `agents/evals/`
5. **Compile**: Generate JSON with `./bin/cbw-agent compile`
6. **Execute**: Run with `./bin/cbw-agent run`
7. **Evaluate**: Test quality with `./bin/cbw-agent eval`

## Runtime Adapters

### Supported Runtimes
- **local**: Built-in lightweight execution (✅ fully implemented)
- **crewai**: Multi-agent collaboration (🔄 adapter stub)
- **pydanticai**: Type-safe agents (🔄 adapter stub)
- **langchain**: LLM framework (🔄 adapter stub)

### Adapter Pattern
All adapters implement a unified interface for framework-agnostic agent execution. The local runtime provides the reference implementation.

## Security Considerations

### Secret Management
- Never commit secrets to repository
- Use environment variables for API keys
- Store sensitive data in `.env` files (git-ignored)
- Provide `.env.example` for documentation

### Input Validation
- Validate all user inputs with Pydantic
- Sanitize file paths and shell commands
- Use parameterized queries for databases

### Dependency Security
- Weekly gitleaks scanning for secrets
- Regular dependency updates via pre-commit
- Vulnerability scanning in CI/CD

## Performance Considerations

### Optimization Strategies
- Compile YAML specs to optimized JSON artifacts
- Use async/await for I/O-bound operations
- Implement caching for expensive operations
- Lazy load large resources

### Resource Management
- Set appropriate timeouts for agent execution
- Implement graceful shutdown handling
- Monitor memory usage for long-running processes
- Use streaming for large data processing

## Extension Points

### Adding New Components

1. **New Agent**: Use `cbw-capture agent` scaffolding
2. **New Tool**: Implement in `agents/tools/` with standard interface
3. **New Runtime**: Implement adapter in `src/cbw_foundry/runtime/adapters.py`
4. **New Workflow**: Create YAML definition in `workflows/`
5. **New MCP Server**: Add directory in `mcp-servers/` with standard structure

### Integration Patterns
- MCP server integration for external tools
- Runtime adapter integration for new frameworks
- Tool registration in agent toolsets
- Workflow composition for multi-step automation

## Future Roadmap

### Planned Features
- Full implementation of CrewAI/LangChain/PydanticAI adapters
- Comprehensive agent evaluation suite
- Performance benchmarking framework
- Enhanced workflow orchestration
- Agent capability discovery API
- Automated documentation deployment

### Experimental Features
- Distributed agent execution
- Agent-to-agent communication protocols
- Dynamic tool loading
- Real-time agent monitoring dashboard

---

*This context file provides essential background for GitHub Copilot to generate appropriate suggestions. Keep it updated as the project evolves.*
