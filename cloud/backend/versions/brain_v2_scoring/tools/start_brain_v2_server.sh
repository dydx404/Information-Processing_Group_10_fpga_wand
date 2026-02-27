#!/usr/bin/env bash
set -euo pipefail

# Starts the brain_v2_scoring FastAPI service.
# Intended for EC2 and local use.

HOST="0.0.0.0"
PORT="8000"
RELOAD="0"
INSTALL_DEPS="0"
GENERATE_TEMPLATES="0"

usage() {
  cat <<'EOF'
Usage: cloud/backend/versions/brain_v2_scoring/tools/start_brain_v2_server.sh [options]

Options:
  --host <ip>              Bind host (default: 0.0.0.0)
  --port <port>            Bind port (default: 8000)
  --reload                 Enable uvicorn autoreload (dev only)
  --install-deps           Install/upgrade runtime deps in venv
  --generate-templates     Run tools/generate_templates.py before server start
  -h, --help               Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --reload) RELOAD="1"; shift ;;
    --install-deps) INSTALL_DEPS="1"; shift ;;
    --generate-templates) GENERATE_TEMPLATES="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${APP_DIR}/.venv"

if [[ ! -d "${APP_DIR}" ]]; then
  echo "v2 app directory not found: ${APP_DIR}" >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Creating virtual environment at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

PY_BIN="${VENV_DIR}/bin/python"
if [[ ! -x "${PY_BIN}" ]]; then
  echo "Venv python not found at ${PY_BIN}" >&2
  exit 1
fi

if [[ "${INSTALL_DEPS}" == "1" ]]; then
  "${PY_BIN}" -m ensurepip --upgrade || true
  "${PY_BIN}" -m pip install --upgrade pip
  "${PY_BIN}" -m pip install "fastapi>=0.100.0" "uvicorn>=0.22.0" "pillow>=9.0.0" "numpy>=1.24.0"
fi

cd "${APP_DIR}"

if [[ "${GENERATE_TEMPLATES}" == "1" ]]; then
  "${PY_BIN}" tools/generate_templates.py
fi

echo "Starting brain_v2_scoring on ${HOST}:${PORT}"
if [[ "${RELOAD}" == "1" ]]; then
  exec "${PY_BIN}" -m uvicorn brain.api.server:app --app-dir src --host "${HOST}" --port "${PORT}" --reload
else
  exec "${PY_BIN}" -m uvicorn brain.api.server:app --app-dir src --host "${HOST}" --port "${PORT}"
fi
