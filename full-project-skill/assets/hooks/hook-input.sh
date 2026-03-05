#!/bin/bash
# Shared input parsing helpers for hook scripts.
# Supports Claude Code and Codex CLI input formats.
# Prefers stdin JSON, with env/argv fallbacks for compatibility.

hook_read_stdin_once() {
  if [[ -n "${HOOK_STDIN_JSON+x}" ]]; then
    return
  fi

  if [[ -t 0 ]]; then
    HOOK_STDIN_JSON=""
    return
  fi

  HOOK_STDIN_JSON="$(cat 2>/dev/null || true)"
}

hook_json_get() {
  local path="$1"
  local default_value="${2:-}"
  local parsed=""

  hook_read_stdin_once

  if [[ -n "$HOOK_STDIN_JSON" ]] && command -v jq >/dev/null 2>&1; then
    parsed="$(printf '%s' "$HOOK_STDIN_JSON" | jq -r "$path // empty" 2>/dev/null || true)"
  fi

  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
  else
    printf '%s' "$default_value"
  fi
}

hook_parse_json_arg() {
  local raw_arg="${1:-}"
  local path="$2"

  if [[ -z "$raw_arg" ]]; then
    return
  fi

  if command -v jq >/dev/null 2>&1 && printf '%s' "$raw_arg" | jq -e . >/dev/null 2>&1; then
    printf '%s' "$raw_arg" | jq -r "$path // empty" 2>/dev/null || true
  fi
}

hook_get_file_path() {
  local arg="${1:-}"
  local parsed=""

  # 1. stdin JSON (Claude Code & Codex both support)
  parsed="$(hook_json_get '.tool_input.file_path' '')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  # 2. Platform env vars (Claude Code → CLAUDE_FILE_PATH, Codex → CODEX_FILE_PATH)
  if [[ -n "${CLAUDE_FILE_PATH:-}" ]]; then
    printf '%s' "$CLAUDE_FILE_PATH"
    return
  fi
  if [[ -n "${CODEX_FILE_PATH:-}" ]]; then
    printf '%s' "$CODEX_FILE_PATH"
    return
  fi

  # 3. argv JSON fallback
  parsed="$(hook_parse_json_arg "$arg" '.tool_input.file_path')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  # 4. Raw string fallback
  printf '%s' "$arg"
}

hook_get_prompt() {
  local arg="${1:-}"
  local parsed=""

  # 1. stdin JSON
  parsed="$(hook_json_get '.user_message' '')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  # 2. Platform env vars
  if [[ -n "${PROMPT:-}" ]]; then
    printf '%s' "$PROMPT"
    return
  fi
  if [[ -n "${CODEX_PROMPT:-}" ]]; then
    printf '%s' "$CODEX_PROMPT"
    return
  fi

  # 3. argv JSON fallback
  parsed="$(hook_parse_json_arg "$arg" '.user_message')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  # 4. Raw string fallback
  printf '%s' "$arg"
}

hook_get_project_dir() {
  if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
    printf '%s' "$CLAUDE_PROJECT_DIR"
    return
  fi
  if [[ -n "${CODEX_PROJECT_DIR:-}" ]]; then
    printf '%s' "$CODEX_PROJECT_DIR"
    return
  fi
  pwd
}

hook_get_session_id() {
  if [[ -n "${CLAUDE_SESSION_ID:-}" ]]; then
    printf '%s' "$CLAUDE_SESSION_ID"
    return
  fi
  if [[ -n "${CODEX_SESSION_ID:-}" ]]; then
    printf '%s' "$CODEX_SESSION_ID"
    return
  fi
  printf '%s' "${SESSION_KEY:-}"
}

hook_get_tool_input() {
  local parsed=""

  parsed="$(hook_json_get '.tool_input' '')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  if [[ -n "${TOOL_INPUT:-}" ]]; then
    printf '%s' "$TOOL_INPUT"
    return
  fi
  if [[ -n "${CODEX_TOOL_INPUT:-}" ]]; then
    printf '%s' "$CODEX_TOOL_INPUT"
    return
  fi
}

hook_get_state_dir() {
  if [[ -n "${HOOK_STATE_DIR:-}" ]]; then
    printf '%s' "$HOOK_STATE_DIR"
    return
  fi

  if [[ -d ".ai" ]]; then
    printf '%s' ".ai"
    return
  fi

  if [[ -d ".claude" && ! -d ".codex" ]]; then
    printf '%s' ".claude"
    return
  fi

  if [[ -d ".codex" && ! -d ".claude" ]]; then
    printf '%s' ".codex"
    return
  fi

  printf '%s' ".ai"
}

hook_get_phase_file() {
  local state_dir
  state_dir="$(hook_get_state_dir)"

  if [[ -f "$state_dir/.phase" ]]; then
    printf '%s' "$state_dir/.phase"
    return
  fi

  if [[ -f ".claude/.phase" ]]; then
    printf '%s' ".claude/.phase"
    return
  fi

  if [[ -f ".codex/.phase" ]]; then
    printf '%s' ".codex/.phase"
    return
  fi

  printf '%s' "$state_dir/.phase"
}

hook_get_phase_gate_marker() {
  local state_dir
  state_dir="$(hook_get_state_dir)"

  if [[ -f "$state_dir/.require-phase-gate" ]]; then
    printf '%s' "$state_dir/.require-phase-gate"
    return
  fi

  if [[ -f ".claude/.require-phase-gate" ]]; then
    printf '%s' ".claude/.require-phase-gate"
    return
  fi

  if [[ -f ".codex/.require-phase-gate" ]]; then
    printf '%s' ".codex/.require-phase-gate"
    return
  fi

  printf '%s' "$state_dir/.require-phase-gate"
}
