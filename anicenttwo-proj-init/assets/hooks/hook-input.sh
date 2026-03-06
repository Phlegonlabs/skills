#!/bin/bash
# Shared input parsing helpers for hook scripts.
# Prefers stdin JSON, with env/argv fallbacks for compatibility.

# Resolve repo root — hooks may run from any cwd
if [[ -z "${HOOK_REPO_ROOT:-}" ]]; then
  HOOK_REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || true
  if [[ -z "$HOOK_REPO_ROOT" ]]; then
    HOOK_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)" || true
  fi
  if [[ -n "$HOOK_REPO_ROOT" ]]; then
    cd "$HOOK_REPO_ROOT" 2>/dev/null || true
  fi
  export HOOK_REPO_ROOT
fi

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

hook_normalize_json_path() {
  local path="$1"

  path="$(printf '%s' "$path" | sed -E 's@[[:space:]]*//[[:space:]]*empty$@@')"
  path="$(printf '%s' "$path" | sed -E 's/^[[:space:]]*\.//; s/[[:space:]]+$//')"
  printf '%s' "$path"
}

hook_query_json_with_runtime() {
  local json_input="$1"
  local path="$2"
  local runtime=""
  local output=""

  path="$(hook_normalize_json_path "$path")"

  if [[ -z "$path" ]]; then
    printf '%s' "$json_input"
    return 0
  fi

  if command -v bun >/dev/null 2>&1; then
    runtime="bun"
  elif command -v node >/dev/null 2>&1; then
    runtime="node"
  else
    return 1
  fi

  output="$(
    JSON_INPUT="$json_input" "$runtime" -e '
      const raw = process.env.JSON_INPUT ?? "";
      const query = (process.argv[1] ?? "").split(".").filter(Boolean);

      let value;
      try {
        value = raw.length > 0 ? JSON.parse(raw) : undefined;
      } catch {
        process.exit(1);
      }

      for (const segment of query) {
        if (
          value !== null &&
          value !== undefined &&
          typeof value === "object" &&
          Object.prototype.hasOwnProperty.call(value, segment)
        ) {
          value = value[segment];
        } else {
          value = undefined;
          break;
        }
      }

      if (value === undefined || value === null) {
        process.exit(2);
      }

      if (typeof value === "string") {
        process.stdout.write(value);
      } else if (typeof value === "number" || typeof value === "boolean") {
        process.stdout.write(String(value));
      } else {
        process.stdout.write(JSON.stringify(value));
      }
    ' "$path" 2>/dev/null || true
  )"

  if [[ -n "$output" ]]; then
    printf '%s' "$output"
    return 0
  fi

  return 1
}

hook_json_get() {
  local path="$1"
  local default_value="${2:-}"
  local parsed=""

  hook_read_stdin_once

  if [[ -n "$HOOK_STDIN_JSON" ]] && command -v jq >/dev/null 2>&1; then
    parsed="$(printf '%s' "$HOOK_STDIN_JSON" | jq -r "$path // empty" 2>/dev/null || true)"
  fi

  if [[ -z "$parsed" ]] && [[ -n "$HOOK_STDIN_JSON" ]]; then
    parsed="$(hook_query_json_with_runtime "$HOOK_STDIN_JSON" "$path" || true)"
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
    return
  fi

  if parsed="$(hook_query_json_with_runtime "$raw_arg" "$path" 2>/dev/null)" && [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
  fi
}

hook_get_file_path() {
  local arg="${1:-}"
  local parsed=""

  parsed="$(hook_json_get '.tool_input.file_path' '')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  if [[ -n "${CLAUDE_FILE_PATH:-}" ]]; then
    printf '%s' "$CLAUDE_FILE_PATH"
    return
  fi

  parsed="$(hook_parse_json_arg "$arg" '.tool_input.file_path')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  printf '%s' "$arg"
}

hook_get_prompt() {
  local arg="${1:-}"
  local parsed=""

  parsed="$(hook_json_get '.user_message' '')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  if [[ -n "${PROMPT:-}" ]]; then
    printf '%s' "$PROMPT"
    return
  fi

  parsed="$(hook_parse_json_arg "$arg" '.user_message')"
  if [[ -n "$parsed" ]]; then
    printf '%s' "$parsed"
    return
  fi

  printf '%s' "$arg"
}
