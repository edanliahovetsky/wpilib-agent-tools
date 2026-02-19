# Tuning Tips

## Recorder Timing

Simulation startup and NT4 availability are not instantaneous.

Practical baseline:

- `--duration 30`
- `--record-delay 3`

Why:

- Gives startup headroom for simulator and NT4 server.
- Still captures early autonomous transitions.

## Delay Tradeoffs

- Lower `record-delay` captures earlier state transitions.
- Higher `record-delay` can avoid early noise but may miss short paths.

Example learned behavior:

- `record-delay 8` captured only post-path `IDLE` in one run.
- `record-delay 3` captured `FOLLOW_PATH -> IDLE` in the same repo.

## Validation Signal Priority

Use telemetry as source of truth:

1. DS mode values
2. autonomous state sequence
3. log generation success

Use process exit as secondary context only.
