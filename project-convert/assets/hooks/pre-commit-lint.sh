#!/bin/bash
# Pre-Commit Lint — PreToolUse on Bash
# Runs lint + typecheck before git commit commands.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

TOOL_INPUT_RAW="$(hook_get_tool_input)"
[[ -z "$TOOL_INPUT_RAW" ]] && exit 0

if echo "$TOOL_INPUT_RAW" | grep -qE 'git\s+commit'; then
  PROJECT_DIR="$(hook_get_project_dir)"
  cd "$PROJECT_DIR"
  {{PM}} run lint && {{PM}} run typecheck
fi
