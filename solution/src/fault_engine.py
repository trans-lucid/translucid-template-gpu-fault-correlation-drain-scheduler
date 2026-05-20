from __future__ import annotations

from collections import defaultdict
from typing import Any

from .topology import nodes_by_rack, nodes_by_switch, rack_for_node, switch_for_node


def _nccl_problem_nodes(snapshot: dict[str, Any]) -> dict[str, int]:
    nodes: dict[str, int] = defaultdict(int)
    for log in snapshot.get("nccl_logs", []):
        message = f"{log.get('level', '')} {log.get('message', '')}".lower()
        if "timeout" in message or "retry exceeded" in message or "below expected" in message:
            nodes[log["node_id"]] += 1
    return dict(nodes)


def _missing_streams(snapshot: dict[str, Any]) -> list[str]:
    streams = ["gpu_metrics", "nccl_logs", "ib_counters", "thermal_readings"]
    return [stream for stream in streams if stream not in snapshot or snapshot.get(stream) in (None, [])]


def classify_faults(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    topology = snapshot.get("topology", {})
    root_causes: list[dict[str, Any]] = []
    explained_nodes: set[str] = set()
    missing = _missing_streams(snapshot)

    nccl_nodes = _nccl_problem_nodes(snapshot)
    switch_nodes = nodes_by_switch(topology)
    for counter in snapshot.get("ib_counters", []) or []:
        switch_id = counter.get("switch_id")
        affected = set(counter.get("nodes") or switch_nodes.get(switch_id, []))
        symptomatic = affected & set(nccl_nodes)
        switch_errors = int(counter.get("symbol_error_delta", 0)) + (1000 * int(counter.get("link_down_delta", 0)))
        if switch_errors >= 500 and len(symptomatic) >= 2:
            confidence = 0.92
            if missing:
                confidence = min(confidence, 0.55)
            root_causes.append(
                {
                    "root_cause_type": "leaf_switch_degradation",
                    "scope": "switch",
                    "target": switch_id,
                    "switch_id": switch_id,
                    "affected_nodes": sorted(symptomatic),
                    "severity": "high",
                    "confidence": confidence,
                    "evidence": [
                        f"ib_error_score={switch_errors}",
                        f"nccl_symptomatic_nodes={','.join(sorted(symptomatic))}",
                    ],
                }
            )
            explained_nodes.update(symptomatic)

    thermal_by_rack: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for reading in snapshot.get("thermal_readings", []) or []:
        if reading.get("thermal_throttle") or int(reading.get("inlet_temp_c", 0)) >= 38:
            thermal_by_rack[reading.get("rack_id") or rack_for_node(topology, reading["node_id"])].append(reading)

    for rack_id, readings in thermal_by_rack.items():
        if len(readings) >= 2:
            root_causes.append(
                {
                    "root_cause_type": "thermal_cooling_fault",
                    "scope": "rack",
                    "target": rack_id,
                    "rack_id": rack_id,
                    "affected_nodes": sorted({reading["node_id"] for reading in readings}),
                    "severity": "high",
                    "confidence": 0.86,
                    "evidence": [f"thermal_nodes={len(readings)}", "thermal_throttle_or_high_inlet"],
                }
            )

    for metric in snapshot.get("gpu_metrics", []) or []:
        node_id = metric["node_id"]
        corrected = int(metric.get("ecc_corrected_delta", 0))
        uncorrected = int(metric.get("ecc_uncorrected_delta", 0))
        xid_errors = metric.get("xid_errors") or []
        if uncorrected > 0 or any(error in [48, 63, 64] for error in xid_errors):
            root_causes.append(
                {
                    "root_cause_type": "gpu_memory_fault",
                    "scope": "gpu",
                    "target": f"{node_id}:{metric['gpu_id']}",
                    "node_id": node_id,
                    "gpu_id": metric["gpu_id"],
                    "severity": "critical",
                    "confidence": 0.94,
                    "evidence": [f"ecc_uncorrected_delta={uncorrected}", f"xid_errors={xid_errors}"],
                }
            )
        elif corrected > 500 and node_id not in explained_nodes:
            root_causes.append(
                {
                    "root_cause_type": "gpu_ecc_warning",
                    "scope": "gpu",
                    "target": f"{node_id}:{metric['gpu_id']}",
                    "node_id": node_id,
                    "gpu_id": metric["gpu_id"],
                    "severity": "medium",
                    "confidence": 0.78,
                    "evidence": [f"ecc_corrected_delta={corrected}"],
                }
            )

    unexplained_nccl = set(nccl_nodes) - explained_nodes
    for node_id in sorted(unexplained_nccl):
        confidence = 0.5 if missing or not snapshot.get("ib_counters") else 0.64
        root_causes.append(
            {
                "root_cause_type": "unknown_interconnect_degradation",
                "scope": "node",
                "target": node_id,
                "node_id": node_id,
                "switch_id": switch_for_node(topology, node_id),
                "severity": "medium",
                "confidence": confidence,
                "evidence": [f"nccl_problem_count={nccl_nodes[node_id]}", f"missing_streams={','.join(missing)}"],
            }
        )

    return root_causes
