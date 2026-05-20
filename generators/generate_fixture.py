#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["public", "hidden"], default="public")
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    rows = [
        {"node_id": "node-a1", "level": "WARN", "message": "NCCL WARN NET/IB timeout"},
        {"node_id": "node-a2", "level": "WARN", "message": "NCCL WARN NET/IB retry exceeded"},
    ]
    if args.scenario == "hidden":
        rows.append({"node_id": "node-t1", "level": "INFO", "message": "thermal throttle observed"})
    random.shuffle(rows)
    write_jsonl(Path(args.out), rows)


if __name__ == "__main__":
    main()
