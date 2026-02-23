# CloudCurio Monorepo - AI Agent Task List

**Version:** 1.1.0  
**Created:** 2026-02-13  
**Updated:** 2026-02-23  
**Purpose:** Comprehensive task list for AI agents to implement improvements and features  
**Repository:** cloudcurio-monorepo-new

---

## 📋 Overview

This document provides a structured, detailed task list that AI agents can follow to complete various improvements, features, and maintenance tasks for the CloudCurio Monorepo. Each task includes:
- **Description**: What needs to be done
- **Reasoning**: Why this task is important
- **Prerequisites**: Dependencies and requirements
- **Implementation Steps**: Detailed step-by-step instructions
- **Validation**: How to verify completion
- **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

---

## ✅ Completed Work (Phase 1 – Inventory & Search)

**PR: "Remote Inventory Management System – Phase 1"**  
**Status:** ✅ Merged

### What was built

| Component | File | Description |
|-----------|------|-------------|
| Inventory module | `src/cbw_foundry/inventory.py` | Scans all asset types (agents, tools, skills, workflows, MCP servers, scripts, templates), extracts metadata, supports search and persistence |
| Search CLI | `src/cbw_foundry/search_cli.py` | `cbw-search` with `index`, `list`, `query`, `info`, `types`, `summary` subcommands |
| Shell wrapper | `bin/cbw-search` | Bash wrapper delegating to the Python CLI |
| Shell library | `shell/lib/inventory.sh` | Sourceable shell enhancement with fzf integration, colored output, and helper functions (`cbw-ls`, `cbw-find`, `cbw-show`, `cbw-pick`, `cbw-run-agent`, etc.) |
| Rich index | `registry/index.json` | JSON index with full metadata for all 35+ assets |
| Enhanced indexer | `src/cbw_foundry/index_cli.py` | Also produces `registry/index.json` alongside legacy YAML files |
| Tests | `tests/python/test_inventory.py` | 26 passing unit + integration tests |

### How to use it

```bash
# Source the shell library in your .bashrc / .zshrc:
source "$CBW_MONO/shell/init/bash.sh"

# Rebuild the index after adding new assets:
cbw-rebuild-index          # or: cbw index

# List all assets:
cbw-ls                     # all types
cbw-ls agent               # agents only

# Search:
cbw-find "transcription"
cbw-find "web" skill

# Interactive fuzzy picker (requires fzf):
cbw-pick
cbw-pick agent

# Get details:
cbw-show researcher

# Run an agent by name:
cbw-run-agent researcher --input "AI trends 2025" --runtime local

# JSON output for scripting:
cbw-search query "video" --format json | jq '.[].path'
cbw-search list --type tool --format plain
```

---

## 🎯 Task Categories

