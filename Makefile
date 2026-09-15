PY ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
export PYTHONPATH := src

Q ?=
q ?=
QUESTION := $(strip $(or $(Q),$(q)))

DIR ?= $(HOME)/Dokumenty
FOLDER_INDEX ?= data/index-docs

.PHONY: install ingest ask eval serve api easy desktop stop demo-error index-folder ask-folder test clean

install:
	$(PY) -m pip install -r requirements.txt

ingest:
	$(PY) -m rag.cli ingest

index-folder:
	$(PY) -m rag.cli ingest --raw "$(DIR)" --index "$(FOLDER_INDEX)"

ask-folder:
	@if [ -z "$(QUESTION)" ]; then echo 'Usage: make ask-folder Q="your question"'; exit 2; fi
	$(PY) -m rag.cli ask --index "$(FOLDER_INDEX)" --show-context "$(QUESTION)"

ask:
	@if [ -z "$(QUESTION)" ]; then echo 'Usage: make ask Q="your question"'; exit 2; fi
	$(PY) -m rag.cli ask "$(QUESTION)" --show-context

eval:
	$(PY) -m rag.cli eval --judge

serve:
	$(PY) -m rag.cli serve

api:
	$(PY) -m rag.cli api

easy:
	./start.sh

desktop:
	bash scripts/install-desktop.sh

stop:
	-pkill -f "streamlit run app/" || true

demo-error:
	OLLAMA_HOST=http://localhost:9 $(PY) -m streamlit run app/simple_app.py

test:
	$(PY) -m pytest -q

clean:
	rm -rf data/index __pycache__ .pytest_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
