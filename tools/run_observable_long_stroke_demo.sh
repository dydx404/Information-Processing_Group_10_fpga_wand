#!/usr/bin/env bash
set -euo pipefail

# Opens live preview page and runs one long noisy single-stroke TX test.
# Backend (Wand-Brain API) must already be running.

API_HOST="${API_HOST:-16.16.202.231}"
API_PORT="${API_PORT:-8000}"
UDP_HOST="${UDP_HOST:-16.16.202.231}"
UDP_PORT="${UDP_PORT:-41000}"
WAND_ID="${WAND_ID:-1}"
DEVICE_ID="${DEVICE_ID:-1}"

PREVIEW_PORT="${PREVIEW_PORT:-8010}"
STROKE_ID="${STROKE_ID:-900100}"
RATE="${RATE:-15}"
DURATION="${DURATION:-60}"
SHAPE="${SHAPE:-lissajous}"
NOISE_STD="${NOISE_STD:-0.008}"
WANDER_STD="${WANDER_STD:-0.003}"
DRIFT_X="${DRIFT_X:-0.0}"
DRIFT_Y="${DRIFT_Y:-0.0}"
SEED="${SEED:-7}"

usage() {
  cat <<EOF
Usage: tools/run_observable_long_stroke_demo.sh [options]

Options:
  --api-host <host>         API host for preview (default: ${API_HOST})
  --api-port <port>         API port (default: ${API_PORT})
  --udp-host <host>         UDP TX host (default: ${UDP_HOST})
  --udp-port <port>         UDP TX port (default: ${UDP_PORT})
  --wand <id>               wand_id (default: ${WAND_ID})
  --device <id>             device_number (default: ${DEVICE_ID})
  --preview-port <port>     local preview static server port (default: ${PREVIEW_PORT})
  --stroke-id <id>          stroke_id for this long attempt (default: ${STROKE_ID})
  --rate <pps>              packets per second (default: ${RATE})
  --duration <sec>          stroke duration seconds (default: ${DURATION})
  --shape <name>            circle|spiral|lemniscate|lissajous (default: ${SHAPE})
  --noise-std <v>           jitter std (default: ${NOISE_STD})
  --wander-std <v>          wander std (default: ${WANDER_STD})
  --drift-x <v>             drift x (default: ${DRIFT_X})
  --drift-y <v>             drift y (default: ${DRIFT_Y})
  --seed <n>                RNG seed (default: ${SEED})
  -h, --help                show help
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
    --stroke-id) STROKE_ID="${2:-}"; shift 2 ;;
    --rate) RATE="${2:-}"; shift 2 ;;
    --duration) DURATION="${2:-}"; shift 2 ;;
    --shape) SHAPE="${2:-}"; shift 2 ;;
    --noise-std) NOISE_STD="${2:-}"; shift 2 ;;
    --wander-std) WANDER_STD="${2:-}"; shift 2 ;;
    --drift-x) DRIFT_X="${2:-}"; shift 2 ;;
    --drift-y) DRIFT_Y="${2:-}"; shift 2 ;;
    --seed) SEED="${2:-}"; shift 2 ;;
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
TX_SCRIPT="${REPO_ROOT}/tools/wb_tx_long_noisy_stroke.py"

if ! curl -fsS "http://${API_HOST}:${API_PORT}/api/v1/health" >/dev/null; then
  echo "API health check failed: http://${API_HOST}:${API_PORT}/api/v1/health" >&2
  echo "Start/restart backend first, then retry." >&2
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

echo "Starting long single-stroke TX..."
python3 "${TX_SCRIPT}" \
  --host "${UDP_HOST}" \
  --port "${UDP_PORT}" \
  --device "${DEVICE_ID}" \
  --wand "${WAND_ID}" \
  --stroke-id "${STROKE_ID}" \
  --rate "${RATE}" \
  --duration "${DURATION}" \
  --shape "${SHAPE}" \
  --noise-std "${NOISE_STD}" \
  --wander-std "${WANDER_STD}" \
  --drift-x "${DRIFT_X}" \
  --drift-y "${DRIFT_Y}" \
  --seed "${SEED}"

echo "TX finished. Preview stays up while this script runs."
echo "Press Ctrl+C to close preview server."
wait "${PREVIEW_PID}"
