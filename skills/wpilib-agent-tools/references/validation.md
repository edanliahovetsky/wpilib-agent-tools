# Validation

## Goal

Produce a deterministic pass/fail result for simulation and autonomous/path behavior using CLI evidence.

## Script

Primary entrypoint:

```bash
scripts/validate_robot_repo.sh --repo <path> [options]
```

Important options:

- `--profile generic|2026-robot-code`
- `--branch <name>`
- `--duration <seconds>`
- `--record-delay <seconds>`
- `--state-key <log-key>`
- `--expected-states CSV` (ordered subsequence check)
- `--keep-sandbox`
- `--keep-sandbox-on-fail`

## Evaluation Logic

The validator reports pass when all required checks are true:

1. Sim produced a log (`log_generation.passed=true`).
2. Optional DS check (`--check-ds`) shows `Enabled=true` and `Autonomous=true`.
3. Optional state-sequence check confirms ordered appearance of expected states.

Exit code:

- `0`: passed
- `1`: failed

## Notes On Sim Exit Code

Bounded sim runs intentionally terminate the gradle process. In CLI output, `exit_code` is normalized to success while `exit_code_raw` may still be `143`.

## Troubleshooting

- If DS keys are missing, verify DS auto-enable logic in target repo startup path.
- If state transitions are missing, lower `--record-delay` and re-run.
- If recorder fails to connect, increase duration and adjust delay/address.
