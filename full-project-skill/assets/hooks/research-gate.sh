#!/bin/bash
# Research Gate — PreToolUse on Edit|Write
# Requires research artifacts before implementation phase writes.
# Default mode: warn only. Enforcement mode: block when marker exists.

set -euo pipefail

PHASE_FILE=".claude/.phase"
ENFORCE_MARKER=".claude/.require-phase-gate"

[[ -f "$PHASE_FILE" ]] || exit 0
PHASE="$(tr -d '\r\n[:space:]' < "$PHASE_FILE" 2>/dev/null || true)"
[[ "$PHASE" == "implement" ]] || exit 0

if [[ -f "research.md" || -f "docs/architecture.md" ]]; then
  exit 0
fi

if [[ -f "$ENFORCE_MARKER" ]]; then
  echo "[ResearchGate] No research artifact found. Run research phase first."
  echo "  Required: research.md or docs/architecture.md"
  exit 2
fi

echo "[ResearchGate] No research artifact found. Run research phase first."
echo "  Warning-only mode. Create $ENFORCE_MARKER to enforce blocking."
exit 0
