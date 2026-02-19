#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/install_all.sh [options]

Options:
  --cli-mode <local|pipx>     CLI install mode (default: local)
  --pipx-spec <spec>          pipx install spec when --cli-mode pipx
  --skill-mode <symlink|copy> Codex skill sync mode (default: symlink)
  --codex-home <path>         Codex home path (default: $CODEX_HOME or ~/.codex)
  --skip-codex                Skip Codex skill sync
  --skip-checks               Skip skill validation + smoke checks
  --cursor-workspace <path>   Also install Cursor rules into this workspace
  --cursor-mode <core|all>    Cursor rules install mode (default: core)
  --cursor-force              Overwrite existing Cursor rule files
  --help                      Show this message

Examples:
  scripts/install_all.sh
  scripts/install_all.sh --cli-mode pipx --skill-mode copy
  scripts/install_all.sh --cursor-workspace ~/FRC/2026-Robot-Code --cursor-mode core
EOF
}

CLI_MODE="local"
PIPX_SPEC=""
SKILL_MODE="symlink"
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
SKIP_CODEX=0
SKIP_CHECKS=0
CURSOR_WORKSPACE=""
CURSOR_MODE="core"
CURSOR_FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli-mode)
      CLI_MODE="$2"
      shift 2
      ;;
    --pipx-spec)
      PIPX_SPEC="$2"
      shift 2
      ;;
    --skill-mode)
      SKILL_MODE="$2"
      shift 2
      ;;
    --codex-home)
      CODEX_HOME="$2"
      shift 2
      ;;
    --skip-codex)
      SKIP_CODEX=1
      shift
      ;;
    --skip-checks)
      SKIP_CHECKS=1
      shift
      ;;
    --cursor-workspace)
      CURSOR_WORKSPACE="$2"
      shift 2
      ;;
    --cursor-mode)
      CURSOR_MODE="$2"
      shift 2
      ;;
    --cursor-force)
      CURSOR_FORCE=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "${CLI_MODE}" != "local" && "${CLI_MODE}" != "pipx" ]]; then
  echo "--cli-mode must be one of: local, pipx" >&2
  exit 2
fi
if [[ "${SKILL_MODE}" != "symlink" && "${SKILL_MODE}" != "copy" ]]; then
  echo "--skill-mode must be one of: symlink, copy" >&2
  exit 2
fi
if [[ "${CURSOR_MODE}" != "core" && "${CURSOR_MODE}" != "all" ]]; then
  echo "--cursor-mode must be one of: core, all" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1/4] Installing CLI (${CLI_MODE})"
CLI_CMD=("${REPO_ROOT}/scripts/install_cli.sh" --mode "${CLI_MODE}")
if [[ -n "${PIPX_SPEC}" ]]; then
  CLI_CMD+=(--pipx-spec "${PIPX_SPEC}")
fi
"${CLI_CMD[@]}"

if [[ "${SKIP_CODEX}" -eq 0 ]]; then
  echo "[2/4] Syncing Codex skill (${SKILL_MODE})"
  "${REPO_ROOT}/scripts/sync_skill.sh" --mode "${SKILL_MODE}" --codex-home "${CODEX_HOME}"
else
  echo "[2/4] Skipping Codex skill sync"
fi

if [[ "${SKIP_CHECKS}" -eq 0 ]]; then
  echo "[3/4] Running validation checks"
  if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    "${REPO_ROOT}/.venv/bin/python" "${REPO_ROOT}/scripts/validate_skill.py" "${REPO_ROOT}/skills/wpilib-agent-tools"
  else
    python3 "${REPO_ROOT}/scripts/validate_skill.py" "${REPO_ROOT}/skills/wpilib-agent-tools"
  fi
  "${REPO_ROOT}/scripts/smoke.sh"
else
  echo "[3/4] Skipping validation checks"
fi

if [[ -n "${CURSOR_WORKSPACE}" ]]; then
  echo "[4/4] Installing Cursor rules (${CURSOR_MODE})"
  CURSOR_CMD=(
    "${REPO_ROOT}/scripts/install_cursor_rules.sh"
    --workspace "${CURSOR_WORKSPACE}"
    --mode "${CURSOR_MODE}"
  )
  if [[ "${CURSOR_FORCE}" -eq 1 ]]; then
    CURSOR_CMD+=(--force)
  fi
  "${CURSOR_CMD[@]}"
else
  echo "[4/4] Cursor setup skipped (no --cursor-workspace provided)"
fi

echo "Install complete."
