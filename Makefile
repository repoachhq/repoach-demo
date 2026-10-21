REPOACH_REF ?= f8915fc9d4487b5339b816a397c74a40bdfcc5dc
DEMO_MODE ?= replay
PR ?= 1
PYTHON ?= python3

.PHONY: demo demo-live demo-record install-repoach test

demo:
	@DEMO_MODE=$(DEMO_MODE) DEMO_INSTALL_T0=$$(cat /tmp/demo-install-t0 2>/dev/null) $(PYTHON) demo/demo.py

demo-live:
	REPOACH_PROVIDER=$${REPOACH_PROVIDER:-claude_code} repoach review pr $(PR) --dry-run --forge github; \
	repoach review gate $(PR) --forge github

demo-record:
	@command -v asciinema >/dev/null || { echo "demo-record: asciinema is not installed"; exit 2; }
	@command -v agg >/dev/null || { echo "demo-record: agg is not installed"; exit 2; }
	asciinema rec --overwrite -c "make demo" demo/demo.cast
	agg demo/demo.cast demo/demo.gif

install-repoach:
	pipx install "repoach @ git+https://github.com/repoachhq/repoach@$(REPOACH_REF)"

test:
	$(PYTHON) -m pytest -q tests
	cd frontend && npx vitest run
