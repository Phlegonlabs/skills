#!/bin/bash
# Shared output helpers for hook scripts.
# Detects the active platform (Claude Code / Codex CLI / generic) and formats
# structured responses accordingly.
#
# Platform detection order:
#   1. Explicit HOOK_PLATFORM env var (claude | codex)
#   2. CLAUDE_PROJECT_DIR present → claude
#   3. CODEX_PROJECT_DIR or CODEX_SESSION_ID present → codex
#   4. Fallback → generic (plain text only)

hook_detect_platform() {
  if [[ -n "${HOOK_PLATFORM:-}" ]]; then
    printf '%s' "$HOOK_PLATFORM"
    return
  fi
  if [[ -n "${CLAUDE_PROJECT_DIR:-}" || -n "${CLAUDE_SESSION_ID:-}" ]]; then
    printf 'claude'
    return
  fi
  if [[ -n "${CODEX_PROJECT_DIR:-}" || -n "${CODEX_SESSION_ID:-}" ]]; then
    printf 'codex'
    return
  fi
  printf 'generic'
}

# Emit a system message that the AI agent will see.
# Usage: hook_system_message "Your reminder text here"
hook_system_message() {
  local msg="$1"
  local platform
  platform="$(hook_detect_platform)"

  case "$platform" in
    claude)
      # Claude Code JSON protocol
      printf '{"systemMessage":"%s"}\n' "$(printf '%s' "$msg" | sed 's/"/\\"/g')"
      ;;
    codex)
      # Codex CLI: plain text to stderr is shown as system context
      printf '[system] %s\n' "$msg" >&2
      ;;
    *)
      printf '%s\n' "$msg"
      ;;
  esac
}

# Request permission confirmation from the user before a tool runs.
# Usage: hook_ask_permission "Reason for asking"
hook_ask_permission() {
  local reason="$1"
  local platform
  platform="$(hook_detect_platform)"

  case "$platform" in
    claude)
      printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"%s"}}\n' \
        "$(printf '%s' "$reason" | sed 's/"/\\"/g')"
      ;;
    codex)
      # Codex CLI: exit 1 triggers approval prompt; print reason first
      printf '[hook] %s\n' "$reason" >&2
      exit 1
      ;;
    *)
      printf '[confirm] %s\n' "$reason"
      exit 1
      ;;
  esac
}

# Block a tool call outright.
# Usage: hook_deny "Reason for blocking"
hook_deny() {
  local reason="$1"
  local platform
  platform="$(hook_detect_platform)"

  case "$platform" in
    claude)
      printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' \
        "$(printf '%s' "$reason" | sed 's/"/\\"/g')"
      exit 2
      ;;
    codex)
      printf '[denied] %s\n' "$reason" >&2
      exit 2
      ;;
    *)
      printf '[denied] %s\n' "$reason"
      exit 2
      ;;
  esac
}
