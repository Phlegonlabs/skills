#!/bin/bash
# Research Gate — PreToolUse on Edit|Write
# Requires research artifacts before implementation phase writes.
# Blocks by default when research artifacts are missing in implementation phase.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

PHASE_FILE="$(hook_get_phase_file)"
ENFORCE_MARKER="$(hook_get_phase_gate_marker)"

[[ -f "$PHASE_FILE" ]] || exit 0
PHASE="$(tr -d '\r\n[:space:]' < "$PHASE_FILE" 2>/dev/null || true)"
[[ "$PHASE" == "implement" ]] || exit 0

if [[ -f "research.md" || -f "docs/architecture.md" ]]; then
  exit 0
fi

echo "[ResearchGate] No research artifact found. Run research phase first."
echo "  Required: research.md or docs/architecture.md"
echo "  Phase gate is enforced by default."
echo "  Marker path: $ENFORCE_MARKER"
exit 2
