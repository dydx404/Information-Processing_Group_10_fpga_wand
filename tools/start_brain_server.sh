#!/usr/bin/env bash
set -euo pipefail

# Starts the canonical cloud app from anywhere in the repo.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

exec "${REPO_ROOT}/cloud/start_script.sh" "$@"
