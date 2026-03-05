#!/bin/bash
# Pre-Push Test — PreToolUse on Bash
# Runs tests before git push commands.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

TOOL_INPUT_RAW="$(hook_get_tool_input)"
[[ -z "$TOOL_INPUT_RAW" ]] && exit 0

if echo "$TOOL_INPUT_RAW" | grep -qE 'git\s+push'; then
  PROJECT_DIR="$(hook_get_project_dir)"
  cd "$PROJECT_DIR"
  {{PM}} run test
fi
