# wpilib-agent-tools

`wpilib-agent-tools` is a repo-first toolkit for FRC teams using agentic coding workflows around WPILib simulation, NT4 recording, and WPILOG analysis.

This repo currently ships two main pieces together:

1. a Python CLI for simulation/log workflows in [`agent/`](agent/)
2. harness support assets/docs for **Codex, Claude Code, and Cursor**

## Why this exists

This started as a side project, but it has already been genuinely useful — especially for closed-loop sim validation and log-driven iteration.

It is worth trying if you are already experimenting with agentic coding in FRC and want:

- sandbox-first robot-code iteration
- bounded sim runs
- NT4 recording to WPILOG
- quick log/query/graph tooling
- a shared installation path for Codex, Claude Code, and Cursor

## Current status

This is **useful and real**, but still **experimental**.

- not fully polished
- scoped to Codex, Claude Code, and Cursor rather than every possible coding agent
- **not MCP-based**
- best results tend to come from stronger lead/orchestrator models (for example Opus or GPT-5.4) and higher-thinking modes
- token usage and subagent usage still deserve care

## Recommended install path

For now, the canonical setup path is:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

That path keeps the code, scripts, and install instructions in one place.

What it does:

- bootstraps the local CLI into `./.venv`
- validates the skill structure
- runs smoke checks
- installs shared harness support into the target workspace
- creates a consistent workspace entry path for Codex, Claude Code, and Cursor

For deeper setup details, see:

- [INSTALL.md](INSTALL.md) — canonical onboarding/install doc
- [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) — why the first release is repo-first
- [agent/README.md](agent/README.md) — full CLI reference

## Alternate install paths

These are supported, but secondary to the shared installer path above.

### CLI only via `pipx` from GitHub

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

This is convenient if you mainly want the CLI. It does **not** replace the shared workspace installer for Codex, Claude Code, and Cursor.

### Harness support only

Use the shared harness installer directly:

```bash
./scripts/install_harness_support.sh --workspace /path/to/robot-repo --harnesses all
```

## Distribution strategy for this release

For the first public share, GitHub is the source of truth for:

- code
- install instructions
- supported setup flow
- tagged releases
- issue tracking

That means the repo + scripts + docs are the primary distribution model for now. The distro goal is near-parity support for **Codex, Claude Code, and Cursor** through one shared installer path, while `pipx` remains a convenience path for the CLI and PyPI remains deferred.

## Common commands

```bash
make test
make skill-validate
make smoke
make validate-2026
make release-check
```

## CLI resolution order

Repo automation prefers local code so validation reflects latest edits:

1. `WPILIB_AGENT_TOOLS_CLI` override (if set)
2. `./.venv/bin/wpilib-agent-tools`
3. `wpilib-agent-tools` from `PATH`
4. `python3 -m wpilib_agent_tools` via repo `agent/src`

## Release hygiene

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

## Draft share copy

A working Chief Delphi draft lives at [docs/CHIEF_DELPHI_POST.md](docs/CHIEF_DELPHI_POST.md).
