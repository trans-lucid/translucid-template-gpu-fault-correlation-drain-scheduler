#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/candidate"

set +e
python3 -m pytest tests/public/test_public.py 2>&1 | tee /tmp/gpu-fault-unit-output.txt
status=${PIPESTATUS[0]}
set -e

if [ "$status" -eq 0 ]; then
  echo "candidate starter unexpectedly passed public unit tests"
  exit 1
fi

for expected in leaf_switch_root_not_detected bad_leaf_switch_overdrain nonpreemptable_drain_violation duplicate_drain_decision; do
  if ! grep -q "$expected" /tmp/gpu-fault-unit-output.txt; then
    echo "public unit tests did not fail for expected reason: $expected"
    exit 1
  fi
done

echo "candidate starter failed public unit tests as expected"
