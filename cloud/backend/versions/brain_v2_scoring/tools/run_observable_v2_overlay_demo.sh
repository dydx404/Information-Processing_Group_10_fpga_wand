#!/usr/bin/env bash
set -euo pipefail

# v2 scoring demo launcher:
# - serves v2 preview page locally
# - opens browser automatically
# - runs long single-stroke noisy UDP TX test
#
# Backend API must already be running (typically on EC2).

API_HOST="${API_HOST:-16.16.202.231}"
API_PORT="${API_PORT:-8000}"
UDP_HOST="${UDP_HOST:-16.16.202.231}"
UDP_PORT="${UDP_PORT:-41000}"

WAND_ID="${WAND_ID:-1}"
DEVICE_ID="${DEVICE_ID:-1}"
PREVIEW_PORT="${PREVIEW_PORT:-8012}"

TEMPLATE_ID="${TEMPLATE_ID:-heart_v1}"   # circle_v1|triangle_v1|heart_v1|sine_v1|infinity_v1
STROKE_ID="${STROKE_ID:-920000}"
RATE="${RATE:-15}"
DURATION="${DURATION:-45}"
SHAPE="${SHAPE:-lissajous}"              # circle|spiral|lemniscate|lissajous
NOISE_STD="${NOISE_STD:-0.008}"
WANDER_STD="${WANDER_STD:-0.003}"
DRIFT_X="${DRIFT_X:-0.0}"
DRIFT_Y="${DRIFT_Y:-0.0}"
SEED="${SEED:-7}"

usage() {
  cat <<EOF
Usage: cloud/backend/versions/brain_v2_scoring/tools/run_observable_v2_overlay_demo.sh [options]

Options:
  --api-host <host>         API host for preview & template (default: ${API_HOST})
  --api-port <port>         API port (default: ${API_PORT})
  --udp-host <host>         UDP target host (default: ${UDP_HOST})
  --udp-port <port>         UDP target port (default: ${UDP_PORT})
  --wand <id>               wand_id (default: ${WAND_ID})
  --device <id>             device_number (default: ${DEVICE_ID})
  --preview-port <port>     local preview static server port (default: ${PREVIEW_PORT})
  --template <id>           template id (default: ${TEMPLATE_ID})
  --stroke-id <id>          stroke id (default: ${STROKE_ID})
  --rate <pps>              packets per second (default: ${RATE})
  --duration <sec>          stroke duration (default: ${DURATION})
  --shape <name>            circle|spiral|lemniscate|lissajous (default: ${SHAPE})
  --noise-std <v>           point jitter std (default: ${NOISE_STD})
  --wander-std <v>          slow wander std (default: ${WANDER_STD})
  --drift-x <v>             x drift over stroke (default: ${DRIFT_X})
  --drift-y <v>             y drift over stroke (default: ${DRIFT_Y})
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
    --template) TEMPLATE_ID="${2:-}"; shift 2 ;;
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
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"
PREVIEW_DIR="${SCRIPT_DIR}"
TX_SCRIPT="${REPO_ROOT}/tools/wb_tx_long_noisy_stroke.py"

if [[ ! -f "${TX_SCRIPT}" ]]; then
  echo "TX script not found: ${TX_SCRIPT}" >&2
  exit 1
fi

if ! curl -fsS "http://${API_HOST}:${API_PORT}/api/v1/health" >/dev/null; then
  echo "API health check failed: http://${API_HOST}:${API_PORT}/api/v1/health" >&2
  exit 1
fi

if ! curl -fsS "http://${API_HOST}:${API_PORT}/api/v2/template/${TEMPLATE_ID}/image.png" >/dev/null; then
  echo "Template check failed: ${TEMPLATE_ID} not accessible on API host ${API_HOST}:${API_PORT}" >&2
  echo "Available templates: curl http://${API_HOST}:${API_PORT}/api/v2/templates" >&2
  exit 1
fi

cd "${PREVIEW_DIR}"
python3 -m http.server "${PREVIEW_PORT}" >/tmp/wand_v2_preview_server.log 2>&1 &
PREVIEW_PID=$!
cleanup() {
  kill "${PREVIEW_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 0.5

PREVIEW_URL="http://127.0.0.1:${PREVIEW_PORT}/preview.html?api=http://${API_HOST}:${API_PORT}&wand=${WAND_ID}&template=${TEMPLATE_ID}&ms=120"
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

echo "TX finished. Preview remains active until Ctrl+C."
wait "${PREVIEW_PID}"
