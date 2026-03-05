#!/bin/bash
# Immutable Layer Guard — PreToolUse on Bash
# Asks for confirmation before modifying architecture or implement docs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-output.sh"

TOOL_INPUT_RAW="$(hook_get_tool_input)"
[[ -z "$TOOL_INPUT_RAW" ]] && exit 0

if echo "$TOOL_INPUT_RAW" | grep -qE 'docs/(architecture|implement)\.md'; then
  hook_ask_permission "This file is in the immutable layer. Confirm with the user before modifying."
fi
