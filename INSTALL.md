# Install and Onboarding

This file is the canonical setup guide for the first public release of `wpilib-agent-tools`.

## Who this is for

This project is a good fit if you are:

- already using agentic coding workflows for FRC
- interested in closed-loop sim validation, NT4 recording, or WPILOG analysis
- comfortable with a repo-first install flow

This is probably **not** the right tool if you want a fully polished, one-click, universal integration across every coding assistant right away.

## Recommended path: clone the repo and run the installer

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh
```

This is the recommended path because it keeps:

- the code
- the install scripts
- the skill bundle
- the docs

all in one place.

## What `install_all.sh` does

By default, it:

1. installs the CLI locally into `./.venv`
2. syncs the Codex skill bundle
3. validates the skill structure
4. runs smoke checks

Useful examples:

```bash
# Default local setup
./scripts/install_all.sh

# Global CLI via pipx, but still repo-managed docs/skill flow
./scripts/install_all.sh --cli-mode pipx --skill-mode copy

# Also install Cursor rules into a robot repo
./scripts/install_all.sh --cursor-workspace ~/FRC/2026-Robot-Code --cursor-mode core
```

## Agent-specific notes

### Codex

Codex is the most directly supported workflow today because the repo already ships a Codex skill bundle:

```bash
./scripts/sync_skill.sh --mode symlink
```

### Cursor

Cursor users can optionally install the packaged rule templates into a robot repo:

```bash
./scripts/install_cursor_rules.sh --workspace /path/to/robot-repo --mode core
```

### Claude Code and other agent environments

There is not a polished, first-class installer for every agent harness yet.

The intended first-release workflow is:

1. use this repo as the source of truth
2. read the docs in-repo
3. adapt the setup steps into your own harness if needed

That is intentional for now. A decent repo plus clear instructions is a better first release than pretending all agent environments are equally integrated already.

## Alternate install paths

### `pipx` from GitHub

If you mainly want the CLI and do not mind a secondary/manual skill setup story:

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

What `pipx` means:

- it installs a Python CLI app into its own isolated virtual environment
- then exposes the command globally on your PATH

This is cleaner than manual venv setup for CLI tools, but it mainly helps with the **CLI** half of this project.

### PyPI

PyPI is the Python package registry. If the project is published there in the future, the CLI could be installed with:

```bash
pipx install wpilib-agent-tools
```

or

```bash
pip install wpilib-agent-tools
```

For this first release, PyPI is intentionally **not** the main story. It solves the CLI side more than the full skill/setup workflow.

### Manual component install

If you want complete control, you can install pieces separately:

```bash
# local CLI
./scripts/install_cli.sh --mode local

# or pipx CLI
./scripts/install_cli.sh --mode pipx

# Codex skill
./scripts/sync_skill.sh --mode symlink
```

## Recommended mental model for this release

Think of `wpilib-agent-tools` as:

- a repo with one recommended setup path
- a CLI you can optionally install more globally
- a skill/workflow bundle that currently lives best alongside the repo docs

That is the cleanest and most honest distribution story for the first public release.
