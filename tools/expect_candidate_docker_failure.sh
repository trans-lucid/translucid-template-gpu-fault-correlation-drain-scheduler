#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/candidate"

docker compose config >/tmp/gpu-fault-compose-config.txt
docker compose up -d

cleanup() {
  docker compose down -v
}
trap cleanup EXIT

make seed

set +e
python3 -m pytest tests/public/test_integration_simulator.py 2>&1 | tee /tmp/gpu-fault-integration-output.txt
status=${PIPESTATUS[0]}
set -e

if [ "$status" -eq 0 ]; then
  echo "candidate starter unexpectedly passed the Docker-backed public integration test"
  exit 1
fi

if ! grep -q "test_docker_simulator_path_exercises_http_telemetry_and_drain_endpoint" /tmp/gpu-fault-integration-output.txt; then
  echo "Docker-backed public integration test did not run"
  exit 1
fi

found=0
for expected in leaf_switch_root_not_detected bad_leaf_switch_overdrain simulator_drain_endpoint_not_used; do
  if grep -q "$expected" /tmp/gpu-fault-integration-output.txt; then
    found=1
  fi
done

if [ "$found" -ne 1 ]; then
  echo "Docker-backed public integration test failed for an unexpected reason"
  exit 1
fi

echo "candidate starter failed Docker-backed public integration test as expected"
