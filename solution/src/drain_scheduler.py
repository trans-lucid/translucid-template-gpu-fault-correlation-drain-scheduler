from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .fault_engine import classify_faults
from .telemetry_loader import load_snapshot, post_drain_decisions


def running_jobs_for_node(snapshot: dict[str, Any], node_id: str) -> list[dict[str, Any]]:
    return [
        job
        for job in snapshot.get("slurm", {}).get("jobs", [])
        if job.get("state") == "RUNNING" and node_id in job.get("nodes", [])
    ]


def has_nonpreemptable_job(snapshot: dict[str, Any], node_id: str) -> bool:
    return any(not job.get("preemptable", True) for job in running_jobs_for_node(snapshot, node_id))


def _timing_for_node(root_cause: dict[str, Any], snapshot: dict[str, Any]) -> str:
    node = root_cause.get("node_id")
    if root_cause.get("confidence", 0) < 0.6:
        return "observe"
    if root_cause.get("severity") == "critical":
        return "immediate"
    if node and has_nonpreemptable_job(snapshot, node):
        return "after_job"
    return "scheduled"


def plan_drains(root_causes: list[dict[str, Any]], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    decisions_by_key: dict[str, dict[str, Any]] = {}

    for cause in root_causes:
        cause_type = cause["root_cause_type"]
        confidence = float(cause.get("confidence", 0.0))

        if cause_type == "leaf_switch_degradation":
            key = f"isolate-switch:{cause['target']}"
            decisions_by_key[key] = {
                "decision_key": key,
                "action": "isolate_switch",
                "target_type": "switch",
                "target": cause["target"],
                "timing": "immediate" if confidence >= 0.75 else "observe",
                "reason": "correlated NCCL timeouts and IB counter deltas",
                "root_cause_type": cause_type,
                "confidence": confidence,
            }
        elif cause_type == "thermal_cooling_fault":
            key = f"cooling:{cause['target']}"
            decisions_by_key[key] = {
                "decision_key": key,
                "action": "page_facilities",
                "target_type": "rack",
                "target": cause["target"],
                "timing": "immediate",
                "reason": "thermal cascade across rack",
                "root_cause_type": cause_type,
                "confidence": confidence,
            }
        elif cause_type in {"gpu_memory_fault", "gpu_ecc_warning"}:
            node = cause["node_id"]
            key = f"drain-node:{node}:{cause_type}"
            decisions_by_key[key] = {
                "decision_key": key,
                "action": "drain_node" if confidence >= 0.6 else "observe",
                "target_type": "node",
                "target": node,
                "timing": _timing_for_node(cause, snapshot),
                "reason": f"{cause_type} on {cause.get('gpu_id', 'unknown_gpu')}",
                "root_cause_type": cause_type,
                "confidence": confidence,
            }
        elif cause_type == "unknown_interconnect_degradation":
            key = f"observe:{cause['target']}:unknown-interconnect"
            decisions_by_key[key] = {
                "decision_key": key,
                "action": "observe",
                "target_type": cause.get("scope", "node"),
                "target": cause["target"],
                "timing": "observe",
                "reason": "insufficient telemetry to safely drain",
                "root_cause_type": cause_type,
                "confidence": confidence,
            }

    return list(decisions_by_key.values())


def write_report(report: dict[str, Any], out: str | Path) -> None:
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    summary = output.parent / "summary.md"
    root_types = ", ".join(report["summary"].get("root_cause_types", [])) or "none"
    summary.write_text(
        "\n".join(
            [
                "# GPU Fault Summary",
                "",
                f"Root causes: {root_types}",
                f"Drain decisions: {report['summary']['drain_decision_count']}",
            ]
        )
        + "\n"
    )


def run_pipeline(source: str = "files", out: str | Path = "results/fault_report.json") -> dict[str, Any]:
    snapshot = load_snapshot(source)
    root_causes = classify_faults(snapshot)
    decisions = plan_drains(root_causes, snapshot)
    report = {
        "root_causes": root_causes,
        "drain_decisions": decisions,
        "summary": {
            "root_cause_types": sorted({cause["root_cause_type"] for cause in root_causes}),
            "drain_decision_count": len(decisions),
        },
    }
    write_report(report, out)
    if source == "service":
        post_drain_decisions(decisions)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["files", "service"], default="files")
    parser.add_argument("--out", default="results/fault_report.json")
    args = parser.parse_args()
    report = run_pipeline(args.source, args.out)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
