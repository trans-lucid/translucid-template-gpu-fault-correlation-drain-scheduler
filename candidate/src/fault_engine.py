from __future__ import annotations

from collections import defaultdict
from typing import Any


def classify_faults(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Classify root causes from cluster telemetry.

    Starter behavior is intentionally flawed: it treats NCCL network symptoms as
    node-local GPU faults, mislabels thermal throttling as memory failure, and
    ignores InfiniBand switch correlation.
    """

    root_causes: list[dict[str, Any]] = []

    for metric in snapshot.get("gpu_metrics", []):
        corrected = int(metric.get("ecc_corrected_delta", 0))
        uncorrected = int(metric.get("ecc_uncorrected_delta", 0))
        if uncorrected > 0 or corrected > 500:
            root_causes.append(
                {
                    "root_cause_type": "gpu_memory_fault",
                    "scope": "gpu",
                    "target": f"{metric['node_id']}:{metric['gpu_id']}",
                    "node_id": metric["node_id"],
                    "gpu_id": metric["gpu_id"],
                    "severity": "critical" if uncorrected > 0 else "medium",
                    "confidence": 0.91,
                    "evidence": [f"ecc_corrected_delta={corrected}", f"ecc_uncorrected_delta={uncorrected}"],
                }
            )

    for reading in snapshot.get("thermal_readings", []):
        if reading.get("thermal_throttle") or int(reading.get("inlet_temp_c", 0)) >= 38:
            root_causes.append(
                {
                    "root_cause_type": "gpu_memory_fault",
                    "scope": "node",
                    "target": reading["node_id"],
                    "node_id": reading["node_id"],
                    "severity": "high",
                    "confidence": 0.84,
                    "evidence": [f"inlet_temp_c={reading.get('inlet_temp_c')}"],
                }
            )

    nccl_nodes: dict[str, int] = defaultdict(int)
    for log in snapshot.get("nccl_logs", []):
        message = f"{log.get('level', '')} {log.get('message', '')}".lower()
        if "timeout" in message or "retry exceeded" in message:
            nccl_nodes[log["node_id"]] += 1

    for node_id, count in nccl_nodes.items():
        root_causes.append(
            {
                "root_cause_type": "node_gpu_fault",
                "scope": "node",
                "target": node_id,
                "node_id": node_id,
                "severity": "high",
                "confidence": 0.76,
                "evidence": [f"nccl_timeout_count={count}"],
            }
        )

    return root_causes
