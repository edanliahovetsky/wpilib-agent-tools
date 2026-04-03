# wpilib-agent-tools

`wpilib-agent-tools` is a repo-first toolkit for FRC teams using agentic coding workflows around WPILib simulation, NT4 recording, and WPILOG analysis.

This repo currently ships two pieces together:

1. a Python CLI for simulation/log workflows in [`agent/`](agent/)
2. a Codex skill bundle for agent orchestration in [`skills/wpilib-agent-tools/`](skills/wpilib-agent-tools/)

## Why this exists

This started as a side project, but it has already been genuinely useful — especially for closed-loop sim validation and log-driven iteration.

It is worth trying if you are already experimenting with agentic coding in FRC and want:

- sandbox-first robot-code iteration
- bounded sim runs
- NT4 recording to WPILOG
- quick log/query/graph tooling
- reusable workflow instructions for coding agents

## Current status

This is **useful and real**, but still **experimental**.

- not fully polished
- not universally plug-and-play across every coding agent
- **not MCP-based**
- best results tend to come from stronger lead/orchestrator models and higher-thinking modes
- token usage and subagent usage still deserve care

## Recommended install path for this first release

For now, the canonical setup path is:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh
```

That path keeps the code, scripts, and install instructions in one place.

What it does:

- bootstraps the local CLI into `./.venv`
- syncs the Codex skill bundle
- validates the skill structure
- runs smoke checks
- optionally installs Cursor rules if you pass a workspace

For deeper setup details, see:

- [INSTALL.md](INSTALL.md) — canonical onboarding/install doc
- [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) — why the first release is repo-first
- [agent/README.md](agent/README.md) — full CLI reference

## Alternate install paths

These are supported, but secondary to the repo-first path above.

### CLI only via `pipx` from GitHub

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

This is convenient if you mainly want the CLI. It does **not** fully solve the skill/setup side of the project by itself.

### Manual Codex skill sync

```bash
./scripts/sync_skill.sh --mode symlink
```

Use `--mode copy` if you want a snapshot install instead of a symlink.

### Cursor rule install

```bash
./scripts/install_cursor_rules.sh --workspace /path/to/robot-repo --mode core
```

## Distribution strategy for this release

For the first public share, GitHub is the source of truth for:

- code
- install instructions
- supported setup flow
- tagged releases
- issue tracking

That means the repo + scripts + docs are the primary distribution model for now. `pipx` is offered as a convenience path for the CLI, while PyPI and more polished multi-agent packaging are intentionally deferred until there is real usage feedback.

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
