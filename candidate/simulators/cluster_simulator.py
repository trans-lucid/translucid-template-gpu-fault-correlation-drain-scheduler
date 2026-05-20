from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI


DATA_DIR = Path(os.getenv("CLUSTER_DATA_DIR", "/data"))
app = FastAPI(title="GPU Cluster Simulator")
drain_decisions: list[dict[str, Any]] = []


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/topology")
def topology():
    return read_json(DATA_DIR / "cluster_topology.json")


@app.get("/slurm")
def slurm():
    return read_json(DATA_DIR / "slurm_schedule.json")


@app.get("/telemetry/gpu_metrics")
def gpu_metrics():
    return read_jsonl(DATA_DIR / "telemetry" / "gpu_metrics.jsonl")


@app.get("/telemetry/nccl_logs")
def nccl_logs():
    return read_jsonl(DATA_DIR / "telemetry" / "nccl_logs.jsonl")


@app.get("/telemetry/ib_counters")
def ib_counters():
    return read_jsonl(DATA_DIR / "telemetry" / "ib_counters.jsonl")


@app.get("/telemetry/thermal_readings")
def thermal_readings():
    return read_jsonl(DATA_DIR / "telemetry" / "thermal_readings.jsonl")


@app.get("/drain-decisions")
def get_drain_decisions():
    return {"decisions": drain_decisions}


@app.post("/drain-decisions")
def post_drain_decisions(payload: dict[str, Any]):
    drain_decisions.extend(payload.get("decisions", []))
    return {"stored": len(drain_decisions)}


@app.delete("/drain-decisions")
def clear_drain_decisions():
    drain_decisions.clear()
    return {"stored": 0}
