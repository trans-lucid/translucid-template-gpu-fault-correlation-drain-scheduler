# GPU Cluster Fault Correlation and Drain Scheduler

This is an internal Translucid challenge template repository. It is not a generated candidate challenge.

The template generates hard ML infrastructure and backend reliability challenges around synthetic GPU cluster telemetry. A generated candidate repo asks the candidate to correlate GPU metrics, NCCL logs, InfiniBand counters, thermal readings, topology, and Slurm jobs to identify true root causes and schedule safe drain actions.

## Template Contents

- `candidate/`: starter repo with public fixtures, Docker simulator, public tests, and intentionally flawed correlation code.
- `solution/`: reference implementation and solution-only notes.
- `evaluator/`: hidden tests, hidden fixtures, rubric, and evaluator scripts.
- `generators/`: deterministic fixture generator and scenario definitions.
- `metadata/`: source mapping rules and safety policy.
- `tools/`: render, safety scan, rendered smoke, and expected-failure validation scripts.
- `source-dossiers/`: source-inspiration notes and reuse boundaries.

## Local Simulator

The candidate path is a local production simulator without real GPUs:

```txt
gpu-cluster-simulator
-> topology, Slurm jobs, GPU metrics, NCCL logs, IB counters, thermal readings
-> telemetry_loader
-> topology model
-> fault_engine
-> drain_scheduler
-> simulator drain-decision endpoint
-> results/fault_report.json and results/summary.md
```

No external credentials, real GPUs, Slurm cluster, NCCL install, or cloud services are required.

## Validation

Run these from the template root:

```bash
make validate-solution
make validate-candidate-main-expected-failure
make render
make scan-safety
make validate-rendered-smoke
make validate-docker-integration
make validate
```

The unsolved starter is expected to fail for stable markers such as `leaf_switch_root_not_detected`, `bad_leaf_switch_overdrain`, `nonpreemptable_drain_violation`, and `duplicate_drain_decision`.
