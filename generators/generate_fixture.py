#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

COUNT_BY_ENTITY = {"low": 3, "medium": 8, "high": 16}


def load_profile(path: str | None) -> dict:
    if not path:
        return {}
    profile_path = Path(path)
    if not profile_path.exists():
        return {}
    return json.loads(profile_path.read_text())


def profile_settings(profile: dict, seed: int, count: int) -> tuple[int, int, str, str]:
    scenario_profile = profile.get("scenario_profile") if isinstance(profile.get("scenario_profile"), dict) else {}
    if profile:
        seed = int(profile.get("generator_seed") or seed)
        count = COUNT_BY_ENTITY.get(str(scenario_profile.get("entity_count", "medium")), count)
    difficulty = str(profile.get("difficulty") or profile.get("difficulty_profile") or "senior").lower()
    failure_modes = str(scenario_profile.get("failure_modes", "multi_step"))
    return seed, count, difficulty, failure_modes


def build_rows(template_slug: str, seed: int, count: int, difficulty: str, failure_modes: str) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    for index in range(count):
        rows.append(
            {
                "case_id": f"{template_slug}-{difficulty}-{index:03d}",
                "difficulty": difficulty,
                "failure_mode": failure_modes,
                "severity": "high" if difficulty == "staff" else "medium" if difficulty == "senior" else "low",
                "entity_id": f"entity_{rng.randint(1000, 9999)}",
                "requires_operator_report": difficulty in {"senior", "staff"},
                "adversarial": difficulty == "staff",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["public", "hidden"], default="public")
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--profile")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    profile = load_profile(args.profile)
    seed, count, difficulty, failure_modes = profile_settings(profile, args.seed, args.count)
    template_slug = profile.get("template_slug") or Path.cwd().name
    rows = build_rows(str(template_slug), seed, count, difficulty, failure_modes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.suffix == ".jsonl":
        args.out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    else:
        args.out.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(rows)} generated personalization cases to {args.out}")


if __name__ == "__main__":
    main()
