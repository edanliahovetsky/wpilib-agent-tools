# wpilib-agent-tools

`wpilib-agent-tools` packages two artifacts in one repo:

1. A shareable Python CLI for WPILib simulation/log workflows (`agent/`)
2. A Codex skill bundle for agent orchestration (`skills/wpilib-agent-tools/`)

## Quick Start

```bash
make bootstrap
make skill-sync-local
make smoke
```

## Common Commands

```bash
make test
make skill-validate
make validate-2026
```

## Setup Notes

- Use `pipx` for globally installed CLI usage.
- Use `pip` in a virtual environment for development and testing in this repo.

## Codex Skill Sync

`make skill-sync-local` installs a symlink at:

- `$CODEX_HOME/skills/wpilib-agent-tools`
- default `CODEX_HOME` is `~/.codex`

Use copy mode if needed:

```bash
./scripts/sync_skill.sh --mode copy
```

## CLI Resolution Order

Repo automation prefers local code so validation reflects your latest edits:

1. `WPILIB_AGENT_TOOLS_CLI` override (if set)
2. `./.venv/bin/wpilib-agent-tools`
3. `wpilib-agent-tools` from `PATH`
4. `python3 -m wpilib_agent_tools` via repo `agent/src`

## Generic Robot Validation

Use the reusable validator against any robot repo:

```bash
./scripts/validate_robot_repo.sh --repo /path/to/robot-repo --profile generic
```

Profile example:

```bash
./scripts/validate_robot_repo.sh \
  --repo ~/FRC/2026-Robot-Code \
  --branch comp-dev \
  --profile 2026-robot-code
```

The validator reports pass/fail using log evidence (DS state, state transitions, log generation), not process exit code alone.
