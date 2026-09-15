#!/usr/bin/env bash
#
# One-command launcher for the friendly "Ask your documents" app.
# Creates the environment, checks Ollama and the models, then opens the app.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8501}"
OLLAMA_URL="http://localhost:11434"
MODELS=("nomic-embed-text" "llama3.1")

say() { printf '\033[1;36m%s\033[0m\n' "$1"; }
ok()  { printf '\033[1;32m  ✓ %s\033[0m\n' "$1"; }
err() { printf '\033[1;31m  ✗ %s\033[0m\n' "$1" >&2; }

say "Asystent dokumentów / Document assistant"
echo

if ! command -v python3 >/dev/null 2>&1; then
  err "Brak Pythona 3. Zainstaluj Python 3.10+ i uruchom ponownie. / Install Python 3.10+ and retry."
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  say "Pierwsze uruchomienie: tworzę środowisko i instaluję zależności (kilka minut)…"
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip >/dev/null
  .venv/bin/python -m pip install -r requirements.txt
fi
ok "Środowisko gotowe / Environment ready"

if ! command -v ollama >/dev/null 2>&1; then
  err "Nie znaleziono Ollamy. Zainstaluj ją z https://ollama.com/download i uruchom ponownie."
  err "Ollama not found. Install it from https://ollama.com/download and retry."
  exit 1
fi

if ! curl -s -m 3 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
  say "Uruchamiam Ollamę w tle / Starting Ollama in the background…"
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  for _ in $(seq 1 30); do
    curl -s -m 2 "$OLLAMA_URL/api/tags" >/dev/null 2>&1 && break
    sleep 1
  done
fi

if curl -s -m 3 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
  ok "Ollama działa / Ollama is running"
else
  err "Nie udało się uruchomić Ollamy. Spróbuj ręcznie: ollama serve"
  exit 1
fi

for model in "${MODELS[@]}"; do
  if ollama list 2>/dev/null | awk '{print $1}' | grep -q "^${model}"; then
    ok "Model ${model} dostępny / available"
  else
    say "Pobieram model ${model} (jednorazowo) / Downloading ${model} (one time)…"
    ollama pull "$model"
  fi
done

URL_PORT="$PORT"
free_port="$(.venv/bin/python - "$PORT" <<'PY'
import socket, sys
start = int(sys.argv[1])
for candidate in range(start, start + 20):
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", candidate))
        except OSError:
            continue
        print(candidate)
        break
else:
    print(start)
PY
)"
if [ "$free_port" != "$PORT" ]; then
  say "Port ${PORT} zajęty — używam ${free_port} / Port ${PORT} busy, using ${free_port}"
  PORT="$free_port"
fi

URL="http://localhost:${PORT}"
say "Uruchamiam aplikację / Starting the app: ${URL}"
(
  sleep 6
  xdg-open "$URL" >/dev/null 2>&1 || python3 -m webbrowser "$URL" >/dev/null 2>&1 || true
) &

export PYTHONPATH=src
exec .venv/bin/python -m streamlit run app/simple_app.py \
  --server.port "$PORT" \
  --server.headless true \
  --browser.gatherUsageStats false
