# GPU Cluster Fault Correlation and Drain Scheduler

You are on call for a synthetic GPU training cluster. A distributed training run is showing NCCL timeouts, degraded bandwidth, and node health alerts. The current fault pipeline over-drains nodes and misses cross-layer root causes.

Your task is to repair the fault correlation and drain scheduler so the system can identify true root causes and produce safe operator-facing actions.

## What To Edit

- `src/telemetry_loader.py`
- `src/topology.py`
- `src/fault_engine.py`
- `src/drain_scheduler.py`

## Commands

```bash
make setup
make dev
make seed
make test
make test-integration
make run
make clean
```

`make dev` starts the local simulator. `make seed` verifies simulator readiness and clears prior drain decisions. `make run` writes `results/fault_report.json` and `results/summary.md`.
