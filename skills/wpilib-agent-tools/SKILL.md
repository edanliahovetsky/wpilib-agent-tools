---
name: wpilib-agent-tools
description: Sandbox-first WPILib simulation, NT4 recording, and WPILOG analysis orchestration with the wpilib-agent-tools CLI. Use when tasks involve running simulation, validating autonomous behavior, querying/graphing log keys, reconstructing DriverStation state, generating evidence from .wpilog files, or iterating robot-code changes safely in isolated sandboxes.
---

# WPILib Agent Tools

Use this skill to run and validate WPILib robot workflows through `wpilib-agent-tools` instead of ad-hoc shell/python glue.

## Quick Start

- Verify CLI availability:
  - `scripts/run_cli.sh --version`
- For quick local validation in a target repo:
  - `scripts/validate_robot_repo.sh --repo /path/to/robot-repo --profile generic`
- For the known 2026 profile:
  - `scripts/validate_robot_repo.sh --repo ~/FRC/2026-Robot-Code --branch comp-dev --profile 2026-robot-code`

## Workflow Selection

- Use direct commands (`logs`, `keys`, `query`, `graph`, `record`, `math`) when only analysis is needed.
- Use sandbox workflow when changing code and validating sim behavior:
  1. `sandbox create`
  2. run `sim` and analysis commands
  3. `sandbox patch`
  4. clean sandbox
- Use `scripts/validate_robot_repo.sh` for repeatable end-to-end checks and machine-readable pass/fail output.

## Pre-Sim Gate

Before `sim`, confirm:

1. The target repo is in simulation mode (for example via `Constants.java`).
2. DriverStation is auto-enabled for the target mode, or the run will not execute meaningful autonomous logic.

## Validation Expectations

Default evidence set for path execution validation:

1. A new log is generated.
2. DriverStation state shows enabled/autonomous when that mode is expected.
3. State telemetry shows a run/finish sequence (for example `FOLLOW_PATH` then `IDLE`).

Do not treat bounded-run termination as an automatic failure if telemetry checks pass (`exit_code_raw` may be `143` while normalized `exit_code` is `0`).

## Known Timing Tip

Startup overhead can consume early autonomous time. A reliable starting point for many repos is:

- `--duration 30`
- `--record-delay 3`

If early transitions are missing, lower `--record-delay`.
If startup is unstable, increase `--duration`.

## References

- Workflow patterns: `references/workflows.md`
- Validation flow: `references/validation.md`
- Timing and recorder tuning: `references/tuning-tips.md`
- Repo profile example: `references/profiles/2026-robot-code.md`
