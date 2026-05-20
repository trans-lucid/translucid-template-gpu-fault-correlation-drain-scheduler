from __future__ import annotations

from src.drain_scheduler import plan_drains


def test_repeated_root_causes_do_not_duplicate_drain_decisions():
    snapshot = {
        "slurm": {"jobs": []},
    }
    repeated = [
        {
            "root_cause_type": "gpu_memory_fault",
            "scope": "gpu",
            "target": "node-z1:gpu0",
            "node_id": "node-z1",
            "gpu_id": "gpu0",
            "severity": "critical",
            "confidence": 0.94,
            "evidence": ["xid=48"],
        },
        {
            "root_cause_type": "gpu_memory_fault",
            "scope": "gpu",
            "target": "node-z1:gpu0",
            "node_id": "node-z1",
            "gpu_id": "gpu0",
            "severity": "critical",
            "confidence": 0.94,
            "evidence": ["ecc_uncorrected_delta=2"],
        },
    ]
    decisions = plan_drains(repeated, snapshot)
    keys = [decision["decision_key"] for decision in decisions]
    assert len(keys) == 1
    assert keys == list(set(keys))
