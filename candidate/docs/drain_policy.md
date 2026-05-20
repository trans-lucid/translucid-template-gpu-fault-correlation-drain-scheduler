# Drain Policy

Drain decisions must be safe for running jobs and idempotent across repeated scheduler runs.

## Timing

- `immediate`: critical hardware fault or fabric isolation action.
- `after_job`: non-critical node issue while a non-preemptable Slurm job is running.
- `scheduled`: non-critical issue without blocking jobs.
- `observe`: insufficient confidence or missing telemetry.

## Slurm Awareness

Do not immediately drain a node running a non-preemptable job unless the root cause is critical.

## Idempotency

Each decision must include a stable `decision_key`. Repeated runs must not produce duplicate decisions for the same target and root cause.
