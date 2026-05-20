from __future__ import annotations

import os
import sys
from pathlib import Path


TARGET = os.environ.get("EVAL_TARGET")
if TARGET:
    sys.path.insert(0, str(Path(TARGET).resolve()))

from src.drain_scheduler import plan_drains
from src.fault_engine import classify_faults
from src.telemetry_loader import load_snapshot_from_files


def duplicate_snapshot():
    return {
        "topology": {"nodes": [{"node_id": "node-x1", "rack_id": "rack-x", "leaf_switch": "leaf-x"}]},
        "slurm": {"jobs": []},
        "gpu_metrics": [
            {
                "node_id": "node-x1",
                "gpu_id": "gpu0",
                "ecc_corrected_delta": 900,
                "ecc_uncorrected_delta": 0,
                "mem_temp_c": 76,
                "xid_errors": [],
            }
        ],
        "nccl_logs": [
            {"node_id": "node-x1", "level": "WARN", "message": "NCCL WARN timeout"},
            {"node_id": "node-x1", "level": "WARN", "message": "NCCL WARN retry exceeded"},
        ],
        "ib_counters": [],
        "thermal_readings": [],
    }


def nonpreemptable_snapshot():
    return {
        "topology": {"nodes": [{"node_id": "node-b1", "rack_id": "rack-b", "leaf_switch": "leaf-b"}]},
        "slurm": {
            "jobs": [
                {
                    "job_id": "job-8822",
                    "nodes": ["node-b1"],
                    "state": "RUNNING",
                    "preemptable": False,
                }
            ]
        },
        "gpu_metrics": [
            {
                "node_id": "node-b1",
                "gpu_id": "gpu3",
                "ecc_corrected_delta": 820,
                "ecc_uncorrected_delta": 0,
                "mem_temp_c": 76,
                "xid_errors": [],
            }
        ],
        "nccl_logs": [],
        "ib_counters": [],
        "thermal_readings": [],
    }


def test_public_snapshot_loads_from_files():
    snapshot = load_snapshot_from_files()
    assert snapshot["topology"]["cluster_id"] == "atlas-gpu-lab"
    assert snapshot["gpu_metrics"]
    assert snapshot["nccl_logs"]
    assert snapshot["ib_counters"]


def test_leaf_switch_root_cause_is_detected():
    snapshot = load_snapshot_from_files()
    root_causes = classify_faults(snapshot)
    root_types = {cause["root_cause_type"] for cause in root_causes}
    assert "leaf_switch_degradation" in root_types, (
        "leaf_switch_root_not_detected: NCCL timeouts across leaf-a plus IB errors should be one switch root cause"
    )


def test_leaf_switch_symptoms_do_not_overdrain_nodes():
    snapshot = load_snapshot_from_files()
    root_causes = classify_faults(snapshot)
    decisions = plan_drains(root_causes, snapshot)
    node_drains = [decision for decision in decisions if decision["action"] == "drain_node" and decision["target"] in {"node-a1", "node-a2"}]
    assert len(node_drains) == 0, (
        "bad_leaf_switch_overdrain: switch-level fault should not drain every affected node as independent GPU failures"
    )


def test_nonpreemptable_job_defers_noncritical_drain():
    snapshot = nonpreemptable_snapshot()
    root_causes = classify_faults(snapshot)
    decisions = plan_drains(root_causes, snapshot)
    assert decisions, "expected a decision for the corrected ECC warning"
    assert decisions[0]["timing"] in {"after_job", "scheduled"}, (
        "nonpreemptable_drain_violation: non-critical GPU warning should not immediately drain a non-preemptable job"
    )


def test_drain_decisions_are_idempotent_for_repeated_symptoms():
    snapshot = duplicate_snapshot()
    root_causes = classify_faults(snapshot)
    decisions = plan_drains(root_causes, snapshot)
    decision_keys = [decision["decision_key"] for decision in decisions]
    assert len(decision_keys) == len(set(decision_keys)), (
        "duplicate_drain_decision: repeated symptoms for one target should produce one stable decision"
    )
