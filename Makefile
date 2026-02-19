SHELL := /bin/bash

REPO_ROOT := $(CURDIR)
SKILL_DIR := skills/wpilib-agent-tools

.PHONY: bootstrap test skill-validate skill-sync-local smoke validate-2026

bootstrap:
	@./scripts/bootstrap.sh

test:
	@if [[ -x .venv/bin/pytest ]]; then \
		cd agent && PYTHONPATH=src ../.venv/bin/pytest -q; \
	else \
		cd agent && PYTHONPATH=src python3 -m pytest -q; \
	fi

skill-validate:
	@if [[ -x .venv/bin/python ]]; then \
		.venv/bin/python scripts/validate_skill.py $(SKILL_DIR); \
	else \
		python3 scripts/validate_skill.py $(SKILL_DIR); \
	fi

skill-sync-local:
	@./scripts/sync_skill.sh --mode symlink

smoke:
	@./scripts/smoke.sh

validate-2026:
	@./scripts/validate_robot_repo.sh \
		--repo $(HOME)/FRC/2026-Robot-Code \
		--branch comp-dev \
		--profile 2026-robot-code \
		--keep-sandbox-on-fail
