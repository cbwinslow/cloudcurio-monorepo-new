#!/usr/bin/env python3
"""desktop_commander_bootstrap.py

Date: 2026-01-01
Author: ChatGPT (for Blaine Winslow / cbwinslow)

Summary
-------
Bootstraps a production-minded, multi-agent "Desktop Commander" repo skeleton that can run 24/7.
This script creates a project directory with:
  - Agent architecture (orchestrator/planner/executor/validator/memory/improver)
  - Event bus + task queue (SQLite-backed)
  - Memory system: short-term session notes + long-term artifacts placeholders
  - Model router: OpenRouter (free) first, Ollama fallback (local)
  - Tool framework with strict allowlist + path sandboxing
  - Systemd service + timer templates
  - Structured JSON logging + log rotation guidance
  - Test stubs + docs

Inputs
------
Command-line args:
  --dest PATH        Destination directory where the project will be created.
  --name NAME        Project folder name. Default: desktop-commander
  --force            Overwrite existing files (safe-merge by default).
  --print-tree       Print the resulting tree.
  --init-git         Initialize a git repo and make an initial commit (if git available).

Outputs
-------
A new directory structure under --dest/--name containing runnable code.

Security & Safety Notes
-----------------------
- The Executor tool runner is intentionally conservative: it uses an allowlist and path sandbox.
- Secrets are NEVER written into tracked files; `.env` is generated as a template.
- Autopatch/self-modification is NOT enabled by default. Improvements are recorded as tickets.

Modification Log
----------------
- 2026-01-01: Initial bootstrap skeleton (Batch 1)
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import logging
import os
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap
from typing import Dict, List, Optional, Tuple


# ------------------------------
# Constants
# ------------------------------
DEFAULT_PROJECT_NAME = "desktop-commander"
DEFAULT_PYTHON_MIN = (3, 10)


# ------------------------------
# Logging Setup
# ------------------------------
class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def build_logger() -> logging.Logger:
    logger = logging.getLogger("dc_bootstrap")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


log = build_logger()


# ------------------------------
# Utilities
# ------------------------------
@dataclasses.dataclass
class WriteResult:
    path: pathlib.Path
    action: str  # created|updated|skipped


def ensure_python_version() -> None:
    if sys.version_info < DEFAULT_PYTHON_MIN:
        raise RuntimeError(
            f"Python {DEFAULT_PYTHON_MIN[0]}.{DEFAULT_PYTHON_MIN[1]}+ required; "
            f"found {sys.version_info.major}.{sys.version_info.minor}."
        )


def safe_mkdir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def write_text_file(
    path: pathlib.Path,
    content: str,
    *,
    force: bool,
    mode: int = 0o644,
) -> WriteResult:
    """Write a UTF-8 text file with safe merge semantics.

    Behavior
    --------
    - If file does not exist: create.
    - If exists and content differs:
        - force=False -> skip
        - force=True  -> overwrite
    """
    content = normalize_newlines(content)
    if not path.exists():
        safe_mkdir(path.parent)
        path.write_text(content, encoding="utf-8")
        os.chmod(path, mode)
        return WriteResult(path=path, action="created")

    existing = path.read_text(encoding="utf-8")
    if existing == content:
        return WriteResult(path=path, action="skipped")

    if not force:
        return WriteResult(path=path, action="skipped")

    path.write_text(content, encoding="utf-8")
    os.chmod(path, mode)
    return WriteResult(path=path, action="updated")


def run_cmd(cmd: List[str], cwd: pathlib.Path) -> Tuple[int, str, str]:
    """Run a command and return (code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 127, "", str(e)


def which(binary: str) -> Optional[str]:
    return shutil.which(binary)


def print_tree(root: pathlib.Path) -> None:
    """Pretty-print a directory tree."""
    root = root.resolve()
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        depth = len(rel.parts)
        indent = "  " * (depth - 1)
        if p.is_dir():
            print(f"{indent}{rel.name}/")
        else:
            print(f"{indent}{rel.name}")


# ------------------------------
# Template Content
# ------------------------------
README_MD = """# Desktop Commander (Multi-Agent)

A 24/7 desktop assistant daemon with a multi-agent architecture:

- **Orchestrator**: routes tasks + policy enforcement
- **Planner**: decomposes goals into testable plans
- **Executor**: runs tools (safe allowlist + path sandbox)
- **Validator**: verifies plan & results, runs checks/tests
- **Memory**: short-term + long-term storage + retrieval
- **Improver**: postmortems + patch proposals (Validator-gated)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run in foreground
python -m dc_daemon

# Optional: install systemd unit templates
# See docs/systemd.md
```

## Safety
- Tool execution uses strict allowlists and path sandboxing.
- Secrets are loaded from `.env` only (never committed).
- Autopatch mode is disabled by default.

## Next
- Add Postgres + pgvector for long-term memory
- Add a TUI/web UI
- Add more tools: window manager controls, notifications, app launchers
"""

REQUIREMENTS_TXT = """pydantic>=2.7
python-dotenv>=1.0
PyYAML>=6.0
httpx>=0.27
rich>=13.7
"""

ENV_EXAMPLE = """# Desktop Commander environment variables

# --- Model routing ---
# OpenRouter
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL_PREFERRED=deepseek/deepseek-r1:free

# Ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL_FALLBACK=qwen2.5-coder:7b

# --- Storage ---
DC_DB_PATH=./data/desktop_commander.sqlite
DC_LOG_DIR=./logs

# --- Safety / Policies ---
DC_ALLOWED_WRITE_ROOT=./workspace
DC_ALLOWED_COMMANDS=echo,ls,pwd,whoami,uname,cat,grep,find,git,python,pip
"""

DEFAULTS_YML = """# Safe defaults. Override with config/machine/<hostname>.yml

router:
  prefer: openrouter
  openrouter:
    timeout_s: 30
    max_retries: 2
  ollama:
    timeout_s: 60

scheduler:
  tick_seconds: 5
  maintenance_minutes: 15
  memory_compact_minutes: 60

safety:
  # Path sandbox: all writes MUST remain under this root.
  allowed_write_root: "./workspace"
  # Command allowlist: Executor can only run these commands.
  allowed_commands:
    - echo
    - ls
    - pwd
    - whoami
    - uname
    - cat
    - grep
    - find
    - git
    - python
    - pip

memory:
  short_term:
    session_ttl_days: 7
  long_term:
    enabled: false
    provider: "postgres"
"""

POLICIES_YML = """# Policy enforcement rules.

approvals:
  # If true, any command outside allowlist is blocked (recommended).
  strict_command_allowlist: true
  # If true, any write outside allowed root is blocked (recommended).
  strict_path_sandbox: true

risk:
  # Commands matching these regexes are always denied.
  deny_regex:
    - "\\brm\\b"
    - "\\bdd\\b"
    - "\\bmkfs\\b"
    - "\\bshutdown\\b"
    - "\\breboot\\b"
    - "\\bkill\\s+-9\\b"

"""

SYSTEMD_MD = """# systemd setup

You can run Desktop Commander as a background service.

## Install (user service)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/desktop-commander.service ~/.config/systemd/user/
cp systemd/desktop-commander.timer ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now desktop-commander.service

# Optional periodic tasks
systemctl --user enable --now desktop-commander.timer

journalctl --user -u desktop-commander.service -f
```

## Notes
- Service uses working directory of the repo.
- Configure `.env` and `config/*.yml` first.
"""

SYSTEMD_SERVICE = """[Unit]
Description=Desktop Commander (Multi-Agent Daemon)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/dev/desktop-commander
Environment=PYTHONUNBUFFERED=1
ExecStart=%h/dev/desktop-commander/.venv/bin/python -m dc_daemon
Restart=always
RestartSec=3

# Resource safety knobs (tune as needed)
Nice=5

[Install]
WantedBy=default.target
"""

SYSTEMD_TIMER = """[Unit]
Description=Desktop Commander periodic maintenance

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
"""

# ------------------------------
# Core Python Package Files
# ------------------------------
DC_DAEMON_INIT = """"""Desktop Commander daemon entrypoint."""

from .main import main

if __name__ == "__main__":
    raise SystemExit(main())
"""

DC_MAIN = """"""dc_daemon/main.py

Date: 2026-01-01
Author: ChatGPT (for Blaine Winslow / cbwinslow)

Summary
-------
Foreground daemon runner for Desktop Commander.

Implements:
- Event bus + scheduler ticks
- Orchestrator loop
- Safe shutdown handling

Notes
-----
This is Batch 1: minimal but working scaffolding.
"""

from __future__ import annotations

import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console

from dc_daemon.core.config import load_config
from dc_daemon.core.logging import get_logger
from dc_daemon.core.bus import EventBus, Event
from dc_daemon.core.store import SqliteStore
from dc_daemon.agents.orchestrator import Orchestrator


console = Console()
log = get_logger("dc")


@dataclass
class Runtime:
    running: bool = True


def _install_signal_handlers(rt: Runtime) -> None:
    def _handler(signum, _frame):
        log.warning("signal_received", extra={"signum": signum})
        rt.running = False

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def main() -> int:
    load_dotenv()

    cfg = load_config()

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    db_path = Path(os.getenv("DC_DB_PATH", "./data/desktop_commander.sqlite"))
    store = SqliteStore(db_path)
    store.migrate()

    bus = EventBus()
    orch = Orchestrator(cfg=cfg, store=store, bus=bus)

    rt = Runtime(True)
    _install_signal_handlers(rt)

    tick_s = cfg.scheduler.tick_seconds
    log.info("daemon_start", extra={"tick_seconds": tick_s, "db": str(db_path)})

    # Seed a startup event
    bus.publish(Event(type="SYSTEM", name="STARTUP", payload={"cwd": os.getcwd()}))

    last_maintenance = 0.0
    last_compact = 0.0

    while rt.running:
        now = time.time()

        # periodic events
        if now - last_maintenance > cfg.scheduler.maintenance_minutes * 60:
            last_maintenance = now
            bus.publish(Event(type="SCHEDULED", name="MAINTENANCE_TICK", payload={}))

        if now - last_compact > cfg.scheduler.memory_compact_minutes * 60:
            last_compact = now
            bus.publish(Event(type="SCHEDULED", name="MEMORY_COMPACT_TICK", payload={}))

        # orchestrator step
        orch.step()

        time.sleep(tick_s)

    log.info("daemon_stop")
    return 0
"""

DC_CONFIG = """"""dc_daemon/core/config.py

Config loading with layered overrides.

Load order:
  1) config/defaults.yml
  2) config/machine/<hostname>.yml (optional)
  3) env overrides where appropriate
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class RouterOpenRouter(BaseModel):
    timeout_s: int = 30
    max_retries: int = 2


