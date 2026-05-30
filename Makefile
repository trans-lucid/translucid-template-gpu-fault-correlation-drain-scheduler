PYTHON ?= python3

.PHONY: validate-personalization check-render check-published-repo install validate-solution validate-candidate-main-expected-failure validate-docker-integration render scan-safety validate-rendered-smoke validate clean

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e candidate

validate-solution: install
	CLUSTER_DATA_DIR="$(CURDIR)/candidate/data" EVAL_TARGET="$(CURDIR)/solution" $(PYTHON) -m pytest candidate/tests/public/test_public.py solution/tests evaluator/tests_hidden

validate-candidate-main-expected-failure: install
	bash tools/expect_candidate_failure.sh

validate-docker-integration: install
	bash tools/expect_candidate_docker_failure.sh

render:
	$(PYTHON) tools/render_template.py

scan-safety:
	$(PYTHON) tools/scan_safety.py

check-render:
	$(PYTHON) tools/check_render_contract.py

check-published-repo:
	$(PYTHON) tools/check_published_repo_contract.py --candidate-dir generated/main --solution-dir generated/solution --manifest translucid-template.json

validate-rendered-smoke: render
	bash tools/validate_rendered_smoke.sh

validate-personalization:
	$(PYTHON) tools/validate_personalization.py

validate: validate-solution validate-candidate-main-expected-failure render check-render check-published-repo scan-safety validate-personalization check-published-repo validate-rendered-smoke validate-docker-integration

clean:
	rm -rf generated
	cd candidate && docker compose down -v || true
