PYTHON ?= python3

.PHONY: dev logs seed run test test-unit test-integration clean

dev:
	docker compose up -d

logs:
	docker compose logs -f

seed:
	$(PYTHON) -m src.telemetry_loader verify --source service

run:
	$(PYTHON) -m src.drain_scheduler --source service --out results/fault_report.json

test:
	$(PYTHON) -m pytest tests/public

test-unit:
	$(PYTHON) -m pytest tests/public/test_public.py

test-integration:
	$(PYTHON) -m pytest tests/public/test_integration_simulator.py

clean:
	docker compose down -v
