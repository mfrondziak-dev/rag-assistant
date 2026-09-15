#!/usr/bin/env bash
#
# Adds "Ask your documents" to the desktop application menu so the app can be
# started with a click, without using the terminal.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
START_SCRIPT="$SCRIPT_DIR/start.sh"
APPS_DIR="$HOME/.local/share/applications"
ENTRY="$APPS_DIR/rag-assistant.desktop"

mkdir -p "$APPS_DIR"
chmod +x "$START_SCRIPT"

cat > "$ENTRY" <<EOF
[Desktop Entry]
Type=Application
Name=Zapytaj swoje dokumenty
Name[en]=Ask your documents
Comment=Lokalny asystent dokumentów (RAG, Ollama)
Comment[en]=Local document assistant (RAG, Ollama)
Exec=bash "$START_SCRIPT"
Terminal=true
Categories=Utility;Office;
Keywords=rag;documents;ollama;ai;
EOF

chmod +x "$ENTRY"
update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
echo "  ✓ Dodano wpis w menu aplikacji: Zapytaj swoje dokumenty"

if [ -d "$HOME/Desktop" ] && [ "${1:-}" != "--menu-only" ]; then
  cp "$ENTRY" "$HOME/Desktop/rag-assistant.desktop"
  chmod +x "$HOME/Desktop/rag-assistant.desktop"
  gio set "$HOME/Desktop/rag-assistant.desktop" metadata::trusted true >/dev/null 2>&1 || true
  echo "  ✓ Dodano skrót na pulpicie: rag-assistant.desktop"
fi

echo "  ℹ Uruchom aplikację z menu systemowego albo klikając skrót na pulpicie."
