SHELL := /usr/bin/env bash

.PHONY: help bootstrap lint type test index validate compile eval doctor fmt

help:
	@echo "Targets: bootstrap lint type test index validate compile eval doctor fmt"

bootstrap:
	./scripts/bootstrap.sh

fmt:
	. .venv/bin/activate && ruff format .

lint:
	. .venv/bin/activate && ruff check .

type:
	. .venv/bin/activate && mypy src

test:
	. .venv/bin/activate && pytest -q

doctor:
	./bin/cbw-doctor

index:
	./bin/cbw-index

validate:
	./bin/cbw-agent validate $$(find agents/specs -name "*.agent.yaml")

compile:
	./bin/cbw-agent compile $$(find agents/specs -name "*.agent.yaml") --out dist/agents

eval:
	./bin/cbw-agent eval $$(find agents/evals/golden -name "*.yaml")
