#!/bin/bash
# Plan Sync Reminder — PostToolUse on Edit|Write
# Reminds to keep documentation.md in sync when plans.md is modified.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-output.sh"

TOOL_INPUT_RAW="$(hook_get_tool_input)"
[[ -z "$TOOL_INPUT_RAW" ]] && exit 0

if echo "$TOOL_INPUT_RAW" | grep -q 'plans.md'; then
  hook_system_message "Reminder: docs/plans.md was modified. Keep docs/documentation.md milestone status in sync."
fi
