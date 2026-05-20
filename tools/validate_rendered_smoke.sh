#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -d "$ROOT/generated/main" ] || [ ! -d "$ROOT/generated/solution" ]; then
  echo "rendered repos missing; run make render first"
  exit 1
fi

cd "$ROOT/generated/main"
python3 -m pip install -e . >/tmp/gpu-render-main-install.txt
set +e
python3 -m pytest tests/public/test_public.py 2>&1 | tee /tmp/gpu-render-main-public.txt
main_status=${PIPESTATUS[0]}
set -e
if [ "$main_status" -eq 0 ]; then
  echo "rendered candidate main unexpectedly passed public unit tests"
  exit 1
fi
if ! grep -q "leaf_switch_root_not_detected" /tmp/gpu-render-main-public.txt; then
  echo "rendered candidate main failed without expected marker"
  exit 1
fi

cd "$ROOT/generated/solution"
python3 -m pip install -e . >/tmp/gpu-render-solution-install.txt
CLUSTER_DATA_DIR="$PWD/data" EVAL_TARGET="$PWD/solution" python3 -m pytest tests/public/test_public.py evaluator/tests_hidden

echo "rendered repo smoke test passed"
