# wpilib-agent-tools

`wpilib-agent-tools` packages two artifacts in one repo:

1. A shareable Python CLI for WPILib simulation/log workflows (`agent/`)
2. A Codex skill bundle for agent orchestration (`skills/wpilib-agent-tools/`)

## Quick Start (Local Contributor)

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh
```

That installs the local CLI (`.venv`), syncs the Codex skill, validates skill structure, and runs smoke checks.

## One-Command Installer

```bash
./scripts/install_all.sh --help
```

Useful examples:

```bash
# Local dev setup (default)
./scripts/install_all.sh

# Global CLI via pipx + Codex skill copy mode
./scripts/install_all.sh --cli-mode pipx --skill-mode copy

# Also install Cursor rules into a robot repo
./scripts/install_all.sh --cursor-workspace ~/FRC/2026-Robot-Code --cursor-mode core
```

## Codex Setup

Default setup:

```bash
./scripts/sync_skill.sh --mode symlink
```

This creates:

- `~/.codex/skills/wpilib-agent-tools` -> `skills/wpilib-agent-tools`

Use copy mode for snapshot installs:

```bash
./scripts/sync_skill.sh --mode copy
```

## Cursor Setup

Install rule templates into any workspace:

```bash
./scripts/install_cursor_rules.sh --workspace /path/to/robot-repo --mode core
```

Make target equivalent:

```bash
make install-cursor WORKSPACE=/path/to/robot-repo CURSOR_MODE=core
```

## Share With Other Users

### Option A: Contributor Flow (editable local repo)

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh
```

### Option B: Consumer Flow (pipx CLI + skill files)

Install CLI from GitHub (pre-PyPI):

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

Then install skill files:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/sync_skill.sh --mode copy
```

## Common Commands

```bash
make test
make skill-validate
make smoke
make validate-2026
```

## CLI Resolution Order

Repo automation prefers local code so validation reflects latest edits:

1. `WPILIB_AGENT_TOOLS_CLI` override (if set)
2. `./.venv/bin/wpilib-agent-tools`
3. `wpilib-agent-tools` from `PATH`
4. `python3 -m wpilib_agent_tools` via repo `agent/src`

## Release Hygiene

Before tagging a release:

```bash
make release-check
```

Then push a version tag to publish a GitHub Release with built artifacts:

```bash
git tag v0.1.1
git push origin v0.1.1
```

Tag pushes matching `v*` trigger `.github/workflows/release.yml`, which runs checks, builds `sdist`/`wheel`, and uploads assets to the release.

Update `CHANGELOG.md` before tagging.
