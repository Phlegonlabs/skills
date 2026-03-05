#!/bin/bash
# Plan Gate — PreToolUse on Edit|Write
# Prevents implementation writes during planning / annotation phases.
# Blocks by default when phase constraints are violated.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

PHASE_FILE="$(hook_get_phase_file)"
ENFORCE_MARKER="$(hook_get_phase_gate_marker)"
FILE_PATH="$(hook_get_file_path "${1:-}")"

[[ -f "$PHASE_FILE" ]] || exit 0
PHASE="$(tr -d '\r\n[:space:]' < "$PHASE_FILE" 2>/dev/null || true)"
[[ -n "$PHASE" ]] || exit 0

is_allowed_for_phase() {
  local phase="$1"
  local path="$2"

  case "$phase" in
    plan)
      [[ "$path" =~ (^|/)(plan\.md|research\.md|docs/|tasks/) ]]
      ;;
    annotate)
      [[ "$path" =~ (^|/)(plan\.md|docs/|tasks/) ]]
      ;;
    *)
      return 0
      ;;
  esac
}

block_with_reason() {
  local message="$1"
  echo "[PlanGate] $message"
  echo "  Phase gate is enforced by default."
  echo "  Marker path: $ENFORCE_MARKER"
  exit 2
}

if [[ -n "$FILE_PATH" ]] && ! is_allowed_for_phase "$PHASE" "$FILE_PATH"; then
  if [[ "$PHASE" == "plan" ]]; then
    block_with_reason "Plan not approved yet. Finish planning before implementing. Target: $FILE_PATH"
  elif [[ "$PHASE" == "annotate" ]]; then
    block_with_reason "Annotation cycle in progress. Address notes before implementing. Target: $FILE_PATH"
  fi
fi

for plan_file in "plan.md" "docs/plans.md"; do
  if [[ -f "$plan_file" ]] && grep -qE "(NOTE|TODO)" "$plan_file"; then
    echo "[PlanGate] Unresolved NOTE/TODO markers detected in $plan_file."
    echo "  Resolve planning notes before writing implementation code."
  fi
done

exit 0
