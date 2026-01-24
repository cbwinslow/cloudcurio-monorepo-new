# CloudCurio Monorepo — Installation Guide

This guide provides comprehensive installation instructions for CloudCurio Monorepo, covering fresh installations, upgrades, and various deployment scenarios.

## Table of Contents

- [System Requirements](#system-requirements)
- [Fresh Installation](#fresh-installation)
- [Verification Steps](#verification-steps)
- [Configuration](#configuration)
- [Optional Components](#optional-components)
- [Upgrading from Older Versions](#upgrading-from-older-versions)
- [Troubleshooting](#troubleshooting)
- [Platform-Specific Notes](#platform-specific-notes)

## System Requirements

### Minimum Requirements

- **Operating System**: 
  - Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
  - macOS 11+ (Big Sur or later)
  - Windows 10/11 with WSL2 (recommended) or native
  
- **Python**: Version 3.10 or higher
  - Check: `python --version` or `python3 --version`
  - With pip and venv modules
  
- **Node.js**: Version 18 or higher (for MCP servers)
  - Check: `node --version`
  - With npm package manager
  
- **Git**: Version 2.30 or higher
  - Check: `git --version`
  
- **Disk Space**: Minimum 500MB free space
  - ~200MB for dependencies
  - ~100MB for virtual environment
  - ~200MB for working data

### Optional Requirements

- **Docker**: Version 20.10+ (for observability stack)
  - Docker Compose v2.0+
  
- **Database**: PostgreSQL 14+ or MySQL 8+ (for certain agents)

## Fresh Installation (Recommended)

This is a **single, ready-to-use** monorepo snapshot that can be used fresh without merging anything.

### Step 1: Prepare Installation Directory

```bash
cd ~/Documents
mkdir -p cloudcurio_monorepo
cd cloudcurio_monorepo
```

### Step 2: Extract or Clone Repository

**Option A: From ZIP Distribution**
```bash
# Unzip this package so you end up with:
# ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
unzip cloudcurio-monorepo-FINAL.zip -d .
cd cloudcurio-monorepo
```

**Option B: From Git Repository**
```bash
git clone <repository-url> cloudcurio-monorepo
cd cloudcurio-monorepo
```

Your directory structure should now be:
```
~/Documents/cloudcurio_monorepo/
└── cloudcurio-monorepo/
    ├── agents/
    ├── bin/
    ├── docs/
    ├── src/
    ├── Makefile
    ├── pyproject.toml
    └── ... (other files)
```

### Step 3: Run Bootstrap Script

The bootstrap script automates environment setup:

```bash
./scripts/bootstrap.sh
```

**What the bootstrap script does:**

1. **Checks system requirements** (Python, Git versions)
2. **Creates Python virtual environment** in `.venv/`
3. **Installs Python dependencies** from `pyproject.toml`:
   - Core framework (cbw_foundry)
   - Agent libraries (crewai, pydantic, etc.)
   - Development tools (pytest, ruff, mypy)
   - Observability (opentelemetry)
4. **Installs Node.js dependencies** for MCP servers
5. **Installs pre-commit hooks** for code quality
6. **Verifies CLI tools** are accessible
7. **Runs initial health check**

**Expected output:**
```
CloudCurio Monorepo Bootstrap
=============================
✓ Python 3.10+ detected
✓ Git 2.30+ detected
✓ Node.js 18+ detected
✓ Creating virtual environment...
✓ Installing Python dependencies...
✓ Installing pre-commit hooks...
✓ Verifying installation...
✓ Bootstrap complete!

Next steps:
  make doctor    # Verify installation
  make index     # Generate registries
```

**Troubleshooting Bootstrap:**

- If Python version is too old: Install Python 3.10+ and retry
- If pip fails: Try `pip install --upgrade pip` first
- If permission errors: Don't use sudo; ensure directory is writable
- If pre-commit fails: Install with `pip install pre-commit`

## Verification Steps

### Step 1: Health Check

```bash
make doctor
```

This comprehensive health check validates:

- ✅ **Python Environment**: Virtual environment active, correct version
- ✅ **Dependencies**: All required packages installed
- ✅ **CLI Tools**: bin/cbw-* executables work
- ✅ **Directory Structure**: All expected directories present
- ✅ **Agent Specs**: YAML files valid
- ✅ **Registry**: Index files current
- ✅ **Git Configuration**: Repository status healthy

**Expected output:**
```
CloudCurio Doctor - Health Check
=================================
✓ Python environment: OK (3.10.x)
✓ Virtual environment: Active
✓ Dependencies: All installed
✓ CLI tools: All accessible
✓ Directory structure: OK
✓ Agent specs: Valid
✓ Registry: Up to date
✓ Git status: Clean

All systems operational ✓
```

### Step 2: Generate Registry Indexes

```bash
make index
```

This generates three key registry files:

- `registry/agents.json` - Catalog of all agent specifications
- `registry/tools.json` - Catalog of all available tools  
- `registry/workflows.json` - Catalog of workflow definitions

**Expected output:**
```
Generating registry indexes...
✓ Scanned agents/specs/: 12 agents found
✓ Scanned agents/tools/: 45 tools found
✓ Scanned workflows/: 3 workflows found
✓ Generated registry/agents.json
✓ Generated registry/tools.json
✓ Generated registry/workflows.json
```

### Step 3: Validate Agent Specifications

```bash
make validate
```

Validates all YAML agent specs against the schema:

**Expected output:**
```
Validating agent specifications...
✓ agents/specs/examples/hello_world.agent.yaml
✓ agents/specs/examples/research_agent.agent.yaml
✓ agents/specs/custom/my_agent.agent.yaml
...
✓ All 12 agent specs valid
```

### Step 4: Compile Agents

```bash
make compile
```

Compiles YAML specs to optimized JSON artifacts:

**Expected output:**
```
Compiling agents to JSON...
✓ hello_world.agent.yaml → dist/agents/hello_world.agent.json
✓ research_agent.agent.yaml → dist/agents/research_agent.agent.json
...
✓ Compiled 12 agents
```

### Step 5: Run Golden Evaluations

```bash
make eval
```

Executes test suites to verify agent behavior:

**Expected output:**
```
Running golden evaluations...
✓ hello_world: 5/5 tests passed
✓ research_agent: 8/8 tests passed
...
✓ All evaluations passed (total: 45/45)
```

### Step 6: Test the Example Agent

```bash
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local
```

**Expected output:**
```
CloudCurio Agent Runner
=======================
Agent: hello_world
Runtime: local
Input: hello
---
Processing...
Response: Hello! I'm the hello_world agent. You said: hello
---
✓ Execution completed successfully
```

## Configuration

### Environment Variables

Create `.env` file in the repository root:

```bash
# Copy example configuration
cp configs/global/env.example .env

# Edit with your settings
nano .env
```

**Key environment variables:**

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...                    # OpenAI API key (optional)
ANTHROPIC_API_KEY=sk-...                 # Anthropic API key (optional)

# Runtime Settings
DEFAULT_RUNTIME=local                    # local, langchain, crewai
DEFAULT_MODEL=gpt-4                      # Model to use

# Observability
OTEL_ENABLED=false                       # Enable OpenTelemetry
OTEL_ENDPOINT=http://localhost:4317      # OTLP endpoint

# Logging
LOG_LEVEL=INFO                           # DEBUG, INFO, WARN, ERROR
LOG_FORMAT=json                          # json or text

# MCP Servers
MCP_AUTOMATION_ENABLED=true              # Enable automation MCP server
MCP_MEDIA_ENABLED=true                   # Enable media MCP server

# Agent Configuration  
AGENT_TIMEOUT=300                        # Agent execution timeout (seconds)
MAX_ITERATIONS=10                        # Max agent reasoning iterations
```

### Global Configuration Files

Edit `configs/global/config.yaml` for system-wide settings:

```yaml
# Framework settings
runtime:
  default: local
  adapters:
    - local
    - langchain
    - crewai
    - pydanticai

# Agent defaults
agents:
  timeout: 300
  max_iterations: 10
  default_model: gpt-4

# Tool settings
tools:
  timeout: 60
  retry_attempts: 3
```

## Optional Components

### Observability Stack (Docker)

Start Prometheus, Grafana, and Jaeger for monitoring:

```bash
docker compose -f docker/compose/observability/docker-compose.yml up -d
```

**Services started:**
- **Prometheus**: http://localhost:9090 (metrics)
- **Grafana**: http://localhost:3000 (dashboards, admin/admin)
- **Jaeger**: http://localhost:16686 (distributed tracing)

**Enable in your .env:**
```bash
OTEL_ENABLED=true
OTEL_ENDPOINT=http://localhost:4317
```

**Stop the stack:**
```bash
docker compose -f docker/compose/observability/docker-compose.yml down
```

### MCP Servers

MCP (Model Context Protocol) servers provide tool integration.

**Start automation server:**
```bash
cd mcp-servers/automation
npm install
npm start
```

**Start media server:**
```bash
cd mcp-servers/media  
pip install -r requirements.txt
python server.py
```

**Configure in .env:**
```bash
MCP_AUTOMATION_ENABLED=true
MCP_MEDIA_ENABLED=true
MCP_AUTOMATION_URL=http://localhost:3000
MCP_MEDIA_URL=http://localhost:3001
```

## Upgrading from Older Versions

If you already have an older repo (v1–v3), use the upgrade script from this FINAL repo.

### Automated Upgrade Process

```bash
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo \
  --backup-dir ~/Documents/cloudcurio_monorepo/backups \
  --apply
```

**What this does:**

1. ✅ **Verifies** old repository path exists
2. ✅ **Creates** timestamped backup zip in backup-dir
3. ✅ **Overlays** new framework files and directories:
   - `bin/`, `src/`, `agents/`, `workflows/`, `kb/`
   - `docker/`, `shell/`, `scripts/`, `prompts/`, `tests/`
   - Root files: `Makefile`, `pyproject.toml`, `.github/`
4. ✅ **Preserves** your custom files and data
5. ✅ **Does not delete** any of your existing work
6. ✅ **Optionally** runs verification steps

**Upgrade options:**

```bash
# Dry run (preview changes without applying)
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/path/to/old/repo \
  --backup-dir ~/backups \
  --dry-run

# Apply without verification
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/path/to/old/repo \
  --backup-dir ~/backups \
  --apply \
  --no-verify

# Apply with full verification
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/path/to/old/repo \
  --backup-dir ~/backups \
  --apply
```

### Post-Upgrade Steps

After successful upgrade, re-bootstrap and verify:

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
make doctor index validate compile eval
```

### Manual Upgrade (Advanced)

If you prefer manual control:

1. **Backup your repository:**
   ```bash
   cd ~/Documents/cloudcurio_monorepo
   tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz cloudcurio-monorepo/
   ```

2. **Overlay new framework files:**
   ```bash
   cp -r cloudcurio-monorepo-FINAL/bin/* cloudcurio-monorepo/bin/
   cp -r cloudcurio-monorepo-FINAL/src/* cloudcurio-monorepo/src/
   cp cloudcurio-monorepo-FINAL/Makefile cloudcurio-monorepo/
   cp cloudcurio-monorepo-FINAL/pyproject.toml cloudcurio-monorepo/
   # ... repeat for other directories
   ```

3. **Merge configuration changes:**
   - Review diff of `pyproject.toml`
   - Update `Makefile` targets
   - Check `.github/` workflows

4. **Re-bootstrap:**
   ```bash
   cd cloudcurio-monorepo
   ./scripts/bootstrap.sh
   ```

## Troubleshooting

### Common Issues

#### 1. Bootstrap fails with "Python version too old"

**Problem:** Python version is below 3.10

**Solution:**
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-pip

# On macOS with Homebrew
brew install python@3.10

# Verify
python3.10 --version
```

Update bootstrap to use correct Python:
```bash
python3.10 -m venv .venv
```

#### 2. "Command not found: cbw-agent"

**Problem:** Virtual environment not activated or CLI not installed

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Reinstall package
pip install -e .

# Verify
which cbw-agent
cbw-agent --help
```

#### 3. Agent validation fails

**Problem:** YAML syntax errors or schema violations

**Solution:**
```bash
# Check YAML syntax
yamllint agents/specs/my_agent.agent.yaml

# View detailed validation errors
./bin/cbw-agent validate agents/specs/my_agent.agent.yaml --verbose

# Common issues:
# - Incorrect indentation (use 2 spaces)
# - Missing required fields (name, description, version)
# - Invalid tool references
```

#### 4. Import errors when running tests

**Problem:** Package not installed in editable mode

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Or use development install
pip install -e ".[dev]"
```

#### 5. Docker observability stack fails to start

**Problem:** Port conflicts or Docker not running

**Solution:**
```bash
# Check Docker is running
docker ps

# Check port availability
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana
lsof -i :16686 # Jaeger

# Stop conflicting services or modify docker-compose.yml ports
docker compose -f docker/compose/observability/docker-compose.yml down
# Edit docker-compose.yml to change ports if needed
docker compose -f docker/compose/observability/docker-compose.yml up -d
```

#### 6. Pre-commit hooks fail

**Problem:** Code quality issues or hooks not installed

**Solution:**
```bash
# Install/reinstall hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

#### 7. Make commands fail

**Problem:** Make not installed or Makefile issues

**Solution:**
```bash
# Install make on Ubuntu/Debian
sudo apt install build-essential

# Install make on macOS
xcode-select --install

# Or run commands directly
python -m cbw_foundry.doctor_cli
python -m cbw_foundry.agent_cli validate agents/specs/**/*.agent.yaml
```

## Platform-Specific Notes

### macOS

**Apple Silicon (M1/M2/M3):**
- Use Python from Homebrew: `brew install python@3.10`
- Some dependencies may need ARM builds
- Docker Desktop for Mac includes Rosetta 2 emulation

**Intel Macs:**
- Standard installation works without modifications

### Linux

**Ubuntu/Debian:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-pip
sudo apt install nodejs npm
sudo apt install git make
```

**RHEL/CentOS/Fedora:**
```bash
# Install dependencies
sudo dnf install python3.10 python3-pip
sudo dnf install nodejs npm
sudo dnf install git make
```

### Windows

**WSL2 (Recommended):**
- Install WSL2 with Ubuntu
- Follow Linux installation steps inside WSL2

**Native Windows:**
- Install Python from python.org
- Install Node.js from nodejs.org
- Install Git from git-scm.com
- Use PowerShell or Git Bash
- Some shell scripts may need adaptation

### Cloud Platforms

**AWS EC2:**
- Use Ubuntu 22.04 or Amazon Linux 2023
- Ensure adequate instance size (t3.medium minimum)
- Open security group ports if using observability stack

**Google Cloud VM:**
- Use Ubuntu 22.04 image
- Enable HTTP/HTTPS if exposing services

**Azure VM:**
- Use Ubuntu 22.04 image
- Configure NSG rules for service ports

## Next Steps

After successful installation:

1. **Read the Quickstart**: [docs/QUICKSTART.md](QUICKSTART.md)
2. **Explore the Knowledge Base**: [kb/](../kb/)
3. **Try Example Agents**: `agents/specs/examples/`
4. **Create Your First Agent**: `./bin/cbw-capture agent my_agent`
5. **Join the Community**: Check GitHub Issues and Discussions

## Support

For installation issues:
- Check this troubleshooting section
- Review [kb/runbooks/using_the_repo.md](../kb/runbooks/using_the_repo.md)
- Open a GitHub Issue with:
  - Operating system and version
  - Python/Node.js versions
  - Full error output
  - Steps to reproduce

---

**Installation complete!** Proceed to [QUICKSTART.md](QUICKSTART.md) to start using the system.
