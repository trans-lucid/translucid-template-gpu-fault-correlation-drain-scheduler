from __future__ import annotations

import requests

from src.drain_scheduler import run_pipeline


def test_docker_simulator_path_exercises_http_telemetry_and_drain_endpoint():
    requests.delete("http://localhost:8090/drain-decisions", timeout=5).raise_for_status()
    report = run_pipeline(source="service", out="results/fault_report.json")

    root_types = set(report["summary"]["root_cause_types"])
    assert "leaf_switch_degradation" in root_types, (
        "leaf_switch_root_not_detected: Docker simulator telemetry should identify leaf-a as the root cause"
    )

    node_drains = [
        decision
        for decision in report["drain_decisions"]
        if decision["action"] == "drain_node" and decision["target"] in {"node-a1", "node-a2"}
    ]
    assert not node_drains, (
        "bad_leaf_switch_overdrain: Docker simulator path should not drain both leaf-a nodes"
    )

    stored = requests.get("http://localhost:8090/drain-decisions", timeout=5).json()["decisions"]
    assert stored, "simulator_drain_endpoint_not_used: decisions must be posted through the local service"
