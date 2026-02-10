# WPILib Agent Tools Validation Runbook

This runbook validates `wpilib-agent-tools` against a real WPILib workspace.

## Target Repositories

- Tool repo: `/Users/edan/FRC/wpilib-agent-tools`
- Reference repo: `/Users/edan/FRC/2026-robot-code` (run on `dev`)

## Preflight

1. Ensure reference repo is on `dev`.
2. Ensure Java 17 and WPILib 2026 are installed.
3. Create/install tool environment:

```bash
cd /Users/edan/FRC/wpilib-agent-tools/agent
python3.12 -m venv /tmp/wpilib-agent-tools-venv312
/tmp/wpilib-agent-tools-venv312/bin/python -m pip install -e . --no-deps
/tmp/wpilib-agent-tools-venv312/bin/python -m pip install robotpy-wpiutil pyntcore numpy matplotlib
```

4. Before each command run, enforce single-instance execution:

```bash
/Users/edan/FRC/wpilib-agent-tools/agent/scripts/cleanup_instances.sh
```

## Sandbox Lifecycle Matrix

```bash
cd /Users/edan/FRC/2026-robot-code
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox clean --all --force --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox create --name val-workspace --source workspace --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox create --name val-branch --source branch:dev --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox create --name val-rev --source rev:$(git rev-parse HEAD) --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox list --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox status --name val-workspace --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-branch --json -- /bin/sh -lc "echo ok"
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox clean --name val-rev --json
```

Patch validation:

```bash
printf "\n// sandbox-patch-validation\n" >> /Users/edan/.wpilib-agent-tools/sandboxes/val-workspace/src/main/java/frc/robot/RobotContainer.java
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox patch --name val-workspace --output /Users/edan/FRC/2026-robot-code/agent/reports/val-workspace.patch --json
```

## Sim Validation

Guardrail:

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sim --duration 1
```

Expected: non-zero exit and refusal to run directly in workspace.

Direct workspace override:

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sim --direct-workspace --duration 1 --gradle-task tasks --no-analyze --json
```

Sandbox sim:

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- sim --duration 10 --json
```

## Logs / Keys / Query / Graph / View Validation

Create deterministic fixture in sandbox:

```bash
python3 -c "import json; from pathlib import Path; p=Path('/Users/edan/.wpilib-agent-tools/sandboxes/val-workspace/agent/logs/test_deterministic.json'); p.parent.mkdir(parents=True, exist_ok=True); payload={'source':'fixture','address':'local','duration_sec':3.0,'entries':{'Shooter/Velocity':{'type':'double','data':[[0.0,0.0],[1.0,1000.0],[2.0,1500.0],[3.0,1200.0]]},'DriverStation/Enabled':{'type':'boolean','data':[[0.0,False],[1.5,True]]},'DriverStation/Autonomous':{'type':'boolean','data':[[0.0,True],[2.5,False]]},'DriverStation/Test':{'type':'boolean','data':[[0.0,False]]},'DriverStation/AllianceStation':{'type':'string','data':[[0.0,'Blue1']]},'DriverStation/MatchTime':{'type':'double','data':[[0.0,15.0],[1.0,14.0],[2.0,13.0]]}}}; p.write_text(json.dumps(payload, indent=2), encoding='utf-8')"
```

Validate commands:

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- logs --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- keys --file agent/logs/test_deterministic.json --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode timestamps --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode values --limit 3 --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode avg --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode minmax --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode deriv --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --key Shooter/Velocity --mode integral --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- query --file agent/logs/test_deterministic.json --mode ds --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- graph --file agent/logs/test_deterministic.json --key Shooter/Velocity --key DriverStation/MatchTime --mode values --output val_values.png --json
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools sandbox run --name val-workspace --json -- view --file agent/logs/test_deterministic.json
```

## Record Validation

Reachable local publisher:

```bash
/tmp/wpilib-agent-tools-venv312/bin/python -c "import ntcore,time; inst=ntcore.NetworkTableInstance.getDefault(); inst.startServer(); pub=inst.getDoubleTopic('/Debug/Value').publish(); t0=time.time(); i=0; \
while time.time()-t0<10: pub.set(float(i)); i+=1; time.sleep(0.05)" &
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools record --address localhost --duration 3 --json
```

Unreachable endpoint:

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools record --address 192.0.2.1 --duration 2 --json
```

Expected: non-zero exit with clear connection failure message.

## Wrapper Script Parity

```bash
WPILIB_AGENT_TOOLS_CLI=/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools /Users/edan/FRC/wpilib-agent-tools/agent/scripts/sandbox_lifecycle.sh create --name script-val --source workspace --force --json
WPILIB_AGENT_TOOLS_CLI=/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools /Users/edan/FRC/wpilib-agent-tools/agent/scripts/sandbox_lifecycle.sh list --json
WPILIB_AGENT_TOOLS_CLI=/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools /Users/edan/FRC/wpilib-agent-tools/agent/scripts/sandbox_lifecycle.sh delete --name script-val --json
WPILIB_AGENT_TOOLS_CLI=/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools /Users/edan/FRC/wpilib-agent-tools/agent/scripts/sandbox_lifecycle.sh clean --all --json
```

## Rules Command Validation

```bash
/tmp/wpilib-agent-tools-venv312/bin/wpilib-agent-tools rules install --mode both --target custom --output-dir /tmp/wpilib-agent-tools-rules --force --json
```

## Acceptance Gates

- Sandbox lifecycle commands pass for workspace/branch/rev sources.
- `sim` enforces workspace guardrail and runs via sandbox.
- `logs`, `keys`, `query`, `graph`, `view` complete successfully on deterministic fixture.
- `record` captures data on reachable NT server and fails clearly on unreachable server.
- Wrapper script behavior matches direct CLI semantics.
- `rules install` writes expected files in selected mode/target.
