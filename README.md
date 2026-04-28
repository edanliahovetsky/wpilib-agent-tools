# wpilib-agent-tools

`wpilib-agent-tools` is an experimental, repo-first toolkit for FRC teams exploring agentic coding workflows around WPILib simulation, NT4 recording, and WPILOG analysis.

It currently bundles two pieces:

1. a Python CLI for simulation, log, graph, math, sandbox, and NT4 workflows in [`agent/`](agent/)
2. workspace support for **Codex, Claude Code, and Cursor** through one shared installer path

This is not a polished product or a universal AI coding platform. It is a practical experiment that has already been useful for closed-loop sim validation and log-driven iteration, and it is shared so other teams can try it, inspect it, and adapt the ideas.

## Quick Start

The recommended setup path is to clone the repo and install the CLI plus workspace harness support into a robot project:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

That command:

- bootstraps the local CLI into `./.venv`
- validates the Codex skill bundle structure
- runs smoke checks
- installs shared harness support into the target workspace
- creates a consistent workspace entry path for Codex, Claude Code, and Cursor

For deeper setup details, see:

- [INSTALL.md](INSTALL.md) for onboarding and install options
- [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) for the repo-first distribution strategy
- [docs/VALIDATION_STATUS.md](docs/VALIDATION_STATUS.md) for current validation coverage and known gaps
- [agent/README.md](agent/README.md) for the full CLI reference

## What It Helps With

The toolkit is meant to give coding agents and humans a better workflow surface around robot-code iteration:

- sandbox-first experiments against a robot repo
- bounded WPILib simulation runs
- NT4 recording to WPILOG
- quick WPILOG key inspection, queries, stats, and graphs
- symbolic or numeric math checks
- shared workspace instructions/rules for Codex, Claude Code, and Cursor

The core idea is not "let the model blindly edit robot code." The useful loop is:

1. make a bounded change in a sandbox
2. run sim or log analysis
3. inspect concrete evidence
4. review the resulting patch before applying anything to the real workspace

## Current Status

This project is **experimental**.

It is useful enough to try if you are already exploring agentic FRC workflows, but it still has rough edges:

- best results tend to come from stronger lead/orchestrator models and higher-reasoning modes
- token usage, usage-based pricing, and subagent usage deserve care
- model outputs still need normal engineering review
- hallucinated fixes, misunderstood logs, and weak math are realistic failure modes
- Cursor support is installer-validated, but full headless/noninteractive Cursor agent validation is still a known gap

For teams using this with students: treat it as a tool for investigation, verification, and learning, not a substitute for understanding the robot code. The workflow should make evidence easier to gather, not remove the need to reason about the system.

## Distribution Strategy

For this public snapshot, GitHub is the source of truth for:

- code
- install instructions
- supported setup flow
- tagged releases
- issue tracking

The primary distribution model is repo-first:

```bash
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

This project is **not MCP-based**. That is a scope decision for this experiment: the current implementation is a CLI plus packaged workspace guidance/harness assets. MCP may be a good direction for adjacent FRC tooling, but this repo currently optimizes for a simple, inspectable, source-first setup.

## Alternate Install Paths

These paths are supported, but secondary to the shared installer above.

### CLI only via `pipx` from GitHub

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

This is convenient if you mainly want the CLI. It does not replace the shared workspace installer for Codex, Claude Code, and Cursor.

### Harness support only

```bash
./scripts/install_harness_support.sh --workspace /path/to/robot-repo --harnesses all
```

## Migration Note

The old top-level source path `skills/wpilib-agent-tools/` is gone.

If you previously relied on that repo path directly, migrate to the supported entrypoints instead:

- `./scripts/sync_skill.sh`
- `./scripts/install_all.sh`
- `./scripts/install_harness_support.sh`

The canonical in-repo Codex skill source now lives under:

- `agent/src/wpilib_agent_tools/integrations/codex/skill_bundle`

## Common Commands

```bash
make test
make skill-validate
make smoke
make validate-2026
make release-check
```

Repo automation prefers local code so validation reflects latest edits:

1. `WPILIB_AGENT_TOOLS_CLI` override, if set
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
git tag v0.2.0
git push origin v0.2.0
```

Tag pushes matching `v*` trigger `.github/workflows/release.yml`, which runs checks, builds `sdist`/`wheel`, and uploads assets to the release.

Update `CHANGELOG.md` before tagging.
