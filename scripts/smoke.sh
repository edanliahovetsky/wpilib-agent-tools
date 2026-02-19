#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_CLI="${REPO_ROOT}/scripts/run_cli.sh"

"${RUN_CLI}" --version >/dev/null
"${RUN_CLI}" --help >/dev/null

JSON_OUT="$("${RUN_CLI}" math --mode simplify --expr "sin(x)**2 + cos(x)**2" --json)"
python3 -c 'import json,sys; payload=json.loads(sys.stdin.read()); assert payload.get("result") == "1", payload' <<<"${JSON_OUT}"

echo "Smoke checks passed."
