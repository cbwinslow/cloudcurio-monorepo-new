# Changelog

All notable changes to CloudCurio Monorepo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation expansion across all core files
- Detailed KB (Knowledge Base) with runbooks, ADRs, and context
- Enhanced installation, quickstart, and upgrade guides

## [0.4.0] - 2026-01-11

### Added

**Repository Infrastructure:**
- ✨ Pre-commit hooks for automated code quality checks (ruff, yamllint, trailing whitespace)
- ✨ GitHub Actions CI/CD pipeline with automated testing and validation
- ✨ Comprehensive Makefile with common development targets (doctor, index, validate, compile, eval, test, lint, fmt)
- ✨ Enhanced .gitignore for Python, Node.js, and build artifacts
- ✨ CODEOWNERS file for repository ownership

**Agent System:**
- ✨ Agent Specification v1 with formal Pydantic schema
- ✨ YAML-to-JSON compilation pipeline for performance optimization
- ✨ Golden evaluation harness for automated agent testing
- ✨ Agent scaffolding tool (`cbw-capture`) for quick agent creation
- ✨ Agent registry system for discovery and cataloging
- ✨ Support for multiple agent frameworks (CrewAI, PydanticAI, LangChain)
- ✨ 31+ pre-built specialized agents in agents/library/
- ✨ Multi-agent orchestration system with swarm coordination
- ✨ Agent evaluation framework with test suites

**Runtime & Framework:**
- ✨ Runtime adapter pattern for framework independence
- ✨ Local runtime fully implemented with agent execution
- ✨ Framework adapter stubs for PydanticAI, LangChain, CrewAI
- ✨ Unified runtime interface for consistent execution
- ✨ Runtime configuration per agent specification

**Tooling:**
- ✨ 45+ pre-built tools organized by domain
- ✨ BaseTool interface for consistent tool development
- ✨ Tool registry system for discovery
- ✨ Domain-specific toolsets (podcast production, video editing, social media)
- ✨ MCP (Model Context Protocol) server integration
- ✨ Automation and media MCP servers

**CLI Commands:**
- ✨ `cbw-doctor` - Comprehensive repository health checks
- ✨ `cbw-index` - Registry generation and updates
- ✨ `cbw-agent` - Agent validation, compilation, execution, and evaluation
- ✨ `cbw-workflow` - Workflow management and execution
- ✨ `cbw-capture` - Agent and workflow scaffolding
- ✨ Enhanced CLI with verbose output and error reporting

**Observability:**
- ✨ OpenTelemetry integration for distributed tracing
- ✨ Docker Compose stack for Prometheus, Grafana, Jaeger
- ✨ Health monitoring and diagnostic systems
- ✨ Telemetry collection and reporting
- ✨ Structured logging with JSON format support

**Documentation:**
- ✨ Knowledge Base (KB) structure with runbooks, ADRs, context, and rules
- ✨ Architecture Decision Records (ADR-0001: Monorepo Structure)
- ✨ Comprehensive installation guide with platform-specific instructions
- ✨ Quickstart tutorial for rapid onboarding
- ✨ Upgrade guide with automated migration scripts
- ✨ Code quality rules and standards
- ✨ Security policy (SECURITY.md)

**Testing:**
- ✨ Pytest-based test suite for Python code
- ✨ Golden test framework for agent evaluation
- ✨ Test fixtures and utilities
- ✨ Coverage reporting integration
- ✨ Pre-commit test hooks

**Development Tools:**
- ✨ Bootstrap script for automated environment setup
- ✨ Upgrade script for safe version migration
- ✨ Ruff for Python linting and formatting
- ✨ MyPy for static type checking
- ✨ YAML validation in pre-commit hooks

### Changed

**Agent Specifications:**
- 🔄 Agent specs now use formal v1 schema with validation
- 🔄 YAML format for human authoring, JSON for execution
- 🔄 Required fields: name, version, description, system_prompt
- 🔄 Enhanced tool configuration with per-tool settings
- 🔄 Runtime configuration embedded in spec

**Repository Structure:**
- 🔄 Reorganized agents/ directory with clear separation:
  - `specs/` - YAML agent definitions
  - `library/` - Pre-built agents
  - `orchestrator/` - Multi-agent coordination
  - `tools/` - Tool implementations
  - `toolsets/` - Domain collections
  - `evals/` - Test suites
- 🔄 Created `kb/` directory for knowledge base
- 🔄 Created `registry/` for auto-generated catalogs
- 🔄 Moved core framework to `src/cbw_foundry/`

**Build Process:**
- 🔄 Added compilation step (YAML → JSON)
- 🔄 Registry generation from specs
- 🔄 Automated validation in CI
- 🔄 Pre-commit hooks enforce quality

