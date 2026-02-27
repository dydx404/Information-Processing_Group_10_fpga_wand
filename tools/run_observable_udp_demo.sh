#!/usr/bin/env bash
set -euo pipefail

# Opens live preview page and runs UDP TX test so rendering is observable.
# Backend (Wand-Brain API) must already be running.

API_HOST="${API_HOST:-16.16.202.231}"
API_PORT="${API_PORT:-8000}"
UDP_HOST="${UDP_HOST:-16.16.202.231}"
UDP_PORT="${UDP_PORT:-41000}"
WAND_ID="${WAND_ID:-1}"
DEVICE_ID="${DEVICE_ID:-1}"

PREVIEW_PORT="${PREVIEW_PORT:-8010}"
RATES="${RATES:-25,50,100}"
DURATION="${DURATION:-12}"
REPEAT="${REPEAT:-3}"
PATTERN="${PATTERN:-circle}"
STROKE_START="${STROKE_START:-1000}"

usage() {
  cat <<EOF
Usage: tools/run_observable_udp_demo.sh [options]

Options:
  --api-host <host>         API host for preview image (default: ${API_HOST})
  --api-port <port>         API port (default: ${API_PORT})
  --udp-host <host>         UDP TX host (default: ${UDP_HOST})
  --udp-port <port>         UDP TX port (default: ${UDP_PORT})
  --wand <id>               wand_id (default: ${WAND_ID})
  --device <id>             device_number (default: ${DEVICE_ID})
  --preview-port <port>     local static preview port (default: ${PREVIEW_PORT})
  --rates <csv>             TX rates (default: ${RATES})
  --duration <sec>          duration per rate (default: ${DURATION})
  --repeat <n>              number of sweep repeats (default: ${REPEAT})
  --pattern <line|circle>   trajectory pattern (default: ${PATTERN})
  --stroke-start <id>       initial stroke_id (default: ${STROKE_START})
  -h, --help                show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-host) API_HOST="${2:-}"; shift 2 ;;
    --api-port) API_PORT="${2:-}"; shift 2 ;;
    --udp-host) UDP_HOST="${2:-}"; shift 2 ;;
    --udp-port) UDP_PORT="${2:-}"; shift 2 ;;
    --wand) WAND_ID="${2:-}"; shift 2 ;;
    --device) DEVICE_ID="${2:-}"; shift 2 ;;
    --preview-port) PREVIEW_PORT="${2:-}"; shift 2 ;;
    --rates) RATES="${2:-}"; shift 2 ;;
    --duration) DURATION="${2:-}"; shift 2 ;;
    --repeat) REPEAT="${2:-}"; shift 2 ;;
    --pattern) PATTERN="${2:-}"; shift 2 ;;
    --stroke-start) STROKE_START="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PREVIEW_DIR="${REPO_ROOT}/cloud/backend/brain/tools"
TX_SCRIPT="${REPO_ROOT}/tools/wb_tx_rate_test.py"

if [[ ! -f "${TX_SCRIPT}" ]]; then
  echo "TX script not found: ${TX_SCRIPT}" >&2
  exit 1
fi

if ! curl -fsS "http://${API_HOST}:${API_PORT}/api/v1/health" >/dev/null; then
  echo "API health check failed: http://${API_HOST}:${API_PORT}/api/v1/health" >&2
  echo "Start server first, then retry." >&2
  exit 1
fi

cd "${PREVIEW_DIR}"
python3 -m http.server "${PREVIEW_PORT}" >/tmp/wand_preview_server.log 2>&1 &
PREVIEW_PID=$!
cleanup() {
  kill "${PREVIEW_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 0.5

PREVIEW_URL="http://127.0.0.1:${PREVIEW_PORT}/preview.html?api=http://${API_HOST}:${API_PORT}&wand=${WAND_ID}&ms=120"
echo "Preview URL: ${PREVIEW_URL}"

if command -v wslview >/dev/null 2>&1; then
  wslview "${PREVIEW_URL}" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${PREVIEW_URL}" >/dev/null 2>&1 || true
elif command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Start-Process '${PREVIEW_URL}'" >/dev/null 2>&1 || true
fi

echo "Starting TX now..."
python3 "${TX_SCRIPT}" \
  --host "${UDP_HOST}" \
  --port "${UDP_PORT}" \
  --device "${DEVICE_ID}" \
  --wand "${WAND_ID}" \
  --stroke-start "${STROKE_START}" \
  --duration "${DURATION}" \
  --repeat "${REPEAT}" \
  --sweep "${RATES}" \
  --pattern "${PATTERN}"

echo "TX finished. Preview remains available while this script is running."
echo "Press Ctrl+C to close preview server."
wait "${PREVIEW_PID}"
