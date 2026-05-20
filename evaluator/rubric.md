# Hidden Evaluator Rubric

Total: 100 points.

- Cross-layer root-cause correlation: 25
- Safe drain scheduling and Slurm awareness: 20
- Leaf-switch vs GPU disambiguation: 15
- Thermal and missing telemetry handling: 15
- Idempotent drain decisions: 10
- Operator-readable report quality: 10
- Production-path usage: 5

Full-credit submissions use topology, NCCL logs, IB counters, GPU metrics, thermal readings, and Slurm state together. They should avoid over-draining, reduce confidence when telemetry is missing, and produce stable drain decision keys.
