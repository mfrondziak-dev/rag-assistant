#!/usr/bin/env bash
#
# Convenience wrapper so you can run the CLI from any directory, e.g.:
#   ~/code_projects/rag-assistant/rag.sh ingest --raw ~/Dokumenty --index data/index-docs
#   ~/code_projects/rag-assistant/rag.sh ask --index data/index-docs "o co pytasz?"
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH=src

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  PY="$(command -v python3 || true)"
fi

if [ -z "$PY" ]; then
  echo "Nie znaleziono Pythona / Python not found. Zainstaluj Python 3.10+." >&2
  exit 1
fi

exec "$PY" -m rag.cli "$@"
