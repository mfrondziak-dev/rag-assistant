PY ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
export PYTHONPATH := src

Q ?=
q ?=
QUESTION := $(strip $(or $(Q),$(q)))

.PHONY: install ingest ask eval serve api test clean

install:
	$(PY) -m pip install -r requirements.txt

ingest:
	$(PY) -m rag.cli ingest

ask:
	@if [ -z "$(QUESTION)" ]; then echo 'Usage: make ask Q="your question"'; exit 2; fi
	$(PY) -m rag.cli ask "$(QUESTION)" --show-context

eval:
	$(PY) -m rag.cli eval --judge

serve:
	$(PY) -m rag.cli serve

api:
	$(PY) -m rag.cli api

test:
	$(PY) -m pytest -q

clean:
	rm -rf data/index __pycache__ .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
