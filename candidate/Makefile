PYTHON ?= python3

.PHONY: setup dev logs seed run test test-unit test-integration clean

setup:
	$(PYTHON) -m pip install -e .[test]

dev:
	docker compose up -d

logs:
	docker compose logs -f

seed: setup
	$(PYTHON) -m src.telemetry_loader verify --source service

run: setup
	$(PYTHON) -m src.drain_scheduler --source service --out results/fault_report.json

test: setup
	$(PYTHON) -m pytest tests/public

test-unit: setup
	$(PYTHON) -m pytest tests/public/test_public.py

test-integration: setup
	$(PYTHON) -m pytest tests/public/test_integration_simulator.py

clean:
	docker compose down -v
