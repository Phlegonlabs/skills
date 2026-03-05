#!/bin/bash
# Doc Drift Guard — PostToolUse on Edit|Write
# Detects project-shape changes that may require docs updates.

set -euo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/hook-input.sh"

FILE_PATH="$(hook_get_file_path "${1:-}")"
[[ -z "$FILE_PATH" ]] && exit 0

BASENAME=$(basename "$FILE_PATH")

# 1) Source implementation drift -> architecture docs.
if [[ "$FILE_PATH" =~ (^|/)(src|apps/[^/]+/src|packages/[^/]+/src)/.+ ]]; then
  echo "[DocDrift] Source changed: $FILE_PATH"
  echo "  Check: docs/architecture.md may need updates."
fi

# 2) Docs content changed -> user-facing documentation consistency.
if [[ "$FILE_PATH" =~ (^|/)docs/.+ ]]; then
  echo "[DocDrift] Documentation file changed: $FILE_PATH"
  echo "  Check: docs/documentation.md stays aligned with current behavior."
fi

# 3) Config changes -> revisit locked tech stack notes.
if [[ "$FILE_PATH" =~ (^|/)(package\.json|bun\.lock|pnpm-lock\.yaml|package-lock\.json|tsconfig.*\.json|eslint.*|biome.*|vite\.config\..*|vitest\.config\..*|playwright\.config\..*|wrangler.*\.toml|turbo\.json)$ ]]; then
  echo "[DocDrift] Config changed: $BASENAME"
  echo "  Check: tech stack and commands in docs/architecture.md + docs/plans.md."
fi
