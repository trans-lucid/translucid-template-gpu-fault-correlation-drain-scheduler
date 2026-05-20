# Failure Modes Reference

Use this as background context only. The telemetry and tests define the contract.

## GPU Memory Fault

Signals:
- uncorrectable ECC on one GPU
- repeated XID memory errors on the same GPU
- localized failures on one node

Expected action:
- drain or quarantine the affected GPU/node
- prefer immediate action for uncorrectable ECC

## Leaf Switch Degradation

Signals:
- NCCL timeouts across multiple nodes under the same leaf switch
- InfiniBand symbol or link error deltas on that leaf
- no matching GPU-local ECC pattern

Expected action:
- isolate or page networking for the switch
- do not drain every affected GPU as if each node is independently bad

## Thermal Cooling Fault

Signals:
- high inlet/ambient temperatures across a chassis or rack
- thermal throttle flags
- no matching ECC/XID memory pattern

Expected action:
- page facilities or reduce workload pressure
- do not classify as GPU memory failure

## Missing Telemetry

Missing streams should reduce confidence and produce conservative actions. It should not create fake certainty.