1. [Remote Management System – Phase 2](#remote-management-system--phase-2)
2. [Runtime Adapters](#runtime-adapters)
3. [Agent Development](#agent-development)
4. [Tool Development](#tool-development)
5. [MCP Server Enhancements](#mcp-server-enhancements)
6. [Testing & Quality](#testing--quality)
7. [Documentation](#documentation)
8. [Infrastructure & DevOps](#infrastructure--devops)
9. [Performance & Optimization](#performance--optimization)
10. [Security](#security)

---

## Remote Management System – Phase 2

> **Context:** Phase 1 built the inventory + search layer. Phase 2 adds the
> download / install / run / update layer so users can manage assets remotely
> with a single command.

### TASK-RMS-002: Download & Install Assets from a Remote Registry
**Priority:** P0 (Critical)  
**Status:** ❌ Not Started  
**Estimated Effort:** 4-6 days  
**Depends on:** Phase 1 (completed)

**Description:**  
Build a `cbw install` / `cbw download` command that lets users pull individual
assets (agents, tools, skills, scripts, MCP servers) from a remote source
(GitHub release, raw URL, or a manifest file) into the local repo and
automatically register them in the index.

**Architecture Overview:**

```
Remote Source                 Local Repo
─────────────────────         ──────────────────────────────────────
GitHub Release          ──►   agents/specs/<name>.agent.yaml
Raw YAML/JSON URL       ──►   skills/<name>.skill.yaml
cbw-manifest.json       ──►   workflows/library/<name>.workflow.yaml
tarball                 ──►   mcp-servers/<name>/
```

**Design:**

1. **Remote Manifest** – A JSON file (hosted e.g. on GitHub Pages or a raw
   GitHub URL) that lists all publishable assets with their download URLs:

   ```json
   // https://raw.githubusercontent.com/cbwinslow/cloudcurio-monorepo-new/main/registry/manifest.json
   {
     "version": "1.0.0",
     "assets": [
       {
         "name": "researcher",
         "type": "agent",
         "version": "1.2.0",
         "url": "https://raw.githubusercontent.com/cbwinslow/cloudcurio-monorepo-new/main/agents/specs/researcher.agent.yaml",
         "sha256": "abc123...",
         "description": "Research agent"
       }
     ]
   }
   ```

2. **Python Module** – `src/cbw_foundry/installer.py`

   ```python
   class AssetInstaller:
       def fetch_manifest(self, url: str) -> dict: ...
       def list_remote(self, asset_type: str | None = None) -> list[dict]: ...
       def download(self, name: str, dest: Path, verify_checksum: bool = True) -> Path: ...
       def install(self, name: str) -> bool: ...
       def update(self, name: str) -> bool: ...
       def remove(self, name: str) -> bool: ...
   ```

3. **CLI extension** – Add subcommands to `cbw-search` or create `bin/cbw-install`:

   ```bash
   cbw-install list                    # List available remote assets
   cbw-install search "transcription"  # Search remote assets
   cbw-install get researcher          # Download + register researcher agent
   cbw-install update researcher       # Pull latest version
   cbw-install remove researcher       # Delete local copy + remove from index
   cbw-install sync                    # Update all installed assets
   ```

4. **Shell functions** – Add to `shell/lib/inventory.sh`:

   ```bash
   cbw-install() { ... }   # install remote asset
   cbw-update()  { ... }   # update one or all assets
   cbw-remove()  { ... }   # remove a local asset
   ```

**Files to Create:**
- `src/cbw_foundry/installer.py` – core installer module
- `src/cbw_foundry/install_cli.py` – CLI entry point
- `bin/cbw-install` – shell wrapper (copy pattern from `bin/cbw-search`)
- `registry/manifest.json` – local copy / template of the remote manifest
- `tests/python/test_installer.py` – unit tests with mocked HTTP calls

**Files to Modify:**
- `pyproject.toml` – add `cbw-install = "cbw_foundry.install_cli:main"` to scripts
- `shell/init/bash.sh` – add `cbw-install()` wrapper function
- `shell/lib/inventory.sh` – add install/update/remove shell functions
- `src/cbw_foundry/cli.py` – add `"install": "cbw-install"` to mapping
- `TASKS.md` – mark this task complete when done

**Implementation Steps:**

1. Create `registry/manifest.json` template (empty assets array, version 1.0.0).

2. Write `src/cbw_foundry/installer.py`:
   - Use `urllib.request` (stdlib only – no new deps) for HTTP GET.
   - Validate SHA-256 checksums before writing.
   - Write assets to the correct directory based on type:
     - `agent` → `agents/specs/<name>.agent.yaml`
     - `skill` → `skills/<name>.skill.yaml`
     - `workflow` → `workflows/library/<name>.workflow.yaml`
     - `tool` → `agents/tools/python/<name>.py`
     - `mcp` → `mcp-servers/<name>/` (tarball extraction)
     - `script` → `scripts/<name>.sh`
   - After writing, call `Inventory.scan()` + `Inventory.save()` to update the index.

3. Write `src/cbw_foundry/install_cli.py` with argparse subcommands.

4. Create `bin/cbw-install` (chmod +x).

5. Write tests using `unittest.mock.patch` to mock `urllib.request.urlopen`.

6. Update shell library with `cbw-install`, `cbw-update`, `cbw-remove` functions.

**Validation:**
```bash
# List remote assets (mocked)
cbw-install list

# Install an asset
cbw-install get researcher

# Verify it was indexed
cbw-search info researcher

# Update
cbw-install update researcher

# Remove
cbw-install remove researcher
```

**Success Criteria:**
- ✅ Can list remote assets from manifest
- ✅ Can download and install an asset
- ✅ Checksum verification works
- ✅ Index updates automatically after install
- ✅ All tests pass with mocked HTTP

---

### TASK-RMS-003: Shell Terminal Enhancement (Starship / fzf Style)
**Priority:** P1 (High)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Description:**  
Enhance the shell environment with a richer prompt, keybindings, and tab
completions so that the CloudCurio tools feel as polished as `fzf` + `starship`.

**What to build:**

1. **`shell/lib/completions.sh`** – Bash/Zsh tab completions for all `cbw-*` commands:
   ```bash
   # Completion: cbw-search query <TAB> → shows index items
   # Completion: cbw-search list --type <TAB> → shows types
   # Completion: cbw-run-agent <TAB> → shows agent names
   ```

2. **`shell/lib/keybindings.sh`** – Optional key bindings:
   ```bash
   # Ctrl+Alt+A → open cbw-pick agent in fzf
   # Ctrl+Alt+S → open cbw-pick skill in fzf
   # Ctrl+Alt+W → open cbw-pick workflow in fzf
   ```

3. **`shell/lib/prompt.sh`** – Optional prompt segment showing active CBW context:
   ```bash
   # Adds " 🤖 cbw" to PS1 when inside the repo dir
   ```

4. **`shell/init/bash.sh`** – Source the new libs.

5. **`shell/init/zsh.sh`** – Zsh-specific completion setup.

**Files to Create:**
- `shell/lib/completions.sh`
- `shell/lib/keybindings.sh`
- `shell/lib/prompt.sh`

**Files to Modify:**
- `shell/init/bash.sh`
- `shell/init/zsh.sh`

---

### TASK-RMS-004: Python API Server for Remote Management
**Priority:** P1 (High)  
**Status:** ❌ Not Started  
**Estimated Effort:** 3-5 days

**Description:**  
Expose the inventory and installer as a lightweight HTTP API (FastAPI) so that
external tools, CI pipelines, and remote machines can query and manage assets
over HTTP without needing a shell.

**Endpoints:**

```
GET  /api/v1/assets              List all assets
GET  /api/v1/assets?type=agent   Filter by type
GET  /api/v1/assets?q=research   Search
GET  /api/v1/assets/{name}       Get single asset details
POST /api/v1/assets/{name}/install  Install asset
POST /api/v1/assets/index        Rebuild the index
GET  /api/v1/health              Health check
```

**Files to Create:**
- `src/cbw_foundry/api/__init__.py`
- `src/cbw_foundry/api/server.py` – FastAPI app
- `src/cbw_foundry/api/routes.py` – route handlers
- `bin/cbw-serve` – shell wrapper to start the server
- `tests/python/test_api_server.py` – tests using FastAPI TestClient
- `docs/API.md` – API documentation

**Files to Modify:**
- `pyproject.toml` – add fastapi + uvicorn to optional deps; add `cbw-serve` script
- `shell/init/bash.sh` – add `cbw-serve()` wrapper

**Implementation:**
```python
# src/cbw_foundry/api/server.py
from fastapi import FastAPI
from cbw_foundry.inventory import Inventory

app = FastAPI(title="CloudCurio Asset API", version="1.0.0")
inv = Inventory()

@app.get("/api/v1/assets")
def list_assets(type: str | None = None, q: str | None = None):
    if q:
        return inv.search(q, item_type=type)
    return inv.list_all(item_type=type)

@app.get("/api/v1/assets/{name}")
def get_asset(name: str):
    item = inv.get(name)
    if not item:
        raise HTTPException(404, detail=f"Asset '{name}' not found")
    return item

@app.post("/api/v1/assets/index")
def rebuild_index():
    items = inv.scan()
    inv.save()
    return {"status": "ok", "total": len(items)}
```

---

### TASK-RMS-005: MCP Server for Inventory Management
**Priority:** P2 (Medium)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Description:**  
Create an MCP server that exposes the inventory as MCP tools so AI assistants
(Claude, Copilot, etc.) can query and manage assets directly in conversation.

**MCP Tools to expose:**
- `list_assets(type?)` – list all or filtered assets
- `search_assets(query, type?)` – search inventory
- `get_asset(name)` – get details for an asset
- `install_asset(name)` – install a remote asset
- `rebuild_index()` – re-scan the repo

**Files to Create:**
- `mcp-servers/inventory/server.py` – MCP server implementation
- `mcp-servers/inventory/requirements.txt`

**Reference:** Look at `mcp-servers/automation/server.py` for implementation pattern.

---

## Runtime Adapters

### TASK-RA-001: Implement Full LangChain Runtime Adapter
**Priority:** P1 (High)  
**Status:** 🔄 In Progress (Stub exists)  
**Estimated Effort:** 3-5 days

**Description:**
Implement complete LangChain runtime adapter to enable running CloudCurio agents with LangChain framework.

**Reasoning:**
- LangChain is industry-standard for LLM applications
- Many users already have LangChain expertise
- Enables integration with LangChain ecosystem (LangSmith, callbacks, memory)
- Expands framework compatibility

**Prerequisites:**
- LangChain installed: `pip install langchain`
- Understanding of LangChain agent patterns
- Access to LLM provider (OpenAI, Anthropic, or local)

**Implementation Steps:**

1. **Study Current Stub**
   ```python
   # File: src/cbw_foundry/runtime/adapters.py
   # Review LangChainRuntime class stub
   ```

2. **Implement Core Methods**
   - `__init__`: Initialize LangChain components
   - `execute`: Convert AgentSpec to LangChain agent and run
   - `_create_llm`: Create LangChain LLM instance
   - `_create_tools`: Convert CloudCurio tools to LangChain tools
   - `_create_agent`: Build LangChain agent with tools

3. **Tool Integration**
   ```python
   def _convert_tool(self, tool_spec: dict) -> LangChainTool:
       """Convert CloudCurio tool to LangChain tool."""
       # Implementation
   ```

4. **Memory Management**
   - Implement conversation history
   - Support persistent memory across runs

5. **Callback System**
   - Add LangSmith integration
   - Support custom callbacks

**Validation:**
```bash
# Test LangChain runtime
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml \
  --runtime langchain \
  --input "test message"

# Should output successful execution result, not stub message
```

**Files to Modify:**
- `src/cbw_foundry/runtime/adapters.py` - Main implementation
- `tests/test_langchain_runtime.py` - Add comprehensive tests
- `docs/RUNTIME_ADAPTERS.md` - Update documentation

**Success Criteria:**
- ✅ Can execute agents with LangChain runtime
- ✅ Tool integration works correctly
- ✅ Memory persists across runs
- ✅ All tests pass
- ✅ Documentation updated

---

### TASK-RA-002: Implement Full CrewAI Runtime Adapter
**Priority:** P1 (High)  
**Status:** 🔄 In Progress (Stub exists)  
**Estimated Effort:** 3-5 days

**Description:**
Implement complete CrewAI runtime adapter to enable multi-agent collaboration workflows.

**Reasoning:**
- CrewAI specializes in multi-agent coordination
- Enables advanced collaborative workflows
- Supports role-based agent systems
- Adds crew composition capabilities

**Prerequisites:**
- CrewAI installed: `pip install crewai`
- Understanding of CrewAI patterns (Crews, Agents, Tasks)
- Access to LLM provider

**Implementation Steps:**

1. **Study CrewAI Architecture**
   - Understand Crew, Agent, Task concepts
   - Review CrewAI tool integration

2. **Implement Core Methods**
   ```python
   class CrewAIRuntime:
       def execute(self, agent_spec: AgentSpec, input_data: dict) -> dict:
           crew = self._create_crew(agent_spec)
           task = self._create_task(input_data)
           result = crew.kickoff(tasks=[task])
           return self._format_result(result)
   ```

3. **Agent Mapping**
   - Convert CloudCurio agent specs to CrewAI agents
   - Map roles and responsibilities
   - Configure collaboration patterns

4. **Task Creation**
   - Generate CrewAI tasks from inputs
   - Define task dependencies
   - Set up task outputs

**Validation:**
```bash
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml \
  --runtime crewai \
  --input "collaborative task"
```

**Success Criteria:**
- ✅ Can execute agents with CrewAI runtime
- ✅ Multi-agent collaboration works
- ✅ Task delegation functions correctly
- ✅ All tests pass

---

### TASK-RA-003: Implement Full PydanticAI Runtime Adapter
**Priority:** P1 (High)  
**Status:** 🔄 In Progress (Stub exists)  
**Estimated Effort:** 2-4 days

**Description:**
Implement complete PydanticAI runtime adapter for type-safe agent execution.

**Implementation Steps:**

1. **Install PydanticAI**
   ```bash
   pip install pydantic-ai
   ```

2. **Implement Adapter**
   - Map AgentSpec to PydanticAI agent
   - Configure type-safe inputs/outputs
   - Implement validation layer

3. **Type Safety**
   - Define Pydantic models for all I/O
   - Add runtime type checking
   - Generate validation errors

**Success Criteria:**
- ✅ Type-safe agent execution
- ✅ Validation catches errors early
- ✅ All tests pass

---

## Agent Development

### TASK-AD-001: Create Agent Discovery API
**Priority:** P0 (Critical)  
**Status:** 🔄 Partially Complete (inventory.py covers discovery; REST API layer still needed)  
**Estimated Effort:** 1-2 days (REST layer only)

See `TASK-RMS-004` for the full API server implementation.

The `cbw_foundry.inventory.Inventory` class already provides:
- `list_all(type?)` – list agents
- `search(query, type?)` – search
- `get(name)` – get single item

**Remaining work:** wrap these in FastAPI routes (see TASK-RMS-004).

---

### TASK-AD-002: Implement Agent Templates System
**Priority:** P2 (Medium)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Description:**
Create a templating system for quickly scaffolding new agents based on common patterns.

**Implementation Steps:**

1. **Create Template Library**
   ```
   agents/templates/
   ├── basic_assistant/
   │   ├── spec.agent.yaml.j2
   │   ├── prompt.md.j2
   │   └── tests.yaml.j2
   ├── data_processor/
   ├── api_integrator/
   └── workflow_orchestrator/
   ```

2. **Implement Template Engine**
   ```python
   class AgentTemplate:
       def render(self, name: str, **kwargs) -> dict:
           """Render template with provided parameters."""
       
       def list_templates(self) -> list[str]:
           """List available templates."""
   ```

3. **Add CLI Command**
   ```bash
   ./bin/cbw-agent new my_agent --template basic_assistant
   ```

**Success Criteria:**
- ✅ Multiple templates available
- ✅ CLI command works
- ✅ Generated agents are valid
- ✅ Documentation complete

---

## MCP Server Enhancements

### TASK-MCP-001: Add Docker Configurations for All MCP Servers
**Priority:** P1 (High)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Description:**
Create Dockerfile and docker-compose configurations for all MCP servers to enable containerized deployment.

**Implementation Steps:**

1. **Create Dockerfiles**
   ```dockerfile
   # mcp-servers/automation/Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   EXPOSE 8000
   
   CMD ["python", "-m", "mcp_servers.automation"]
   ```

2. **Create docker-compose**
   ```yaml
   # docker/compose/mcp-servers/docker-compose.yml
   version: '3.8'
   services:
     automation:
       build: ../../../mcp-servers/automation
       ports:
         - "8001:8000"
     media:
       build: ../../../mcp-servers/media
       ports:
         - "8002:8000"
   ```

3. **Add Health Checks**

**Files to Create:**
- `mcp-servers/automation/Dockerfile`
- `mcp-servers/media/Dockerfile`
- `mcp-servers/content-optimizer/Dockerfile`
- `docker/compose/mcp-servers/docker-compose.yml`
- `docs/MCP_DEPLOYMENT.md`

**Success Criteria:**
- ✅ All MCP servers have Dockerfiles
- ✅ docker-compose configuration works
- ✅ Health checks functional

---

## Testing & Quality

### TASK-TQ-001: Achieve 80% Test Coverage
**Priority:** P1 (High)  
**Status:** 🔄 In Progress  
**Current Coverage:** ~60%  
**Target Coverage:** 80%+  
**Estimated Effort:** 5-7 days

**Implementation Steps:**

1. **Generate Coverage Report**
   ```bash
   pytest --cov=cbw_foundry --cov-report=html
   open htmlcov/index.html
   ```

2. **Identify Low Coverage Areas**
   - Look for modules < 80% coverage
   - Focus on critical business logic
   - Prioritize security-sensitive code

3. **Write Missing Tests**
   - Unit tests for utility functions
   - Integration tests for workflows
   - Edge case testing
   - Error handling tests

**Validation:**
```bash
pytest --cov=cbw_foundry --cov-report=term --cov-fail-under=80
```

**Success Criteria:**
- ✅ 80%+ overall coverage
- ✅ 100% coverage on security code
- ✅ All critical paths tested

---

## Documentation

### TASK-DOC-001: Generate API Documentation
**Priority:** P1 (High)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Implementation Steps:**

1. **Install Sphinx**
   ```bash
   pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
   ```

2. **Configure Sphinx**
   ```python
   # docs/conf.py
   extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx_autodoc_typehints']
   ```

3. **Generate Documentation**
   ```bash
   sphinx-apidoc -o docs/api src/cbw_foundry
   cd docs && make html
   ```

---

## Infrastructure & DevOps

### TASK-INFRA-001: Create Windows Installation Script
**Priority:** P2 (Medium)  
**Status:** ❌ Not Started  
**Estimated Effort:** 2-3 days

**Implementation Steps:**

1. **Create PowerShell Script**
   ```powershell
   # scripts/bootstrap.ps1
   Write-Host "CloudCurio Monorepo Bootstrap (Windows)"
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   pre-commit install
   ```

---

## Summary

| Task | Priority | Status |
|------|----------|--------|
| TASK-RMS-002: Download & Install Assets | P0 | ❌ Not Started |
| TASK-RMS-003: Shell Terminal Enhancement | P1 | ❌ Not Started |
| TASK-RMS-004: Python API Server | P1 | ❌ Not Started |
| TASK-RMS-005: MCP Server for Inventory | P2 | ❌ Not Started |
| TASK-RA-001: LangChain Runtime | P1 | 🔄 Stub |
| TASK-RA-002: CrewAI Runtime | P1 | 🔄 Stub |
| TASK-RA-003: PydanticAI Runtime | P1 | 🔄 Stub |
| TASK-AD-002: Agent Templates | P2 | ❌ Not Started |
| TASK-MCP-001: Docker for MCP | P1 | ❌ Not Started |
| TASK-TQ-001: 80% Test Coverage | P1 | 🔄 In Progress |
| TASK-DOC-001: API Documentation | P1 | ❌ Not Started |
| TASK-INFRA-001: Windows Bootstrap | P2 | ❌ Not Started |

---

**Version:** 1.1.0  
**Maintained by:** @cbwinslow  
**Last Updated:** 2026-02-23
