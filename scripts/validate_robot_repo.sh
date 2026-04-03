#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export WPILIB_AGENT_TOOLS_REPO="${REPO_ROOT}"
exec python3 "${REPO_ROOT}/agent/src/wpilib_agent_tools/integrations/codex/skill_bundle/scripts/validate_robot_repo.py" "$@"
