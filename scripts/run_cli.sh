#!/usr/bin/env bash
set -euo pipefail

CLI_BIN="${WPILIB_AGENT_TOOLS_CLI:-wpilib-agent-tools}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v "${CLI_BIN}" >/dev/null 2>&1; then
  exec "${CLI_BIN}" "$@"
fi

if [[ -d "${REPO_ROOT}/agent/src" ]]; then
  export PYTHONPATH="${REPO_ROOT}/agent/src:${PYTHONPATH:-}"
  exec python3 -m wpilib_agent_tools "$@"
fi

echo "wpilib-agent-tools CLI not found. Run scripts/bootstrap.sh first." >&2
exit 127
