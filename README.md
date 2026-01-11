# CloudCurio Monorepo (Master Toolbox)

**Goal:** One reusable, industry-grade source of truth for AI agents, tools, workflows, and automation.

**Generated:** 2026-01-11

## Quick Start

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
```

## Common Commands

```bash
make doctor        # Check repo health
make index        # Generate registry indexes
make validate      # Validate agent specs
make compile      # Compile agents to JSON
make eval         # Run golden test suites
make test         # Run Python tests
make lint         # Lint with ruff
make fmt          # Format code
```

## CLI Surface

```bash
./bin/cbw doctor                                   # Health check
./bin/cbw index                                   # Update registry
./bin/cbw-agent validate agents/specs/**/*.agent.yaml
./bin/cbw-agent compile agents/specs/**/*.agent.yaml --out dist/agents
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local
./bin/cbw-capture agent my_agent                   # Create new agent
```

## Project Structure

- `agents/` - Agent specs, tools, evals
- `workflows/` - Repeatable YAML workflows
- `kb/` - Knowledge base, runbooks, ADRs
- `src/` - Python package (cbw_foundry)
- `bin/` - CLI entrypoints
- `shell/` - Shell library and init scripts
- `docker/` - Docker compose stacks
- `registry/` - Auto-generated indexes

## Philosophy

- Specs in YAML (human-friendly), compiled artifacts in JSON (machine-friendly)
- Everything works locally without paid services
- Optional integrations are env-driven
- Treat as internal tooling at a serious AI company
