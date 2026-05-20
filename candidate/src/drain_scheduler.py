from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .fault_engine import classify_faults
from .telemetry_loader import load_snapshot, post_drain_decisions


def running_jobs_for_node(snapshot: dict[str, Any], node_id: str) -> list[dict[str, Any]]:
    jobs = []
    for job in snapshot.get("slurm", {}).get("jobs", []):
        if job.get("state") == "RUNNING" and node_id in job.get("nodes", []):
            jobs.append(job)
    return jobs


def plan_drains(root_causes: list[dict[str, Any]], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Plan drain actions.

    Starter behavior is intentionally flawed: it drains every node immediately,
    ignores non-preemptable Slurm jobs, and does not de-duplicate decisions.
    """

    decisions: list[dict[str, Any]] = []
    for root_cause in root_causes:
        node = root_cause.get("node_id") or root_cause.get("target")
        decisions.append(
            {
                "decision_key": f"drain:{node}",
                "action": "drain_node",
                "target_type": "node",
                "target": node,
                "timing": "immediate",
                "reason": root_cause["root_cause_type"],
                "root_cause_type": root_cause["root_cause_type"],
                "confidence": root_cause["confidence"],
            }
        )
    return decisions


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
