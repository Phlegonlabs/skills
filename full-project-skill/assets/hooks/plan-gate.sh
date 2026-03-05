#!/bin/bash
# Plan Gate — PreToolUse on Edit|Write
# Prevents implementation writes during planning / annotation phases.
# Default mode: warn only. Enforcement mode: block when marker exists.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

PHASE_FILE=".claude/.phase"
ENFORCE_MARKER=".claude/.require-phase-gate"
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

warn_or_block() {
  local message="$1"
  if [[ -f "$ENFORCE_MARKER" ]]; then
    echo "[PlanGate] $message"
    echo "  Enforcement marker: $ENFORCE_MARKER"
    exit 2
  fi
  echo "[PlanGate] $message"
  echo "  Warning-only mode. Create $ENFORCE_MARKER to enforce blocking."
}

if [[ -n "$FILE_PATH" ]] && ! is_allowed_for_phase "$PHASE" "$FILE_PATH"; then
  if [[ "$PHASE" == "plan" ]]; then
    warn_or_block "Plan not approved yet. Finish planning before implementing. Target: $FILE_PATH"
  elif [[ "$PHASE" == "annotate" ]]; then
    warn_or_block "Annotation cycle in progress. Address notes before implementing. Target: $FILE_PATH"
  fi
fi

for plan_file in "plan.md" "docs/plans.md"; do
  if [[ -f "$plan_file" ]] && grep -qE "(NOTE|TODO)" "$plan_file"; then
    echo "[PlanGate] Unresolved NOTE/TODO markers detected in $plan_file."
    echo "  Resolve planning notes before writing implementation code."
  fi
done

exit 0
