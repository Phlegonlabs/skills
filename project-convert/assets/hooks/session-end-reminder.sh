#!/bin/bash
# Session End Reminder — Stop event
# Reminds about unchecked tasks when a session ends.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-output.sh"

PROJECT_DIR="$(hook_get_project_dir)"
TODO_FILE="$PROJECT_DIR/tasks/todo.md"

if [[ -f "$TODO_FILE" ]] && grep -q '\- \[ \]' "$TODO_FILE"; then
  hook_system_message "Session ending with unchecked tasks in tasks/todo.md. Follow Session Handoff Protocol: update task status, note in-progress context, run verification, create WIP commit."
fi
