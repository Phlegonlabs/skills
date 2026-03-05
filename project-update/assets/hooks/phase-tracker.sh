#!/bin/bash
# Phase Tracker — UserPromptSubmit
# Detects intent keywords and updates phase state automatically.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

PHASE_FILE="$(hook_get_phase_file)"
STATE_DIR="$(dirname "$PHASE_FILE")"
PROMPT_TEXT="$(hook_get_prompt "${1:-}")"
PROMPT_LC="$(printf '%s' "$PROMPT_TEXT" | tr '[:upper:]' '[:lower:]')"

detect_phase() {
  local text="$1"

  if echo "$text" | grep -qE "(research|study|调研|深读|研究)"; then
    echo "research"
    return
  fi
  if echo "$text" | grep -qE "(plan|planning|计划|方案)"; then
    echo "plan"
    return
  fi
  if echo "$text" | grep -qE "(notes|annotate|annotation|注释|批注)"; then
    echo "annotate"
    return
  fi
  if echo "$text" | grep -qE "(implement|execution|execute|build it|do it|实现|执行|开始写|动手)"; then
    echo "implement"
    return
  fi
}

NEXT_PHASE="$(detect_phase "$PROMPT_LC" || true)"
[[ -n "$NEXT_PHASE" ]] || exit 0

PREV_PHASE=""
if [[ -f "$PHASE_FILE" ]]; then
  PREV_PHASE="$(tr -d '\r\n[:space:]' < "$PHASE_FILE" 2>/dev/null || true)"
fi

mkdir -p "$STATE_DIR"
printf '%s\n' "$NEXT_PHASE" > "$PHASE_FILE"
echo "[PhaseTracker] phase=$NEXT_PHASE"

if [[ "$PREV_PHASE" == "research" && "$NEXT_PHASE" == "plan" ]]; then
  echo "[PhaseTracker] Research complete. Write a plan before implementing."
fi

if [[ "$PREV_PHASE" == "plan" && "$NEXT_PHASE" == "implement" ]]; then
  echo "[PhaseTracker] Entering implementation. Run typecheck continuously."
fi

exit 0
