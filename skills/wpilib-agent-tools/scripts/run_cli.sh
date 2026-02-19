#!/usr/bin/env bash
set -euo pipefail

CLI_BIN="${WPILIB_AGENT_TOOLS_CLI:-wpilib-agent-tools}"

if command -v "${CLI_BIN}" >/dev/null 2>&1; then
  exec "${CLI_BIN}" "$@"
fi

if [[ -n "${WPILIB_AGENT_TOOLS_REPO:-}" ]]; then
  if [[ -d "${WPILIB_AGENT_TOOLS_REPO}/agent/src" ]]; then
    export PYTHONPATH="${WPILIB_AGENT_TOOLS_REPO}/agent/src:${PYTHONPATH:-}"
    exec python3 -m wpilib_agent_tools "$@"
  fi
fi

echo "wpilib-agent-tools CLI not found. Install it or set WPILIB_AGENT_TOOLS_REPO." >&2
exit 127
