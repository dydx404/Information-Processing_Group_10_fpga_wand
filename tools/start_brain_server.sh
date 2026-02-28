#!/usr/bin/env bash
set -euo pipefail

# Starts the Wand-Brain FastAPI service from anywhere in the repo.
# Works on WSL and EC2.

HOST="0.0.0.0"
PORT="8000"
RELOAD="0"
INSTALL_DEPS="0"

usage() {
  cat <<'EOF'
Usage: tools/start_brain_server.sh [options]

Options:
  --host <ip>         Bind host (default: 0.0.0.0)
  --port <port>       Bind port (default: 8000)
  --reload            Enable uvicorn autoreload (dev only)
  --install-deps      Install/upgrade runtime deps in venv
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="${2:-}"; shift 2 ;;
    --port)
      PORT="${2:-}"; shift 2 ;;
    --reload)
      RELOAD="1"; shift ;;
    --install-deps)
      INSTALL_DEPS="1"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BRAIN_DIR="${REPO_ROOT}/cloud/backend/brain"
VENV_DIR="${BRAIN_DIR}/.venv"

if [[ ! -d "${BRAIN_DIR}" ]]; then
  echo "Brain directory not found: ${BRAIN_DIR}" >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Creating virtual environment at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [[ "${INSTALL_DEPS}" == "1" ]]; then
  python -m pip install --upgrade pip
  python -m pip install "fastapi>=0.100.0" "uvicorn>=0.22.0" "pillow>=9.0.0"
fi

cd "${BRAIN_DIR}"

echo "Starting Wand-Brain on ${HOST}:${PORT}"
if [[ "${RELOAD}" == "1" ]]; then
  exec uvicorn brain.api.server:app --app-dir src --host "${HOST}" --port "${PORT}" --reload
else
  exec uvicorn brain.api.server:app --app-dir src --host "${HOST}" --port "${PORT}"
fi
