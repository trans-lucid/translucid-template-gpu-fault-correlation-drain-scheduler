# Source Dossier: GPU Fault Correlation and Drain Scheduler

This dossier records architectural inspiration and reuse boundaries for the template.

## Sources Studied

- NVIDIA NCCL tests: distributed collective test vocabulary, all-reduce performance concepts, ranks, threads, GPUs per process, and bandwidth terminology.
  Source: https://github.com/NVIDIA/nccl-tests
- CoreWeave NCCL tests: Slurm-oriented distributed NCCL job examples, job logs, and operator workflow shape.
  Source: https://github.com/coreweave/nccl-tests
- NVIDIA DeepOps Slurm validation docs: validation playbook concepts, Pyxis/Enroot/NCCL test orchestration, and cluster health-check flow.
  Source: https://github.com/NVIDIA/deepops/blob/master/docs/slurm-cluster/README.md
- NVIDIA NCCL troubleshooting docs: failure ambiguity across GPU, network, container, VM, BIOS, and topology configuration layers.
  Source: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html
- NVIDIA/DCGM exporter family: GPU monitoring concepts such as temperatures, utilization, power, ECC-style health, and exporter-shaped metrics.

## Allowed Reuse

- Architecture ideas.
- Generic terminology such as NCCL ranks, all-reduce, bus bandwidth, Slurm jobs, and InfiniBand counters.
- Synthetic metric names inspired by common GPU telemetry.
- Local simulator pattern.
- Operator workflow concepts.

## Forbidden

- Copying source code from public repos.
- Copying exact logs, job scripts, or datasets wholesale.
- Requiring real GPUs, CUDA, NCCL, Slurm, Pyxis, Enroot, cloud services, or credentials.
- Copying private customer code or production telemetry.
- Embedding real cluster names, tenant data, customer incidents, or secrets.

All code and fixtures in this template are Translucid-owned synthetic material.
