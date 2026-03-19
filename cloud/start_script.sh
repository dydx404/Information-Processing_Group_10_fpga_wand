#!/usr/bin/env bash
set -euo pipefail

HOST="0.0.0.0"
PORT="8000"
INSTALL_DEPS="0"

usage() {
  cat <<'USAGE'
Usage: cloud/start_script.sh [--host <ip>] [--port <port>] [--install-deps]

Environment:
  DATABASE_URL   Optional. Defaults to local SQLite at cloud/data/fpgawand.sqlite3.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --install-deps) INSTALL_DEPS="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

PY_BIN="${VENV_DIR}/bin/python"
PIP_BIN="${VENV_DIR}/bin/pip"

if [[ "${INSTALL_DEPS}" == "1" ]]; then
  "${PY_BIN}" -m ensurepip --upgrade || true
  "${PIP_BIN}" install --upgrade pip
  "${PIP_BIN}" install \
    "fastapi>=0.100.0" \
    "uvicorn>=0.22.0" \
    "pillow>=9.0.0" \
    "numpy>=1.24.0" \
    "sqlalchemy>=2.0.0" \
    "psycopg2-binary>=2.9.0"
fi

cd "${SCRIPT_DIR}"
exec "${PY_BIN}" -m uvicorn main:app --host "${HOST}" --port "${PORT}"
