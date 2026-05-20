from __future__ import annotations

from src.drain_scheduler import plan_drains
from src.fault_engine import classify_faults


def switch_snapshot():
    return {
        "topology": {
            "nodes": [
                {"node_id": "h100-a1", "rack_id": "rack-a", "leaf_switch": "leaf-z9"},
                {"node_id": "h100-a2", "rack_id": "rack-a", "leaf_switch": "leaf-z9"},
                {"node_id": "h100-b1", "rack_id": "rack-b", "leaf_switch": "leaf-ok"},
            ]
        },
        "slurm": {"jobs": []},
        "gpu_metrics": [
            {"node_id": "h100-a1", "gpu_id": "gpu0", "ecc_corrected_delta": 0, "ecc_uncorrected_delta": 0, "xid_errors": []},
            {"node_id": "h100-a2", "gpu_id": "gpu0", "ecc_corrected_delta": 0, "ecc_uncorrected_delta": 0, "xid_errors": []},
        ],
        "nccl_logs": [
            {"node_id": "h100-a1", "level": "WARN", "message": "NCCL WARN NET/IB timeout"},
            {"node_id": "h100-a2", "level": "WARN", "message": "NCCL WARN NET/IB retry exceeded"},
        ],
        "ib_counters": [
            {"switch_id": "leaf-z9", "symbol_error_delta": 2400, "link_down_delta": 3, "nodes": ["h100-a1", "h100-a2"]}
        ],
        "thermal_readings": [],
    }


def test_one_bad_leaf_switch_is_not_many_gpu_faults():
    snapshot = switch_snapshot()
    causes = classify_faults(snapshot)
    assert [cause["root_cause_type"] for cause in causes].count("leaf_switch_degradation") == 1
    assert not [cause for cause in causes if cause["root_cause_type"] == "gpu_memory_fault"]

    decisions = plan_drains(causes, snapshot)
    assert any(decision["action"] == "isolate_switch" and decision["target"] == "leaf-z9" for decision in decisions)
    node_drains = [decision for decision in decisions if decision["action"] == "drain_node"]
    assert len(node_drains) == 0