**Dependencies:**
- 🔄 Updated to Pydantic v2.x
- 🔄 Added OpenTelemetry SDK
- 🔄 Added pytest and testing dependencies
- 🔄 Added ruff for linting
- 🔄 Pinned critical dependencies for stability

### Fixed

- 🐛 Agent specification validation edge cases
- 🐛 Tool discovery and registration issues
- 🐛 Import path resolution in runtime adapters
- 🐛 Pre-commit hook compatibility issues
- 🐛 Documentation inconsistencies

### Deprecated

- ⚠️ Old agent format (pre-v1 schema) - migrate using upgrade script
- ⚠️ Direct framework imports - use runtime adapters
- ⚠️ Function-based tools - use BaseTool classes

### Removed

- ❌ Legacy agent execution code
- ❌ Outdated documentation
- ❌ Unused dependencies

### Security

- 🔒 Added security policy (SECURITY.md)
- 🔒 Dependency vulnerability scanning via pre-commit
- 🔒 Secrets excluded from git via .gitignore
- 🔒 Security-focused code quality rules

## [0.3.0] - 2025-12-XX

### Added
- Initial agent orchestration framework
- Basic tool library
- CrewAI integration experiments

### Changed
- Refined agent architecture
- Improved tool interfaces

## [0.2.0] - 2025-11-XX

### Added
- Initial agent specification format
- Basic CLI tools
- Example agents

### Changed
- Repository structure refinements

## [0.1.0] - 2025-10-XX

### Added
- Initial repository setup
- Basic project structure
- Core dependencies
- README and initial documentation

---

## Version History Overview

| Version | Date | Key Focus |
|---------|------|-----------|
| 0.4.0 | 2026-01-11 | Hardening, schemas, observability, production-ready |
| 0.3.0 | 2025-12-XX | Orchestration, multi-agent systems |
| 0.2.0 | 2025-11-XX | Agent specs, CLI tooling |
| 0.1.0 | 2025-10-XX | Initial release, project foundation |

## Migration Guides

### Migrating from v0.3.x to v0.4.0

1. **Run the upgrade script:**
   ```bash
   ./scripts/upgrade_existing_repo.sh --old <path> --backup-dir <backup> --apply
   ```

2. **Update agent specifications to v1 schema:**
   - Add `version: "X.Y.Z"` field
   - Add `description:` field
   - Ensure `system_prompt:` is defined
   - Update `tools:` from list to objects with descriptions

3. **Re-bootstrap environment:**
   ```bash
   ./scripts/bootstrap.sh
   ```

4. **Validate and compile:**
   ```bash
   make validate compile
   ```

5. **Update tool implementations:**
   - Inherit from `BaseTool` class
   - Implement `execute()` method
   - Add proper docstrings

6. **Run tests:**
   ```bash
   make test eval
   ```

### Migrating from v0.2.x to v0.3.0

1. Update agent imports
2. Migrate to orchestration patterns
3. Update tool interfaces

### Migrating from v0.1.x to v0.2.0

1. Update repository structure
2. Migrate agent specs
3. Update CLI usage

## Roadmap

### v0.5.0 (Planned)

**Themes:** Enhanced Multi-Agent Collaboration, Production Deployments

- [ ] Advanced swarm coordination patterns
- [ ] Production deployment guides and tooling
- [ ] Enhanced observability dashboards
- [ ] Agent marketplace/registry UI
- [ ] Workflow visual editor
- [ ] Performance optimization pass
- [ ] Additional runtime adapters (AutoGen, custom frameworks)

### v0.6.0 (Planned)

**Themes:** Enterprise Features, Scale

- [ ] RBAC and access control
- [ ] Multi-tenancy support
- [ ] Advanced caching strategies
- [ ] Distributed agent execution
- [ ] Enhanced security features
- [ ] Compliance tooling (SOC2, GDPR)

### v1.0.0 (Target: Q2 2026)

**Themes:** Production Ready, Stable API

- [ ] Stable, backward-compatible API
- [ ] Comprehensive documentation
- [ ] Production deployments at scale
- [ ] Enterprise support model
- [ ] Full test coverage (>90%)
- [ ] Performance benchmarks
- [ ] Security audit complete

## Contributing

See [Code Quality Rules](kb/rules/code_quality_rules.md) for contribution guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/cbwinslow/cloudcurio-monorepo-new/issues)
- **Documentation**: [docs/](docs/) and [kb/](kb/)
- **Security**: See [SECURITY.md](SECURITY.md)

---

**Format:** Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
**Versioning:** [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
**Maintained By:** @cbwinslow
