from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import requests


DEFAULT_DATA_DIR = Path(os.getenv("CLUSTER_DATA_DIR", "data"))
DEFAULT_SIM_URL = os.getenv("CLUSTER_SIM_URL", "http://localhost:8090")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def load_snapshot_from_files(data_dir: str | Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    base = Path(data_dir)
    return {
        "topology": read_json(base / "cluster_topology.json"),
        "slurm": read_json(base / "slurm_schedule.json"),
        "gpu_metrics": read_jsonl(base / "telemetry" / "gpu_metrics.jsonl"),
        "nccl_logs": read_jsonl(base / "telemetry" / "nccl_logs.jsonl"),
        "ib_counters": read_jsonl(base / "telemetry" / "ib_counters.jsonl"),
        "thermal_readings": read_jsonl(base / "telemetry" / "thermal_readings.jsonl"),
    }


def _get_json(base_url: str, path: str, retries: int = 30) -> Any:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - integration retry path
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"cluster simulator did not become ready for {path}: {last_error}")


def load_snapshot_from_service(base_url: str = DEFAULT_SIM_URL) -> dict[str, Any]:
    return {
        "topology": _get_json(base_url, "/topology"),
        "slurm": _get_json(base_url, "/slurm"),
        "gpu_metrics": _get_json(base_url, "/telemetry/gpu_metrics"),
        "nccl_logs": _get_json(base_url, "/telemetry/nccl_logs"),
        "ib_counters": _get_json(base_url, "/telemetry/ib_counters"),
        "thermal_readings": _get_json(base_url, "/telemetry/thermal_readings"),
    }


def reset_simulator(base_url: str = DEFAULT_SIM_URL) -> None:
    for _ in range(30):
        try:
            response = requests.delete(f"{base_url}/drain-decisions", timeout=5)
            response.raise_for_status()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("cluster simulator did not become ready for reset")


def post_drain_decisions(decisions: list[dict[str, Any]], base_url: str = DEFAULT_SIM_URL) -> None:
    response = requests.post(f"{base_url}/drain-decisions", json={"decisions": decisions}, timeout=10)
    response.raise_for_status()


def load_snapshot(source: str = "files") -> dict[str, Any]:
    if source == "service":
        return load_snapshot_from_service()
    return load_snapshot_from_files()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify"])
    parser.add_argument("--source", choices=["files", "service"], default="files")
    args = parser.parse_args()

    if args.source == "service":
        snapshot = load_snapshot_from_service()
        reset_simulator()
    else:
        snapshot = load_snapshot_from_files()
    print(json.dumps({"ok": True, "nodes": len(snapshot["topology"]["nodes"])}))


if __name__ == "__main__":
    main()