class RouterOllama(BaseModel):
    timeout_s: int = 60


class RouterConfig(BaseModel):
    prefer: str = "openrouter"  # openrouter|ollama
    openrouter: RouterOpenRouter = Field(default_factory=RouterOpenRouter)
    ollama: RouterOllama = Field(default_factory=RouterOllama)


class SchedulerConfig(BaseModel):
    tick_seconds: int = 5
    maintenance_minutes: int = 15
    memory_compact_minutes: int = 60


class SafetyConfig(BaseModel):
    allowed_write_root: str = "./workspace"
    allowed_commands: List[str] = Field(default_factory=list)


class MemoryShortTerm(BaseModel):
    session_ttl_days: int = 7


class MemoryLongTerm(BaseModel):
    enabled: bool = False
    provider: str = "postgres"


class MemoryConfig(BaseModel):
    short_term: MemoryShortTerm = Field(default_factory=MemoryShortTerm)
    long_term: MemoryLongTerm = Field(default_factory=MemoryLongTerm)


class AppConfig(BaseModel):
    router: RouterConfig = Field(default_factory=RouterConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge b into a (recursive)."""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> AppConfig:
    base = _read_yaml(Path("config/defaults.yml"))

    hostname = socket.gethostname().split(".")[0]
    machine = _read_yaml(Path("config/machine") / f"{hostname}.yml")

    merged = _deep_merge(base, machine)

    # Environment overrides (safe, minimal)
    env_cmds = os.getenv("DC_ALLOWED_COMMANDS")
    if env_cmds:
        merged.setdefault("safety", {})
        merged["safety"]["allowed_commands"] = [c.strip() for c in env_cmds.split(",") if c.strip()]

    env_root = os.getenv("DC_ALLOWED_WRITE_ROOT")
    if env_root:
        merged.setdefault("safety", {})
        merged["safety"]["allowed_write_root"] = env_root

    return AppConfig.model_validate(merged)
"""

DC_LOGGING = """"""dc_daemon/core/logging.py

Structured logging using JSON lines.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import datetime as _dt


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach structured extras if present
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
    return logger
"""

DC_BUS = """"""dc_daemon/core/bus.py

Simple in-process event bus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Deque, Dict, Optional
from collections import deque


@dataclass
class Event:
    type: str
    name: str
    payload: Dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._q: Deque[Event] = deque()

    def publish(self, event: Event) -> None:
        self._q.append(event)

    def poll(self) -> Optional[Event]:
        if not self._q:
            return None
        return self._q.popleft()
"""

DC_STORE = """"""dc_daemon/core/store.py

SQLite store for:
- tasks queue
- session memory
- run logs metadata

This keeps Batch 1 self-contained and robust.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TaskRow:
    id: int
    status: str
    priority: int
    kind: str
    payload_json: str
    created_ts: str
    updated_ts: str


class SqliteStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def migrate(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_ts TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_ts TEXT NOT NULL DEFAULT (datetime('now'))
                );
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS session_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    tags TEXT NOT NULL DEFAULT '',
                    created_ts TEXT NOT NULL DEFAULT (datetime('now'))
                );
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_ts TEXT NOT NULL DEFAULT (datetime('now'))
                );
                """
            )

    def enqueue_task(self, kind: str, payload_json: str, priority: int = 50) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO tasks (status, priority, kind, payload_json) VALUES ('queued', ?, ?, ?)",
                (priority, kind, payload_json),
            )
            return int(cur.lastrowid)

    def fetch_next_task(self) -> Optional[TaskRow]:
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM tasks WHERE status='queued' ORDER BY priority ASC, id ASC LIMIT 1"
            ).fetchone()
            if not row:
                return None
            return TaskRow(**dict(row))

    def set_task_status(self, task_id: int, status: str) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE tasks SET status=?, updated_ts=datetime('now') WHERE id=?",
                (status, task_id),
            )

    def put_session_memory(self, key: str, value: str, tags: str = "") -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO session_memory (key, value, tags) VALUES (?, ?, ?)",
                (key, value, tags),
            )

    def list_session_memory(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM session_memory ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_improvement(self, title: str, details: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO improvements (title, details) VALUES (?, ?)",
                (title, details),
            )
            return int(cur.lastrowid)
"""

