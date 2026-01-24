# Upgrading CloudCurio Monorepo

Comprehensive guide for upgrading from older versions (v1–v3) to FINAL (v4).

## Table of Contents

- [Overview](#overview)
- [Pre-Upgrade Checklist](#pre-upgrade-checklist)
- [Automated Upgrade](#automated-upgrade)
- [Manual Upgrade](#manual-upgrade)
- [Version-Specific Migration](#version-specific-migration)
- [Post-Upgrade Verification](#post-upgrade-verification)
- [Rollback Procedure](#rollback-procedure)
- [Breaking Changes](#breaking-changes)

## Overview

Manual merges between versions are error-prone and time-consuming. The CloudCurio upgrade script automates the process safely.

### What Changed in v4 (FINAL)

**Major Improvements:**
- ✅ **Repo Hardening**: CI/CD pipelines, pre-commit hooks, stronger validation
- ✅ **Agent Spec v1**: Formal schema with YAML→JSON compilation
- ✅ **Golden Eval Harness**: Automated test suite runner
- ✅ **Runtime Adapters**: Stable interfaces for local, langchain, pydanticai, crewai
- ✅ **Observability**: OpenTelemetry integration, health monitoring
- ✅ **Enhanced CLI**: New commands (cbw-doctor, cbw-index, cbw-capture)
- ✅ **Tool Ecosystem**: Expanded tool library with 45+ tools
- ✅ **Documentation**: Comprehensive KB, runbooks, ADRs

### Upgrade Safety

The upgrade process:
- ✅ **Creates automatic backups** before any changes
- ✅ **Preserves all custom content** (agents, workflows, configs)
- ✅ **Overlays framework files** without deleting your work
- ✅ **Validates** the upgrade with health checks
- ✅ **Supports rollback** if issues occur

## Pre-Upgrade Checklist

Before upgrading, complete these steps:

### 1. Verify Current Version

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo

# Check if pyproject.toml exists
cat pyproject.toml | grep version

# Or check git tags
git describe --tags
```

### 2. Commit All Changes

Ensure your working directory is clean:

```bash
git status

# If you have uncommitted changes
git add .
git commit -m "Pre-upgrade checkpoint"
```

### 3. Document Custom Modifications

List any custom files or modifications:

```bash
# List custom agent specs
ls -la agents/specs/custom/

# List custom tools
ls -la agents/tools/custom/

# List configuration changes
git diff origin/main configs/
```

Save this list for post-upgrade verification.

### 4. Export Environment Variables

```bash
# Backup your .env file
cp .env .env.backup

# Or export to file
env | grep -E "(OPENAI|ANTHROPIC|OTEL|MCP)" > env-backup.txt
```

### 5. Verify System Requirements

```bash
python --version   # Must be 3.10+
node --version     # Must be v18+
git --version      # Must be 2.30+
docker --version   # Optional but recommended
```

### 6. Test Current Installation

Run full test suite on current version:

```bash
make test
make validate
make eval
```

Document any failing tests (you'll verify these post-upgrade).

## Automated Upgrade

### Step 1: Download FINAL Package

```bash
cd ~/Documents/cloudcurio_monorepo
# Download cloudcurio-monorepo-FINAL.zip
unzip cloudcurio-monorepo-FINAL.zip -d ./FINAL
```

### Step 2: Run Upgrade Script (Dry Run)

Preview what will change without applying:

```bash
cd FINAL/cloudcurio-monorepo

bash ./scripts/upgrade_existing_repo.sh \
  --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo \
  --backup-dir ~/Documents/cloudcurio_monorepo/backups \
  --dry-run
```

**Review the output:**
- Files to be overlaid
- Files to be preserved
- Backup location
- Verification steps

### Step 3: Run Upgrade Script (Apply)

Apply the upgrade with automatic backup:

```bash
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo \
  --backup-dir ~/Documents/cloudcurio_monorepo/backups \
  --apply
```

**Expected output:**
```
CloudCurio Monorepo Upgrade
===========================
Old repo: ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
Backup dir: ~/Documents/cloudcurio_monorepo/backups

✓ Old repository verified
✓ Creating backup: backup-20260115-143022.zip
✓ Backup created successfully
✓ Overlaying framework directories...
  ✓ bin/
  ✓ src/
  ✓ agents/
  ✓ workflows/
  ✓ kb/
  ✓ docker/
  ✓ shell/
  ✓ scripts/
  ✓ prompts/
  ✓ tests/
  ✓ .github/
✓ Overlaying root files...
  ✓ Makefile
  ✓ pyproject.toml
  ✓ .pre-commit-config.yaml
  ✓ .editorconfig
✓ Preserving custom files...
✓ Upgrade complete!

Next steps:
  cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
  ./scripts/bootstrap.sh
  make doctor index validate compile eval
```

Next steps:
  cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
  ./scripts/bootstrap.sh
  make doctor index validate compile eval
```

### Script Behavior Details

**What the script does:**

1. **Verifies** the old repository path exists and is valid
2. **Creates** timestamped backup zip in specified backup directory
3. **Overlays** framework directories (preserves custom content):
   - `bin/` - CLI executables
   - `src/` - Python package source
   - `agents/` - Framework agents (preserves custom agents)
   - `workflows/` - Framework workflows (preserves custom workflows)
   - `kb/` - Knowledge base
   - `docker/` - Docker compose stacks
   - `shell/` - Shell library
   - `scripts/` - Utility scripts
   - `prompts/` - System prompts
   - `tests/` - Test suite
   - `.github/` - CI/CD workflows
4. **Overlays** key root files:
   - `Makefile` - Build targets
   - `pyproject.toml` - Package metadata
   - `.pre-commit-config.yaml` - Code quality hooks
   - `.editorconfig` - Editor settings
5. **Does NOT delete** your custom files, configurations, or data
6. **Optionally** runs bootstrap and verification

**Script options:**

```bash
--old PATH              # Path to existing repository (required)
--backup-dir PATH       # Backup directory (required)
--apply                 # Apply changes (vs. dry-run)
--dry-run               # Preview without applying
--no-verify             # Skip post-upgrade verification
--help                  # Show usage
```

## Manual Upgrade

For advanced users who want full control:

### Step 1: Create Manual Backup

```bash
cd ~/Documents/cloudcurio_monorepo
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz cloudcurio-monorepo/
mv backup-*.tar.gz backups/
```

### Step 2: Extract FINAL Package

```bash
unzip cloudcurio-monorepo-FINAL.zip -d FINAL/
```

### Step 3: Compare Directory Structures

```bash
# See what changed
diff -r cloudcurio-monorepo/ FINAL/cloudcurio-monorepo/ --brief

# Or use a visual diff tool
meld cloudcurio-monorepo/ FINAL/cloudcurio-monorepo/
```

### Step 4: Overlay Framework Files

```bash
cd FINAL/cloudcurio-monorepo

# Overlay directories
cp -r bin/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/bin/
cp -r src/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/src/
cp -r docker/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/docker/
cp -r shell/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/shell/
cp -r scripts/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/scripts/
cp -r tests/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/tests/

# Overlay framework agents (be careful not to overwrite custom ones)
cp -r agents/library/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/agents/library/
cp -r agents/orchestrator/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/agents/orchestrator/
cp -r agents/tools/* ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/agents/tools/

# Overlay root files
cp Makefile ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/
cp pyproject.toml ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/
cp .pre-commit-config.yaml ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/
cp .editorconfig ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo/
```

### Step 5: Merge Configuration Changes

Review and merge configuration differences:

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo

# Compare pyproject.toml
diff pyproject.toml ../FINAL/cloudcurio-monorepo/pyproject.toml

# Update dependencies, version, etc.
nano pyproject.toml
```

### Step 6: Update Git Configuration

```bash
# Update .gitignore if needed
cat ../FINAL/cloudcurio-monorepo/.gitignore >> .gitignore

# Update GitHub workflows
cp -r ../FINAL/cloudcurio-monorepo/.github/ .github/
```

## Version-Specific Migration

### From v1 to v4

**Breaking changes:**
- Agent spec format changed from loose YAML to formal schema
- CLI commands restructured (old `cbw` → new `cbw-agent`, `cbw-workflow`)
- Runtime interface changed (requires adapter implementation)

**Migration steps:**

1. **Update agent specs to v1 format:**
   ```yaml
   # Old format (v1)
   agent:
     name: my_agent
     tools: [tool1, tool2]
   
   # New format (v4)
   name: my_agent
   version: "1.0.0"
   description: "Agent description"
   system_prompt: |
     System instructions...
   tools:
     - name: tool1
       description: "Tool 1 description"
     - name: tool2
       description: "Tool 2 description"
   runtime:
     framework: local
   ```

2. **Update CLI usage:**
   ```bash
   # Old
   ./bin/cbw run my_agent.yaml
   
   # New
   ./bin/cbw-agent run my_agent.yaml --runtime local
   ```

3. **Add golden tests:**
   ```yaml
   # Create agents/evals/my_agent/golden_test.yaml
   tests:
     - name: "basic_test"
       input: "test input"
       expected_output: "expected output"
   ```

### From v2 to v4

**Changes:**
- Tool interface standardized with BaseTool class
- Workflow format updated to support multi-step orchestration
- Observability integration added

**Migration steps:**

1. **Update custom tools:**
   ```python
   # Old (v2)
   def my_tool(input):
       return result
   
   # New (v4)
   from cbw_foundry.tools import BaseTool
   
   class MyTool(BaseTool):
       name = "my_tool"
       description = "Description"
       
       def execute(self, **kwargs):
           return result
   ```

2. **Update workflows:**
   ```yaml
   # Add version and metadata
   version: "1.0.0"
   name: my_workflow
   description: "Workflow description"
   
   steps:
     - name: step1
       agent: agent1
       input: "data"
   ```

### From v3 to v4

**Changes:**
- Pre-commit hooks added
- Registry system introduced
- Enhanced CLI with cbw-doctor, cbw-index

**Migration steps:**

1. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Generate registries:**
   ```bash
   make index
   ```

3. **Update to new CLI commands:**
   - Use `cbw-doctor` instead of manual health checks
   - Use `cbw-index` for registry updates

## Post-Upgrade Verification

### Step 1: Re-Bootstrap Environment

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
```

This will:
- Recreate virtual environment with new dependencies
- Install updated pre-commit hooks
- Verify CLI tools

### Step 2: Run Health Check

```bash
make doctor
```

**Verify all checks pass:**
- ✓ Python environment
- ✓ Dependencies
- ✓ CLI tools
- ✓ Directory structure
- ✓ Agent specs
- ✓ Registry

### Step 3: Update Registry

```bash
make index
```

Regenerates agent, tool, and workflow registries.

### Step 4: Validate All Specs

```bash
make validate
```

**If validation fails:**
- Review error messages for schema violations
- Update specs to v1 format (see version migration above)
- Check YAML syntax with `yamllint`

### Step 5: Compile Agents

```bash
make compile
```

Generates JSON artifacts for all agents.

### Step 6: Run Evaluations

```bash
make eval
```

**Compare results with pre-upgrade:**
- Same tests should pass/fail
- New tests may be added by framework

### Step 7: Run Test Suite

```bash
make test
```

All tests should pass. If not:
- Check for custom test modifications
- Review test output for specific failures
- Update tests for new framework interfaces

### Step 8: Verify Custom Content

```bash
# Check custom agents
ls -la agents/specs/custom/
./bin/cbw-agent validate agents/specs/custom/*.agent.yaml

# Check custom tools
ls -la agents/tools/custom/

# Check custom workflows
ls -la workflows/custom/
```

### Step 9: Test Agent Execution

```bash
# Test framework agent
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml \
  --input "hello" --runtime local

# Test your custom agent
./bin/cbw-agent run agents/specs/custom/my_agent.agent.yaml \
  --input "test" --runtime local
```

### Step 10: Verify Integrations

**MCP Servers:**
```bash
cd mcp-servers/automation
npm install
npm start
```

**Observability Stack:**
```bash
docker compose -f docker/compose/observability/docker-compose.yml up -d
# Check: http://localhost:9090 (Prometheus)
# Check: http://localhost:3000 (Grafana)
# Check: http://localhost:16686 (Jaeger)
```

## Rollback Procedure

If the upgrade fails or causes issues, rollback to the backup:

### Automatic Rollback

```bash
cd ~/Documents/cloudcurio_monorepo

# Remove upgraded repo
rm -rf cloudcurio-monorepo

# Extract backup
unzip backups/backup-TIMESTAMP.zip -d .

# Verify rollback
cd cloudcurio-monorepo
make doctor
```

### Verify Rollback

```bash
# Check version
cat pyproject.toml | grep version

# Run tests
make test validate
```

## Breaking Changes

### v4 Breaking Changes from v3

1. **Agent Spec Format**
   - **Old:** Loose YAML with minimal schema
   - **New:** Formal schema with required fields (version, description, system_prompt)
   - **Action:** Update all agent specs to include required fields

2. **CLI Commands**
   - **Old:** `./bin/cbw run agent.yaml`
   - **New:** `./bin/cbw-agent run agent.yaml --runtime local`
   - **Action:** Update scripts and documentation

3. **Tool Interface**
   - **Old:** Function-based tools
   - **New:** Class-based tools inheriting from BaseTool
   - **Action:** Wrap custom tools in BaseTool classes

4. **Runtime Adapters**
   - **Old:** Direct framework imports
   - **New:** Runtime adapter interface
   - **Action:** Use `--runtime` flag, implement adapters for custom frameworks

5. **Environment Variables**
   - **New:** OTEL_ENABLED, OTEL_ENDPOINT, MCP_*_ENABLED
   - **Action:** Update .env with new variables

6. **Registry System**
   - **New:** Auto-generated indexes required
   - **Action:** Run `make index` after changes

## Troubleshooting Upgrades

### Upgrade script fails

**Check permissions:**
```bash
chmod +x ./scripts/upgrade_existing_repo.sh
```

**Check paths:**
```bash
# Ensure old repo path is correct
ls ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo

# Ensure backup dir exists
mkdir -p ~/Documents/cloudcurio_monorepo/backups
```

### Bootstrap fails after upgrade

**Clean and retry:**
```bash
rm -rf .venv
./scripts/bootstrap.sh
```

**Check Python version:**
```bash
python --version  # Must be 3.10+
```

### Validation fails after upgrade

**Update agent specs:**
```bash
# Check specific errors
./bin/cbw-agent validate agents/specs/my_agent.agent.yaml --verbose

# Common fixes:
# - Add version: "1.0.0"
# - Add description field
# - Update tool format from list to objects
```

### Tests fail after upgrade

**Reinstall dependencies:**
```bash
pip install -e .
make test
```

**Update test imports:**
```python
# Old
from cbw import Agent

# New  
from cbw_foundry.spec.models import AgentSpec
```

### Custom tools broken

**Wrap in BaseTool:**
```python
from cbw_foundry.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Description"
    
    def execute(self, **kwargs):
        # Your existing tool code
        return result
```

## Best Practices

1. **Always use dry-run first** to preview changes
2. **Keep multiple backups** from different timestamps
3. **Test thoroughly** after upgrade before production use
4. **Document custom changes** for future upgrades
5. **Update incrementally** rather than skipping versions
6. **Review changelog** for breaking changes
7. **Verify integrations** (APIs, databases, services) post-upgrade

## Support

For upgrade issues:
- Review this guide thoroughly
- Check [docs/INSTALL.md](INSTALL.md) troubleshooting section
- Review backup files for comparison
- Open GitHub Issue with:
  - Source version
  - Target version
  - Upgrade method (automated/manual)
  - Error output
  - Backup timestamp (for potential recovery)

---

After upgrade run:

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
make doctor index validate compile eval
```
