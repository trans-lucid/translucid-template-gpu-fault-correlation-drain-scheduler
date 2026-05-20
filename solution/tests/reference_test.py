from __future__ import annotations

from src.drain_scheduler import plan_drains
from src.fault_engine import classify_faults


def public_like_snapshot():
    return {
        "topology": {
            "nodes": [
                {"node_id": "node-a1", "rack_id": "rack-a", "leaf_switch": "leaf-a"},
                {"node_id": "node-a2", "rack_id": "rack-a", "leaf_switch": "leaf-a"},
                {"node_id": "node-b1", "rack_id": "rack-b", "leaf_switch": "leaf-b"},
            ]
        },
        "slurm": {"jobs": [{"job_id": "job-1", "nodes": ["node-b1"], "state": "RUNNING", "preemptable": False}]},
        "gpu_metrics": [
            {"node_id": "node-b1", "gpu_id": "gpu3", "ecc_corrected_delta": 820, "ecc_uncorrected_delta": 0, "xid_errors": []}
        ],
        "nccl_logs": [
            {"node_id": "node-a1", "level": "WARN", "message": "NCCL WARN timeout"},
            {"node_id": "node-a2", "level": "WARN", "message": "NCCL WARN retry exceeded"},
        ],
        "ib_counters": [
            {"switch_id": "leaf-a", "symbol_error_delta": 1800, "link_down_delta": 1, "nodes": ["node-a1", "node-a2"]}
        ],
        "thermal_readings": [],
    }


def test_reference_detects_switch_and_ecc_without_overdrain():
    snapshot = public_like_snapshot()
    causes = classify_faults(snapshot)
    types = {cause["root_cause_type"] for cause in causes}
    assert "leaf_switch_degradation" in types
    assert "gpu_ecc_warning" in types
    decisions = plan_drains(causes, snapshot)
    assert any(decision["action"] == "isolate_switch" for decision in decisions)
    assert not [decision for decision in decisions if decision["target"] in {"node-a1", "node-a2"} and decision["action"] == "drain_node"]
    assert any(decision["target"] == "node-b1" and decision["timing"] == "after_job" for decision in decisions)
