#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"

pre-commit install || true

./bin/cbw-doctor || true
./bin/cbw-index
./bin/cbw-agent validate agents/specs/examples/*.agent.yaml
./bin/cbw-agent compile agents/specs/examples/*.agent.yaml --out dist/agents
./bin/cbw-agent eval agents/evals/golden/*.yaml

echo "Bootstrap complete."
