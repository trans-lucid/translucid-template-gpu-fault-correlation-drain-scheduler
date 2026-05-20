from __future__ import annotations

from src.drain_scheduler import plan_drains
from src.fault_engine import classify_faults


def test_thermal_cascade_is_not_classified_as_memory_failure():
    snapshot = {
        "topology": {
            "nodes": [
                {"node_id": "node-t1", "rack_id": "rack-hot", "leaf_switch": "leaf-h"},
                {"node_id": "node-t2", "rack_id": "rack-hot", "leaf_switch": "leaf-h"},
            ]
        },
        "slurm": {"jobs": []},
        "gpu_metrics": [
            {"node_id": "node-t1", "gpu_id": "gpu0", "ecc_corrected_delta": 0, "ecc_uncorrected_delta": 0, "xid_errors": []},
            {"node_id": "node-t2", "gpu_id": "gpu1", "ecc_corrected_delta": 0, "ecc_uncorrected_delta": 0, "xid_errors": []},
        ],
        "nccl_logs": [],
        "ib_counters": [],
        "thermal_readings": [
            {"node_id": "node-t1", "rack_id": "rack-hot", "inlet_temp_c": 39, "thermal_throttle": True},
            {"node_id": "node-t2", "rack_id": "rack-hot", "inlet_temp_c": 40, "thermal_throttle": True},
        ],
    }
    causes = classify_faults(snapshot)
    assert any(cause["root_cause_type"] == "thermal_cooling_fault" for cause in causes)
    assert not any(cause["root_cause_type"] == "gpu_memory_fault" for cause in causes)
    decisions = plan_drains(causes, snapshot)
    assert any(decision["action"] == "page_facilities" for decision in decisions)


def test_missing_ib_telemetry_reduces_confidence_and_observes():
    snapshot = {
        "topology": {"nodes": [{"node_id": "node-m1", "rack_id": "rack-m", "leaf_switch": "leaf-m"}]},
        "slurm": {"jobs": []},
        "gpu_metrics": [],
        "nccl_logs": [{"node_id": "node-m1", "level": "WARN", "message": "NCCL WARN timeout"}],
        "ib_counters": [],
        "thermal_readings": [],
    }
    causes = classify_faults(snapshot)
    assert causes
    assert all(cause["confidence"] <= 0.55 for cause in causes)
    decisions = plan_drains(causes, snapshot)
    assert all(decision["timing"] == "observe" for decision in decisions)


def test_nonpreemptable_job_changes_noncritical_drain_timing():
    snapshot = {
        "topology": {"nodes": [{"node_id": "node-s1", "rack_id": "rack-s", "leaf_switch": "leaf-s"}]},
        "slurm": {
            "jobs": [{"job_id": "job-np", "nodes": ["node-s1"], "state": "RUNNING", "preemptable": False}]
        },
        "gpu_metrics": [
            {"node_id": "node-s1", "gpu_id": "gpu2", "ecc_corrected_delta": 900, "ecc_uncorrected_delta": 0, "xid_errors": []}
        ],
        "nccl_logs": [],
        "ib_counters": [],
        "thermal_readings": [],
    }
    causes = classify_faults(snapshot)
    decisions = plan_drains(causes, snapshot)
    assert decisions[0]["timing"] == "after_job"