DC_ORCH = """"""dc_daemon/agents/orchestrator.py

Orchestrator: routes events and queued tasks to specialist agents.
Batch 1 includes:
- A minimal planner/validator/executor flow for tool tasks
- Memory write hooks

Later upgrades:
- parallel agents
- webhooks/UI
- long-term vector memory
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from dc_daemon.core.bus import EventBus, Event
from dc_daemon.core.config import AppConfig
from dc_daemon.core.logging import get_logger
from dc_daemon.core.store import SqliteStore

from dc_daemon.agents.planner import PlannerAgent
from dc_daemon.agents.validator import ValidatorAgent
from dc_daemon.agents.executor import ExecutorAgent
from dc_daemon.agents.memory import MemoryAgent
from dc_daemon.agents.improver import ImproverAgent


log = get_logger("dc.orchestrator")


@dataclass
class Orchestrator:
    cfg: AppConfig
    store: SqliteStore
    bus: EventBus

    def __post_init__(self) -> None:
        self.planner = PlannerAgent(cfg=self.cfg)
        self.validator = ValidatorAgent(cfg=self.cfg)
        self.executor = ExecutorAgent(cfg=self.cfg)
        self.memory = MemoryAgent(cfg=self.cfg, store=self.store)
        self.improver = ImproverAgent(cfg=self.cfg, store=self.store)

    def step(self) -> None:
        # 1) drain events
        evt = self.bus.poll()
        while evt is not None:
            self._handle_event(evt)
            evt = self.bus.poll()

        # 2) process one queued task per tick (conservative)
        task = self.store.fetch_next_task()
        if not task:
            return

        self.store.set_task_status(task.id, "running")
        try:
            payload = json.loads(task.payload_json)
            result = self._run_task(kind=task.kind, payload=payload)
            self.store.set_task_status(task.id, "done")
            # record a short memory note
            self.memory.note(
                key=f"task:{task.id}",
                value=json.dumps({"kind": task.kind, "result": result})[:4000],
                tags="task,done",
            )
        except Exception as e:
            log.error("task_failed", extra={"task_id": task.id, "err": str(e)})
            self.store.set_task_status(task.id, "error")

    def _handle_event(self, evt: Event) -> None:
        if evt.name == "STARTUP":
            self.memory.note("startup", json.dumps(evt.payload), tags="system")
            return

        if evt.name == "MAINTENANCE_TICK":
            self.improver.sweep()
            return

        if evt.name == "MEMORY_COMPACT_TICK":
            self.memory.compact()
            return

        # Unknown events are still recorded for traceability
        self.memory.note("event", json.dumps({"type": evt.type, "name": evt.name, "payload": evt.payload})[:4000], tags="event")

    def _run_task(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Batch 1 task runner.

        Supported kinds:
        - "shell": run a safe command
        - "note": store memory note
        """
        if kind == "note":
            self.memory.note(payload.get("key", "note"), payload.get("value", ""), tags=payload.get("tags", ""))
            return {"ok": True}

        if kind == "shell":
            plan = self.planner.plan_shell(payload)
            approval = self.validator.review_plan(plan)
            if not approval.approved:
                return {"ok": False, "blocked": True, "reasons": approval.reasons}

            exec_result = self.executor.run_shell(plan)
            verify = self.validator.verify_result(plan, exec_result)

            # postmortem ticket if something looks off
            if not verify.approved:
                self.improver.open_ticket(
                    title="Validation failed for shell task",
                    details=json.dumps({"plan": plan, "exec": exec_result, "verify": verify.model_dump()}, indent=2)[:8000],
                )

            return {"ok": verify.approved, "exec": exec_result, "verify": verify.model_dump()}

        return {"ok": False, "error": f"unknown task kind: {kind}"}
"""

DC_PLANNER = """"""dc_daemon/agents/planner.py

Planner Agent
-------------
Batch 1: generate a structured plan for a shell command.
Later: full task DAG planning, multi-agent decomposition, user goal reasoning.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from dc_daemon.core.config import AppConfig


class ShellPlan(BaseModel):
    kind: str = "shell"
    command: List[str]
    cwd: str = "."
    expected_exit_codes: List[int] = Field(default_factory=lambda: [0])
    expected_artifacts: List[str] = Field(default_factory=list)
    notes: str = ""


class PlannerAgent:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg

    def plan_shell(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal: ensure command is list
        cmd = payload.get("command")
        if isinstance(cmd, str):
            # Split conservatively on whitespace
            cmd_list = [c for c in cmd.strip().split() if c]
        elif isinstance(cmd, list):
            cmd_list = [str(x) for x in cmd]
        else:
            cmd_list = ["echo", "No command provided"]

        plan = ShellPlan(
            command=cmd_list,
            cwd=str(payload.get("cwd", ".")),
            notes=str(payload.get("notes", "")),
        )
        return plan.model_dump()
"""

DC_VALIDATOR = """"""dc_daemon/agents/validator.py

Validator Agent
---------------
Batch 1: approves/blocks shell plans based on allowlist + deny-regex policies.
Also checks exit codes and basic artifact expectations.

Later upgrades:
- semantic validation (LLM-based)
- unit/integration test runner
- rollback verification
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from dc_daemon.core.config import AppConfig


class PlanApproval(BaseModel):
    approved: bool
    reasons: List[str] = Field(default_factory=list)


class ResultApproval(BaseModel):
    approved: bool
    reasons: List[str] = Field(default_factory=list)


class ValidatorAgent:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, Any]:
        p = Path("config/policies.yml")
        if not p.exists():
            return {}
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    def review_plan(self, plan: Dict[str, Any]) -> PlanApproval:
        reasons: List[str] = []

        cmd = plan.get("command") or []
        if not isinstance(cmd, list) or not cmd:
            return PlanApproval(approved=False, reasons=["empty or invalid command"])  # type: ignore

        command_name = str(cmd[0])

        # deny-regex
        deny_patterns = (self.policies.get("risk", {}) or {}).get("deny_regex", [])
        joined = " ".join([str(x) for x in cmd])
        for pat in deny_patterns:
            try:
                if re.search(pat, joined, flags=re.IGNORECASE):
                    reasons.append(f"denied by regex policy: {pat}")
            except re.error:
                reasons.append(f"invalid deny regex in policy: {pat}")

        # allowlist
        allow = set(self.cfg.safety.allowed_commands)
        if self.policies.get("approvals", {}).get("strict_command_allowlist", True):
            if command_name not in allow:
                reasons.append(f"command not in allowlist: {command_name}")

        # path sandbox check for cwd
        cwd = Path(str(plan.get("cwd", "."))).resolve()
        root = Path(self.cfg.safety.allowed_write_root).resolve()
        if self.policies.get("approvals", {}).get("strict_path_sandbox", True):
            # For Batch 1, we require cwd to be within root, even for read-only commands.
            # This is conservative. You can loosen this later.
            try:
                cwd.relative_to(root)
            except Exception:
                reasons.append(f"cwd outside allowed root: cwd={cwd} root={root}")

        return PlanApproval(approved=(len(reasons) == 0), reasons=reasons)

    def verify_result(self, plan: Dict[str, Any], exec_result: Dict[str, Any]) -> ResultApproval:
        reasons: List[str] = []
        expected = set(plan.get("expected_exit_codes") or [0])
        code = int(exec_result.get("exit_code", 999))
        if code not in expected:
            reasons.append(f"unexpected exit code: {code} not in {sorted(expected)}")

        # artifact expectations (existence)
        for artifact in plan.get("expected_artifacts") or []:
            if not Path(str(artifact)).exists():
                reasons.append(f"expected artifact missing: {artifact}")

        return ResultApproval(approved=(len(reasons) == 0), reasons=reasons)
"""

DC_EXECUTOR = """"""dc_daemon/agents/executor.py

Executor Agent
--------------
Batch 1: safe shell runner.

Guarantees:
- Executes commands as list (no shell=True)
- Captures stdout/stderr
- Enforces cwd existence

Later upgrades:
- run as restricted OS user / container
- more tools and typed tool contracts
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from dc_daemon.core.config import AppConfig


class ExecutorAgent:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg

    def run_shell(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        cmd: List[str] = [str(x) for x in (plan.get("command") or [])]
        cwd = Path(str(plan.get("cwd", ".")))
        cwd.mkdir(parents=True, exist_ok=True)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout[-20000:],
                "stderr": proc.stderr[-20000:],
                "cmd": cmd,
                "cwd": str(cwd),
            }
        except Exception as e:
            return {"exit_code": 127, "stdout": "", "stderr": str(e), "cmd": cmd, "cwd": str(cwd)}
"""

DC_MEMORY = """"""dc_daemon/agents/memory.py

Memory Agent
------------
Batch 1: writes and compacts short-term memory to SQLite.

Later upgrades:
- long-term memory: Postgres/pgvector
- retrieval with hybrid search
- personal preference inference
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict

from dc_daemon.core.config import AppConfig
from dc_daemon.core.store import SqliteStore


class MemoryAgent:
    def __init__(self, cfg: AppConfig, store: SqliteStore) -> None:
        self.cfg = cfg
        self.store = store

    def note(self, key: str, value: str, tags: str = "") -> None:
        self.store.put_session_memory(key=key, value=value, tags=tags)

    def compact(self) -> None:
        # Batch 1 placeholder: in later batches, prune older than TTL.
        # SQLite pruning can be based on created_ts < now - ttl.
        self.note("memory.compact", json.dumps({"ts": time.time(), "status": "noop_batch1"}), tags="maintenance")
"""

DC_IMPROVER = """"""dc_daemon/agents/improver.py

Improver Agent
--------------
Batch 1: opens improvement tickets based on validation issues.

Later upgrades:
- patch proposals + git branch creation
- autopatch (opt-in) with validator gate + rollback
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict

from dc_daemon.core.config import AppConfig
from dc_daemon.core.store import SqliteStore


class ImproverAgent:
    def __init__(self, cfg: AppConfig, store: SqliteStore) -> None:
        self.cfg = cfg
        self.store = store

    def open_ticket(self, title: str, details: str) -> int:
        return self.store.add_improvement(title=title, details=details)

    def sweep(self) -> None:
        # Batch 1 placeholder: run periodic health checks.
        self.store.add_improvement(
            title="Maintenance sweep executed",
            details=json.dumps({"ts": time.time(), "note": "Batch1 placeholder sweep"}),
        )
"""

TOOLS_README = """# Tools

Batch 1 includes only a safe **shell tool** built into the Executor.

Next tool modules to add:
- filesystem read/write with path sandbox enforcement
- process/service control (read-only to start)
- notification tool
- app/window manager control
"""

TEST_SMOKE = """"""tests/test_smoke.py

Batch 1 smoke test.
"""

def test_smoke_import():
    import dc_daemon
"""

PYPROJECT = """[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "desktop-commander"
version = "0.1.0"
description = "Multi-agent desktop assistant daemon"
requires-python = ">=3.10"
"""

SETUP_CFG = """[metadata]
name = desktop-commander
version = 0.1.0

[options]
packages = find:
include_package_data = True
python_requires = >=3.10
"""

GITIGNORE = """# Python
__pycache__/
*.pyc
.venv/

# Env
.env

# Data / logs
/data/
/logs/
/workspace/

# Editors
.vscode/
.idea/
"""


# ------------------------------
# Project Writer
# ------------------------------
@dataclasses.dataclass
class BootstrapOptions:
    dest: pathlib.Path
    name: str
    force: bool
    print_tree: bool
    init_git: bool


def make_files() -> Dict[str, Tuple[str, int]]:
    """Return mapping of relative path -> (content, mode)."""
    return {
        "README.md": (README_MD, 0o644),
        "requirements.txt": (REQUIREMENTS_TXT, 0o644),
        ".env.example": (ENV_EXAMPLE, 0o600),
        "pyproject.toml": (PYPROJECT, 0o644),
        "setup.cfg": (SETUP_CFG, 0o644),
        ".gitignore": (GITIGNORE, 0o644),
        "docs/systemd.md": (SYSTEMD_MD, 0o644),
        "docs/tools.md": (TOOLS_README, 0o644),
        "config/defaults.yml": (DEFAULTS_YML, 0o644),
        "config/policies.yml": (POLICIES_YML, 0o644),
        "config/machine/.keep": ("# per-host overrides\n", 0o644),
        "systemd/desktop-commander.service": (SYSTEMD_SERVICE, 0o644),
        "systemd/desktop-commander.timer": (SYSTEMD_TIMER, 0o644),
        "dc_daemon/__init__.py": ("\n", 0o644),
        "dc_daemon/__main__.py": (DC_DAEMON_INIT, 0o644),
        "dc_daemon/main.py": (DC_MAIN, 0o644),
        "dc_daemon/core/bus.py": (DC_BUS, 0o644),
        "dc_daemon/core/config.py": (DC_CONFIG, 0o644),
        "dc_daemon/core/logging.py": (DC_LOGGING, 0o644),
        "dc_daemon/core/store.py": (DC_STORE, 0o644),
        "dc_daemon/agents/orchestrator.py": (DC_ORCH, 0o644),
        "dc_daemon/agents/planner.py": (DC_PLANNER, 0o644),
        "dc_daemon/agents/validator.py": (DC_VALIDATOR, 0o644),
        "dc_daemon/agents/executor.py": (DC_EXECUTOR, 0o644),
        "dc_daemon/agents/memory.py": (DC_MEMORY, 0o644),
        "dc_daemon/agents/improver.py": (DC_IMPROVER, 0o644),
        "tests/test_smoke.py": (TEST_SMOKE, 0o644),
    }


def bootstrap(opts: BootstrapOptions) -> pathlib.Path:
    root = (opts.dest / opts.name).resolve()
    safe_mkdir(root)

    results: List[WriteResult] = []
    files = make_files()

    for rel, (content, mode) in files.items():
        p = root / rel
        res = write_text_file(p, content, force=opts.force, mode=mode)
        results.append(res)

    # Ensure runtime dirs exist
    for d in ["data", "logs", "workspace"]:
        safe_mkdir(root / d)

    # Optional git init
    if opts.init_git:
        if which("git"):
            code, out, err = run_cmd(["git", "init"], cwd=root)
            log.info("git_init", extra={"code": code, "stderr": err.strip()[:500]})
            if code == 0:
                run_cmd(["git", "add", "-A"], cwd=root)
                run_cmd(["git", "commit", "-m", "chore: initial Desktop Commander skeleton"], cwd=root)
        else:
            log.warning("git_not_found")

    created = sum(1 for r in results if r.action == "created")
    updated = sum(1 for r in results if r.action == "updated")
    skipped = sum(1 for r in results if r.action == "skipped")

    log.info("bootstrap_done", extra={"root": str(root), "created": created, "updated": updated, "skipped": skipped})

    if opts.print_tree:
        print_tree(root)

    return root


def parse_args(argv: Optional[List[str]] = None) -> BootstrapOptions:
    p = argparse.ArgumentParser(
        description="Bootstrap Desktop Commander multi-agent repo skeleton",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python desktop_commander_bootstrap.py --dest ~/dev --init-git --print-tree
              python desktop_commander_bootstrap.py --dest . --name desktop-commander --force
            """
        ),
    )
    p.add_argument("--dest", required=True, help="Destination directory")
    p.add_argument("--name", default=DEFAULT_PROJECT_NAME, help="Project folder name")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    p.add_argument("--print-tree", action="store_true", help="Print generated tree")
    p.add_argument("--init-git", action="store_true", help="Initialize git and commit")

    a = p.parse_args(argv)

    return BootstrapOptions(
        dest=pathlib.Path(a.dest).expanduser(),
        name=a.name,
        force=a.force,
        print_tree=a.print_tree,
        init_git=a.init_git,
    )


def main() -> int:
    ensure_python_version()
    opts = parse_args()
    bootstrap(opts)

    # Friendly next steps
    print("\nNext steps:\n")
    print("1) cd into the project directory")
    print("2) python -m venv .venv && source .venv/bin/activate")
    print("3) pip install -r requirements.txt")
    print("4) cp .env.example .env  (fill keys)")
    print("5) python -m dc_daemon")
    print("\nTip: Keep writes within ./workspace until you loosen policies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
