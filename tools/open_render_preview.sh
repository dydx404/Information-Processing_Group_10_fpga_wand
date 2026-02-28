#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../cloud/backend/brain/tools" && pwd)"
URL="http://127.0.0.1:${PORT}/preview.html"

cd "${ROOT_DIR}"

echo "Serving preview from ${ROOT_DIR} on port ${PORT}"
python3 -m http.server "${PORT}" >/tmp/wand_preview_server.log 2>&1 &
SERVER_PID=$!
trap 'kill "${SERVER_PID}" >/dev/null 2>&1 || true' EXIT

sleep 0.5

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${URL}" >/dev/null 2>&1 || true
elif command -v wslview >/dev/null 2>&1; then
  wslview "${URL}" >/dev/null 2>&1 || true
elif command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Start-Process '${URL}'" >/dev/null 2>&1 || true
fi

echo "Preview URL: ${URL}"
echo "Press Ctrl+C to stop."
wait "${SERVER_PID}"
