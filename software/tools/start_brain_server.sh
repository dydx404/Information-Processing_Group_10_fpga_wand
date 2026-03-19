#!/usr/bin/env bash
set -euo pipefail

# Starts the canonical cloud app from anywhere inside the software subtree.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOFTWARE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

exec "${SOFTWARE_ROOT}/cloud/start_script.sh" "$@"
