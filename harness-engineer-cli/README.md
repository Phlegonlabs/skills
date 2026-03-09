# Harness Engineer CLI

An agent-first project framework based on Harness Engineering principles.
Works with **Claude Code** and **Codex** on **Windows**, macOS, and Linux.

## What it does

Two modes:

- **Greenfield** — New project from scratch. Product discovery → PRD → scaffold → execution.
- **Retrofit** — Existing project. Analyze the codebase, add harness layer on top.

Both modes generate a unified CLI (`scripts/harness.ts`) that agents use to
autonomously loop through tasks: pick → start → code → validate → commit → done → repeat.

## How to install

Add this folder as a skill in claude.ai. The skill triggers when you say things like
"new project", "bootstrap", "scaffold", "add harness to my project", or "retrofit".

## Execution Modes

The generated project supports two execution modes. You choose which one during setup,
and can switch anytime by editing the config files.

### Auto Mode (default)

The agent runs the full task loop without asking permission. It only pauses at
Human quality checkpoints (security changes, merge failures, blocked tasks).

This is the default because the harness CLI + git hooks + CI already enforce all
rules mechanically. The agent can't commit bad code — the hooks reject it.

**Claude Code — `.claude/settings.json`:**
```json
{
  "permissions": {
    "allowedTools": [
      "Read", "Write",
      "Bash(git *)",
      "Bash(<package-manager> *)",
      "Bash(npx tsx scripts/harness.ts *)",
      "Bash(npx tsx scripts/check-commit-msg.ts *)",
      "Bash(npx lint-staged)"
    ],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

**Codex — `.codex/config.toml`:**
```toml
approval_policy = "never"

[sandbox]
sandbox_mode = "workspace-write"
```

### Menu Mode (supervised)

The agent pauses before every shell command and asks for your approval.
Use this when you want to review each step, or when working on sensitive code.

**To switch Claude Code to Menu Mode:**

Edit `.claude/settings.json` — remove the harness commands from `allowedTools`:
```json
{
  "permissions": {
    "allowedTools": ["Read", "Write"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

Now the agent will ask "Allow Bash(npx tsx scripts/harness.ts validate)?" before
each command. You press Y to approve or N to skip.

**To switch Codex to Menu Mode:**

Edit `.codex/config.toml`:
```toml
approval_policy = "on-request"
```

Now Codex pauses for every command and waits for your approval.

### Switching between modes

| Want | Claude Code | Codex |
|------|------------|-------|
| **Auto → Menu** | Remove `Bash(...)` entries from `allowedTools` | Change `approval_policy` to `"on-request"` |
| **Menu → Auto** | Add `Bash(...)` entries back to `allowedTools` | Change `approval_policy` to `"never"` |

Changes take effect on the next agent session. No restart needed — just start a new session.

### When to use which

| Situation | Recommended mode |
|-----------|-----------------|
| Routine feature work | Auto |
| First time using the harness | Menu (to see what the agent does) |
| Security-sensitive code | Menu |
| Unfamiliar codebase (retrofit) | Menu for first milestone, then Auto |
| Parallel agents on multiple milestones | Auto |
| Debugging a blocked task | Menu |

## File structure

```
harness-engineer-cli/
├── SKILL.md                        ← Main skill file (claude.ai reads this)
├── README.md                       ← You are here
└── references/                     ← Templates used during generation
    ├── harness-cli.md              ← The CLI source code + schema + hooks
    ├── eslint-configs.md           ← ESLint flat configs per framework
    ├── project-configs.md          ← tsconfig, prettier, vitest, Docker, CI configs
    ├── gitignore-templates.md      ← .gitignore templates per stack
    └── execution-runtime.md        ← Agent guidelines (context budget, parallel, quality gates)
```

## What gets generated into your project

```
your-project/
├── AGENTS.md + CLAUDE.md           ← Agent instructions (identical content)
├── ARCHITECTURE.md                 ← Domain map, dependency layers
├── docs/
│   ├── PRD.md                      ← Product requirements
│   ├── PLAN.md                     ← Milestones + tasks
│   ├── progress.json               ← Machine-readable state (CLI manages this)
│   ├── learnings.md                ← Agent learnings log
│   └── ...
├── scripts/
│   ├── harness.ts                  ← The CLI entry point — thin command router
│   ├── check-commit-msg.ts         ← Commit message format enforcer
│   └── harness/
│       ├── config.ts               ← Constants, colors, helpers
│       ├── types.ts                ← All interfaces
│       ├── state.ts                ← progress.json + PLAN.md I/O
│       ├── plan-utils.ts           ← Row-level PLAN.md table parser (shared)
│       ├── recovery.ts             ← Install retry + milestone board recovery
│       ├── worktree.ts             ← Worktree commands + agent lifecycle
│       ├── tasks.ts                ← init, status, next, start, done, block, reset
│       ├── validate.ts             ← lint, type-check, test, file-guard
│       └── quality.ts              ← merge-gate, stale-check, changelog
├── schemas/
│   └── progress.schema.json        ← Validates progress.json
├── .claude/settings.json           ← Claude Code config (auto mode)
├── .codex/config.toml              ← Codex config (auto mode)
├── .husky/                         ← Git hooks (pre-commit, commit-msg, pre-push)
└── ...                             ← Scaffold (src/, tests/, configs, CI, Docker)
```

## CLI commands

```
# Worktree management (milestone isolation — run from main repo root)
harness worktree:start <M-id>   Create branch + worktree + install + init + auto-start
harness worktree:finish <M-id>  Merge milestone → main, remove worktree, update progress

# Session (run inside the milestone worktree)
harness init              Session boot: sync plans, stale check, print status
harness init --auto-start Session boot + auto-claim first available task
harness status            Print current milestone, task, blockers, progress

# Task loop (inside worktree)
harness next              Find and print the next unblocked task
harness start <id>        Claim a task → auto-updates progress.json + PLAN.md
harness validate          lint:fix → lint → type-check → test
harness validate:full     + integration + e2e + file-guard
harness done <id>         Complete a task → auto-updates state + commit hash + git checkout .
harness block <id> <msg>  Mark task blocked, log reason

# Quality gates
harness merge-gate        Full gate check before worktree:finish
harness stale-check       Detect stale docs, env, plans
harness file-guard        Check no source file exceeds 500 lines
harness schema            Validate progress.json against JSON Schema
harness changelog         Generate release notes from commit messages
harness recover           Auto-detect and fix milestone board inconsistencies
```

## Requirements

- Node.js 18+
- Git
- One of: pnpm, bun, or npm
- `tsx` (added automatically as a dev dependency)
