# Harness Engineer CLI

An agent-first project framework based on Harness Engineering principles.
Works with **Claude Code** and **Codex** on **Windows**, macOS, and Linux.

## What it does

Two modes:

- **Greenfield** — New project from scratch. Product discovery → PRD → scaffold → execution.
- **Retrofit** — Existing project. Analyze the codebase, add harness layer on top.

Both modes generate a CLI that agents use to autonomously loop through tasks:
pick → start → code → validate → commit → done → repeat.

- **Node/TS projects** — TypeScript CLI (`scripts/harness.ts` + `scripts/harness/` modules)
- **Non-Node projects** (Python, Go, Rust without Node) — Shell CLI (`scripts/harness.sh` + `Makefile`)
The animated chain map is in [flow-visualizer.html](flow-visualizer.html).

> **`references/replay-protocol.md` is for framework-level development only.**
> It documents the SOP for verifying changes to this skill's own reference files across
> downstream fixture repos. It is NOT part of any project's task loop or completion criteria.
> Per-project completion is defined by the Idle Protocol in `references/skill-execution.md`:
> all milestones merged → changelog reviewed → human confirms release tag.

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
├── flow-visualizer.html            ← Interactive workflow chain map (open in browser)
└── references/                     ← Templates used during generation
    ├── skill-greenfield.md         ← Greenfield workflow (discovery → PRD → scaffold)
    ├── skill-retrofit.md           ← Existing-project retrofit workflow
    ├── skill-desktop.md            ← Desktop-specific reference (Electron/Tauri)
    ├── skill-mobile.md             ← Mobile-specific reference (Expo/EAS)
    ├── skill-auth.md               ← Auth-specific reference
    ├── skill-artifacts.md          ← Generated docs / config artifact templates
    ├── skill-execution.md          ← Post-scaffold runtime + task-loop handoff
    ├── harness-cli.md              ← The CLI source code + schema + hooks (TypeScript)
    ├── scaffold-templates.md       ← CLI scaffold command templates (MCP, SKILL.md, Cloudflare, agent)
    ├── harness-native.md           ← Shell-based CLI alternative for non-Node projects
    ├── eslint-configs.md           ← ESLint flat configs per framework
    ├── project-configs.md          ← TS, Python, Go, Rust, workspace, Docker, CI configs
    ├── gitignore-templates.md      ← .gitignore templates per stack
    ├── execution-runtime.md        ← Agent guidelines (context budget, parallel, quality gates)
    └── replay-protocol.md          ← Downstream replay / fixture verification SOP
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
│   ├── harness.ts                  ← [Node/TS] CLI entry point — thin command router
│   ├── check-commit-msg.ts         ← [Node/TS] Commit message format enforcer
│   ├── harness/                    ← [Node/TS] CLI modules (config, tasks, quality…)
│   └── harness.sh                  ← [Non-Node] Shell-based CLI alternative
├── Makefile                        ← [Non-Node] validate / done / next / block targets
├── schemas/
│   └── progress.schema.json        ← Validates progress.json
├── .claude/settings.json           ← Claude Code config (auto mode)
├── .codex/config.toml              ← Codex config (auto mode)
├── .husky/                         ← [Node/TS] Git hooks (pre-commit, commit-msg, pre-push)
├── .pre-commit-config.yaml         ← [Python/Go] Hook alternative to husky
├── .githooks/                      ← [Rust] Hook alternative to husky
└── ...                             ← Scaffold (src/, tests/, configs, CI, Docker)
```

## CLI commands

```
# Worktree management (milestone isolation — run from main repo root)
harness worktree:start <M-id>   Create branch + worktree + install + init + auto-start
harness worktree:finish <M-id>  Rebase → merge → archive plans → push → cleanup
harness worktree:reclaim <M-id> Reclaim a stale/abandoned milestone and reopen its worktree
harness worktree:status         Show worktrees, agents, auto-finish jobs, and merge readiness
harness migrate                 Refresh harness-managed runtime folders + schema after upgrades
harness sync-template           Alias of migrate

# Session (run inside the milestone worktree)
harness init              Session boot: sync plans, stale check, print status
harness init --auto-start Session boot + auto-claim first available task
harness status            Print current milestone, task, blockers, progress

# Task loop (inside worktree)
harness next              Find and print the next unblocked task
harness start <id>        Claim a task → auto-updates progress.json + PLAN.md
harness validate          lint:fix → lint → type-check → test
harness validate:full     + integration/e2e when matching test files exist + file-guard
harness done <id>         Complete a task → auto-updates state + commit hash + git checkout .
harness block <id> <msg>  Mark task blocked, log reason

# Quality gates
harness merge-gate        Full gate check before worktree:finish
harness stale-check       Detect stale docs, env, plans
harness file-guard        Check no source file exceeds 500 lines
harness schema            Validate progress.json against JSON Schema
harness changelog         Generate release notes from commit messages
harness recover           Auto-detect and fix milestone board inconsistencies

# Planning (add new work mid-project)
harness plan:status       Show project progress overview + pending plan files
harness plan:apply [file] Parse plan → analyze state → insert milestones + tasks + deps

# Scaffold (inject capability templates — no web search needed)
harness scaffold mcp            MCP server: src/tools/, server.ts, tests
harness scaffold skill           SKILL.md agent discovery file
harness scaffold llms-txt        llms.txt for LLM discoverability
harness scaffold milestone:agent Pre-built 11-task milestone for agent work
harness scaffold agent-card      A2A Agent Card (/.well-known/agent.json)
harness scaffold agent-observe   Tool observability: metrics, latency, errors
harness scaffold agent-auth      Auth + rate limit for remote SSE
harness scaffold agent-pay       x402 micropayments + Stripe metered billing
harness scaffold agent-test      MCP protocol compliance tests
harness scaffold agent-schema-ci CI: detect SKILL.md vs code schema drift
harness scaffold agent-version   Tool versioning strategy docs
harness scaffold agent-client    Multi-agent client: discover + call remotes
harness scaffold agent-prompts   MCP Prompts: pre-built prompt templates
harness scaffold agent-webhook   Long-running task + webhook callback
harness scaffold agent-cost      Per-call cost estimation + audit log
harness scaffold cloudflare      wrangler.toml + .dev.vars + CI
```

## Requirements

**Node/TS projects (TypeScript CLI):**
- Node.js 18+
- Git
- One of: pnpm, bun, or npm
- `tsx` (added automatically as a dev dependency)

**Non-Node projects (Shell CLI — Python, Go, Rust):**
- Git
- `jq` (JSON processor — for `scripts/harness.sh`)
- `bash` 4+ (macOS ships bash 3; install bash via Homebrew if needed)
- Language runtime: Python 3.11+ / Go 1.22+ / Rust stable
- No Node.js or npm required — the shell CLI handles all harness operations

## Validation Strategy

This repo is a doc-first skill bundle, so template changes should be verified by replaying them
into representative fixture outputs or downstream repos before being treated as done.

Recommended minimum replay matrix:

- Web app, single-package TypeScript scaffold
- Desktop app scaffold (`Electron` or `Tauri`)
- Mixed-language monorepo (`apps/web` in TS + backend in Python, Go, or Rust)

Snapshot or diff at least these generated artifacts:

- `docs/PLAN.md`
- `docs/progress.json`
- `schemas/progress.schema.json`
- `scripts/harness.ts` and `scripts/harness/`
- Stack-native manifests such as `package.json`, `pyproject.toml`, `go.work`, and `Cargo.toml`

If the change touches harness runtime behavior, CI, or generated workflow rules, replay it in at
least one real downstream project or fixture repo and confirm the generated project still passes
`harness validate`.
