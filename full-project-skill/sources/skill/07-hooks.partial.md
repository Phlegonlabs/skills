## Hooks

Install project hooks via `scripts/setup-hooks.sh`. See `assets/hooks/settings.template.json`
for the full hook wiring. Hook scripts live in `assets/hooks/` and are copied to
`.claude/hooks/` by the installer.

These hooks are Claude Code specific and depend on Claude Code hook events + JSON protocol.
They are not compatible with Codex CLI hooks.

Default hook coverage:
- User prompt guards: `prompt-guard.sh`, `phase-tracker.sh`
- Pre-write guards: `worktree-guard.sh`, `tdd-guard-hook.sh`, `pre-code-change.sh`, `plan-gate.sh`, `research-gate.sh`
- Post-write guards: `anti-simplification.sh`, `doc-drift-guard.sh`, `atomic-pending.sh`
- Post-bash guards: `post-bash.sh`, `atomic-commit.sh`
- Session monitor: `context-pressure-hook.sh`
- Shared helper: `hook-input.sh`

Inline template hooks retained in settings:
- pre-commit lint/typecheck
- pre-push test
- immutable-layer guard
- plan-sync guard
- session-end reminder

During Phase 3 (Next Steps), hooks MUST be installed:
```bash
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project
```
