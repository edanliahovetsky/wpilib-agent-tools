# WPILib Agent Tools

`wpilib-agent-tools` is a sandbox-first CLI for iterating on WPILib robot code and analyzing logs without mutating the user workspace during experimentation.

## Installation

From this repository:

```bash
cd agent
pip install -e .
```

From PyPI (when published):

```bash
pip install wpilib-agent-tools
```

## Core Principles

- Iterative code changes happen inside sandboxes, not in the user workspace.
- Source selection is explicit: `workspace`, `branch:<name>`, or `rev:<sha>`.
- Multiple sandboxes can run concurrently.
- Final workspace changes should come from an explicit patch/diff review step.

## Command Reference

### Data and analysis

- `wpilib-agent-tools logs --dir agent/logs [--json]`
- `wpilib-agent-tools keys --file <log> [--filter KEY] [--json]`
- `wpilib-agent-tools query --mode <mode> [--file <log>] [--key <key>] [--json]`
- `wpilib-agent-tools graph --key <key> [--key <key2>] [--mode values|deriv|integral] [--output graph.png]`
- `wpilib-agent-tools record --address <host> --duration <seconds> [--keys prefix] [--json]`
- `wpilib-agent-tools view [--file <log>]`

### Sandbox lifecycle

- `wpilib-agent-tools sandbox create --name <id> --source workspace`
- `wpilib-agent-tools sandbox list`
- `wpilib-agent-tools sandbox run --name <id> -- sim --duration 15`
- `wpilib-agent-tools sandbox status [--name <id>]`
- `wpilib-agent-tools sandbox stop --name <id>`
- `wpilib-agent-tools sandbox clean --name <id>`
- `wpilib-agent-tools sandbox clean --all --older-than 24`
- `wpilib-agent-tools sandbox patch --name <id> --output patch.diff`

### Cursor rules

- `wpilib-agent-tools rules install`
- `wpilib-agent-tools rules install --mode scoped|both`
- `wpilib-agent-tools rules install --target custom --output-dir <path>`

### Sandbox automation script

For non-interactive agent workflows:

```bash
agent/scripts/sandbox_lifecycle.sh create --name expA --source workspace --json
agent/scripts/sandbox_lifecycle.sh list --json
agent/scripts/sandbox_lifecycle.sh delete --name expA
```

The script wraps `wpilib-agent-tools sandbox ...` commands.

### Cursor rule setup

Install default always-on core rule (recommended):

```bash
wpilib-agent-tools rules install
```

Optional modes:

```bash
# Install only scoped optional rule
wpilib-agent-tools rules install --mode scoped

# Install both core and scoped rules
wpilib-agent-tools rules install --mode both
```

Optional custom location:

```bash
wpilib-agent-tools rules install --target custom --output-dir /path/to/rules
```

Idempotent behavior:

- Existing files are skipped by default.
- Use `--force` to overwrite installed rule files.
- Use `--json` for machine-readable install output.

## Typical Workflow

1. Create sandbox from current workspace snapshot:

   ```bash
   wpilib-agent-tools sandbox create --name tune_shooter --source workspace
   ```

2. Run iteration commands in sandbox:

   ```bash
   wpilib-agent-tools sandbox run --name tune_shooter -- sim --duration 15
   wpilib-agent-tools sandbox run --name tune_shooter -- query --mode avg --key "Shooter/Velocity"
   ```

3. Generate and review patch:

   ```bash
   wpilib-agent-tools sandbox patch --name tune_shooter --output tune_shooter.diff
   ```

4. Apply reviewed patch to workspace manually.
5. Clean sandbox when finished (unless you need to keep it for more iteration):

   ```bash
   wpilib-agent-tools sandbox clean --name tune_shooter
   ```


## Notes

- `sim` refuses direct workspace execution by default. Use `sandbox run` for normal operation.
- `sim --direct-workspace` is available for advanced/manual workflows.
- `record` requires `pyntcore` and a reachable NT4 server.
