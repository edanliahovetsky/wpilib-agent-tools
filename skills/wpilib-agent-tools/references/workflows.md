# Workflows

## Direct Analysis (No Sandbox Required)

Use this path when no code edits are required.

```bash
wpilib-agent-tools logs --json
wpilib-agent-tools keys --file <log.wpilog> --json
wpilib-agent-tools query --mode stats --file <log.wpilog> --key "<key>" --json
wpilib-agent-tools graph --file <log.wpilog> --key "<key>" --output plot.png --json
```

Tips:

- Prefer `--json` for machine parsing.
- Prefer `--summary`, `--limit`, and `--max-lines` for bounded output.

## Sandbox Iteration Workflow

Use this path for robot-code iteration plus sim validation.

```bash
wpilib-agent-tools sandbox create --name <id> --source workspace
wpilib-agent-tools sandbox run --name <id> -- sim --duration 30 --record-delay 3 --json
wpilib-agent-tools sandbox run --name <id> -- query --mode ds --json
wpilib-agent-tools sandbox patch --name <id> --output <id>.diff
wpilib-agent-tools sandbox clean --name <id>
```

Rules:

- Keep generated artifacts in sandbox unless asked otherwise.
- Export patch only after collecting evidence.
- Keep all behavior checks tied to log evidence, not process exit alone.

## Reusable Validation Script Workflow

Use `scripts/validate_robot_repo.sh` for repeatable validation and a single report.

```bash
scripts/validate_robot_repo.sh --repo /path/to/repo --profile generic
```

For repo-specific defaults:

```bash
scripts/validate_robot_repo.sh \
  --repo ~/FRC/2026-Robot-Code \
  --branch comp-dev \
  --profile 2026-robot-code
```
