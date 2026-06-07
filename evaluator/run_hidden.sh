#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if ! find evaluator/tests_hidden -name 'test_*.py' -print -quit | grep -q .; then
  echo "no hidden tests discovered" >&2
  exit 1
fi
if [ -d "$ROOT/src" ]; then
  TARGET="${EVAL_TARGET:-$ROOT}"
else
  TARGET="${EVAL_TARGET:-$ROOT/solution}"
fi
EVAL_TARGET="$TARGET" python3 -m pytest evaluator/tests_hidden
