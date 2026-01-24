# Quickstart Guide

Get up and running with CloudCurio Monorepo in under 5 minutes.

## Prerequisites

Before starting, ensure you have:

- **Python 3.10 or higher** with pip and venv
- **Node.js 18 or higher** (for MCP servers)
- **Git 2.30+**
- **Docker & Docker Compose** (optional, for observability)
- **~500MB disk space** for dependencies

Check your versions:
```bash
python --version   # Should be 3.10+
node --version     # Should be v18+
git --version      # Should be 2.30+
```

## Step 1: Clone or Extract Repository

If cloning from GitHub:
```bash
cd ~/Documents
mkdir -p cloudcurio_monorepo
cd cloudcurio_monorepo
git clone <repository-url> cloudcurio-monorepo
cd cloudcurio-monorepo
```

If using a zip distribution:
```bash
cd ~/Documents
mkdir -p cloudcurio_monorepo
cd cloudcurio_monorepo
unzip cloudcurio-monorepo-FINAL.zip -d .
cd cloudcurio-monorepo
```

## Step 2: Bootstrap the Environment

Run the automated bootstrap script:
```bash
./scripts/bootstrap.sh
```

This script will:
1. ✅ Create Python virtual environment in `.venv/`
2. ✅ Install Python dependencies from `pyproject.toml`
3. ✅ Install pre-commit hooks for code quality
4. ✅ Verify CLI tools are properly installed
5. ✅ Run initial sanity checks

**Expected output:**
```
✓ Python virtual environment created
✓ Dependencies installed
✓ Pre-commit hooks installed
✓ CLI tools verified
✓ Bootstrap complete!
```

## Step 3: Verify Installation

Run the health check to ensure everything is configured correctly:
```bash
make doctor
```

This validates:
- ✅ Python environment and dependencies
- ✅ CLI tools are in PATH
- ✅ Directory structure is intact
- ✅ Agent specifications are valid
- ✅ Registry indexes are current

Expected output: All checks should pass with ✓ marks.

## Step 4: Generate Registry Indexes

Build the agent and tool registries:
```bash
make index
```

This creates:
- `registry/agents.json` - Catalog of all available agents
- `registry/tools.json` - Catalog of all available tools
- `registry/workflows.json` - Catalog of workflow definitions

## Step 5: Validate & Compile Agents

Validate all agent specifications:
```bash
make validate
```

Compile agent specs to JSON artifacts:
```bash
make compile
```

This generates machine-optimized JSON files in `dist/agents/`.

## Step 6: Run Your First Agent

Test the hello_world example agent:
```bash
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local
```

**Expected output:**
```
Running agent: hello_world
Runtime: local
Input: hello
---
[Agent processes input]
Output: [Agent response]
✓ Execution complete
```

## Step 7: Run Golden Evaluations

Verify agents work correctly with golden test suites:
```bash
make eval
```

This runs all test cases in `agents/evals/` and reports:
- ✅ Passed tests
- ❌ Failed tests
- 📊 Coverage metrics

## Next Steps

### Create Your First Agent

Scaffold a new agent:
```bash
./bin/cbw-capture agent my_first_agent
```

This creates:
- `agents/specs/my_first_agent.agent.yaml` - Agent definition
- `agents/evals/my_first_agent/golden_test.yaml` - Test suite

Edit the spec file to customize your agent:
```yaml
# agents/specs/my_first_agent.agent.yaml
name: my_first_agent
description: "My custom agent for [purpose]"
version: "1.0.0"
system_prompt: |
  You are a helpful agent that [does X].
  
tools:
  - name: some_tool
    description: "Tool description"

runtime:
  framework: local
  model: gpt-4
```

### Validate Your Agent

```bash
./bin/cbw-agent validate agents/specs/my_first_agent.agent.yaml
```

### Test Your Agent

```bash
./bin/cbw-agent run agents/specs/my_first_agent.agent.yaml \
  --input "test input" \
  --runtime local
```

### Explore Available Agents

List all agents in the registry:
```bash
cat registry/agents.json | jq '.agents[] | {name, description}'
```

Browse agent specs:
```bash
ls -la agents/specs/
```

### Explore Available Tools

List all tools:
```bash
cat registry/tools.json | jq '.tools[] | {name, description}'
```

Browse tool implementations:
```bash
ls -la agents/tools/
```

## Common Workflows

### Development Cycle

```bash
# 1. Make changes to agent specs or code
# 2. Validate changes
make validate

# 3. Run tests
make test

# 4. Lint and format
make lint fmt

# 5. Compile
make compile

# 6. Run evaluations
make eval
```

### Full Verification

Run all quality checks:
```bash
make doctor index validate compile eval test lint
```

## Optional: Enable Observability

Start the observability stack (Prometheus, Grafana, Jaeger):
```bash
docker compose -f docker/compose/observability/docker-compose.yml up -d
```

Access dashboards:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Jaeger**: http://localhost:16686

Stop the observability stack:
```bash
docker compose -f docker/compose/observability/docker-compose.yml down
```

## Troubleshooting

### Bootstrap fails with Python version error

Ensure you have Python 3.10+:
```bash
python --version
# If too old, install Python 3.10+ and try again
```

### CLI commands not found

Activate the virtual environment:
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Agent validation fails

Check your YAML syntax:
```bash
yamllint agents/specs/my_agent.agent.yaml
```

Review error messages for schema violations.

### Import errors when running agents

Reinstall dependencies:
```bash
pip install -e .
```

## Learn More

- **Full Documentation**: See [docs/](../docs/) directory
- **Agent Development**: [kb/runbooks/adding_new_agent.md](../kb/runbooks/adding_new_agent.md)
- **Daily Operations**: [kb/runbooks/using_the_repo.md](../kb/runbooks/using_the_repo.md)
- **Architecture**: [kb/decisions/](../kb/decisions/)

## Getting Help

- Check the [README.md](../README.md) for comprehensive documentation
- Review examples in `agents/specs/examples/`
- Read the knowledge base in `kb/`
- Report issues via GitHub Issues

---

**Congratulations!** You now have a fully operational CloudCurio agent development environment.
