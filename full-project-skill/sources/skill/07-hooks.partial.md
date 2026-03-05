## Hooks

Install project hooks via `scripts/setup-hooks.sh`. Hooks are **platform-universal** and support
both Claude Code and Codex CLI.

### Supported Platforms

| Platform | Config Dir | Template | Event Names |
|----------|-----------|----------|-------------|
| Claude Code | `.claude/` | `settings.template.json` | `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` |
| Codex CLI | `.codex/` | `settings.template.codex.json` | `on_agent_message`, `pre_tool_call`, `post_tool_call`, `on_session_end` |

### Hook Scripts (shared across platforms)

All hook scripts live in `assets/hooks/` and are platform-agnostic. They use shared helpers:
- `hook-input.sh` — Unified input parsing (supports both Claude Code and Codex CLI env vars / JSON)
- `hook-output.sh` — Platform-aware structured output (auto-detects platform for JSON responses)

Default hook coverage:
- User prompt guards: `prompt-guard.sh`, `phase-tracker.sh`
- Pre-tool guards: `worktree-guard.sh`, `tdd-guard-hook.sh`, `pre-code-change.sh`, `plan-gate.sh`, `research-gate.sh`
- Pre-tool (Bash): `pre-commit-lint.sh`, `pre-push-test.sh`, `immutable-layer-guard.sh`
- Post-tool guards: `anti-simplification.sh`, `doc-drift-guard.sh`, `atomic-pending.sh`, `plan-sync-reminder.sh`
- Post-bash guards: `post-bash.sh`, `atomic-commit.sh`
- Session monitor: `context-pressure-hook.sh`
- Session end: `session-end-reminder.sh`
- Shared helpers: `hook-input.sh`, `hook-output.sh`

### Auto-Installation

Hooks are **automatically installed** during Phase 3 (Init), Update Phase 4, and Convert Phase 4.
The skill auto-detects the package manager and runs `setup-hooks.sh --platform both` without user intervention.

Manual installation:
```bash
# Both platforms (default)
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project

# Codex CLI
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project --platform codex

# Claude Code only
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project --platform claude
```
