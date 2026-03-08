## Artifact Generation Rules

### AGENTS.md + CLAUDE.md (Identical Content)

These two files have **the same content**. Generate one, copy to the other.
AGENTS.md is for Codex. CLAUDE.md is for Claude Code. Same rules, no divergence.

#### What is TEMPLATED (copy verbatim into every project):

Only the Iron Rules section is fixed:

```
## Iron Rules — Non-Negotiable

These rules are absolute. No exceptions. No workarounds. No "just this once."

### 1. 500-Line Hard Ceiling + Proactive Modularization
No single **source code file** may exceed 500 lines. But don't wait until 500 — split
proactively. If a file is approaching ~250 lines and has more than one responsibility,
extract a module NOW. Every file should have a single, clear purpose.

**Proactive split triggers (act on ANY of these):**
- File has 2+ unrelated sections → extract to separate modules
- File has functions used by multiple other files → move to a shared module
- A single function exceeds ~80 lines → extract helpers or decompose
- You're adding a new feature to an existing file and it'll push past ~300 lines → new module
- A component renders AND fetches data AND handles state → split by concern
- The harness CLI itself follows this rule: entry point ~50 lines, 6 focused modules, each <350 lines

**How to decompose:**
- Group by domain/responsibility, not by file type (don't put all types in one file)
- Each module exports a clear, minimal API — internal helpers stay private
- Prefer deep module trees (modules/auth/service.ts, modules/auth/routes.ts) over flat ones
- Re-export from index.ts barrel files when the module API is stable

**Documentation files are exempt from the 500-line limit.** These files may
(and often will) exceed 500 lines — do NOT split them:
- `docs/PRD.md` — grows with the project
- `docs/PLAN.md` — grows with each sprint
- `AGENTS.md` / `CLAUDE.md` — must stay in one file (agents read them whole)
- `ARCHITECTURE.md`, `docs/site/*.md`, `docs/learnings.md`, any file under `docs/`

If `PLAN.md` grows past ~1000 lines, archive completed milestone sections to
`docs/exec-plans/completed/` rather than splitting the file. The CLI handles this
automatically via `harness done` when a milestone completes.

### 2. Zero Compatibility Code
No polyfills. No shims. No backward-compat wrappers.
Write for the target runtime and version in project config. Period.
If a dependency requires compat hacks, replace the dependency.

### 3. Conflict = Delete and Rebuild
If a module conflicts with existing code — type mismatches, circular deps, API surface
disagreements — do NOT patch around it. Delete and rebuild from scratch.
Code is cheap. Tokens are infinite. Architectural clarity is priceless.

### 4. First Principles Programming
Every function, module, and abstraction must justify its existence from first principles.
Ask: What is this actually trying to do? What is the simplest correct way?
If you can't explain the WHY in one sentence, the code shouldn't exist.

### 5. Frontend = Always Use frontend-design Skill
When generating any frontend code (components, pages, layouts, styles), ALWAYS read
and follow `docs/frontend-design.md` first. This file is bundled in the project.
No exceptions. Even for "small" UI changes.

### 6. Secrets Never Touch Git
.env files are NEVER committed. Not even "example" values that look like real keys.
- `.env` is in .gitignore from day zero — non-negotiable
- `.env.example` contains only KEY_NAME=placeholder pairs, never real values
- All secrets load from environment variables at runtime, never hardcoded
- If you see a string that looks like a key/token/password in source code, extract it to env immediately

### 7. Production Ready Standard
Every milestone must be shippable. Code that "works on my machine" is not done.
- Error handling: every external call (API, DB, file I/O) has try/catch or error boundary
- Input validation: every endpoint/command validates input before processing
- Logging: every error is logged with context (request ID, user, operation)
- No console.log in production code — use structured logger
- No hardcoded URLs, ports, or credentials — all from env/config
- No TODO/FIXME/HACK comments — if it's not fixed, it's a task in PLAN.md
- Tests cover the happy path AND at least one error path per function
- Build produces zero warnings (not just zero errors)
- README/docs accurately describe what the code actually does right now
```

#### What is DYNAMICALLY GENERATED (unique to each project):

Everything else must be written fresh from the user's actual project context.
DO NOT use generic placeholders. DO NOT copy from the template — write it.

Dynamically generate these sections:

- **Project overview** — What THIS project does, its stack, its purpose. From the PRD.
- **Quick start** — Real commands for THIS project's package manager and stack.
  e.g., `bun install && bun dev` not "install deps and run dev server"
  Include `docker-compose up -d` if Docker is configured.
- **Repository map** — Pointers to the actual docs in THIS project.
- **Architecture rules** — Dependency layers, module boundaries, import restrictions
  specific to THIS project's domain. Derived from ARCHITECTURE.md.
- **Error handling conventions** — Point to `src/lib/errors.ts`, explain the error
  class hierarchy. "All errors thrown in application code must extend AppError."
- **Logging conventions** — "Use the structured logger from `src/lib/logger.ts`.
  Never use console.log in production code."
- **Feature flag conventions** — "Every new user-facing feature ships behind a flag.
  Check `src/lib/feature-flags.ts`. Remove flag when feature is stable."
- **Analytics conventions** — "Use `trackEvent()` from `src/lib/analytics.ts`.
  Never call GA/Posthog directly."
- **Dev environment tips** — Real tips for THIS stack. pnpm project gets pnpm commands.
  Go project gets Go tips. Include Docker commands if applicable.
- **Testing instructions** — The full testing loop for THIS project. Include:
  - The exact `lint:fix`, `lint`, `type-check`, `test`, `validate` commands
  - How to run a single test file or test case
  - The rule: run `validate` before EVERY commit, no exceptions
- **Deploy instructions** — How to deploy THIS project to the chosen target.
  Actual commands, not generic advice.
- **PR conventions** — Scope names from THIS project's actual modules/domains.

- **Plan File Convention** — Where plan files go (critical for Codex compatibility):

```
## Plan Files

All plan files MUST be written to `docs/exec-plans/active/`.

For Claude Code: this is handled automatically via .claude/settings.json (plansDirectory).
For Codex: when creating a plan, ALWAYS write it to `docs/exec-plans/active/<descriptive-name>.md`.
  Do NOT write plans to ~/.codex/ or any other location outside the project.

Plan files in docs/exec-plans/active/ are detected at Session Init and synced into
PLAN.md + progress.json. This is how new work enters the execution loop.

Naming convention: `YYYY-MM-DD-<short-description>.md`
Example: `2026-03-08-add-user-profile-editing.md`

After a plan is synced to PLAN.md, it stays in exec-plans/active/ as reference.
When the milestone it created is completed, move it to exec-plans/completed/.
```

- **Session Init Protocol** — What the agent does FIRST when starting:

```
## Session Init — Do This First, Every Time

Run: <pkg-mgr> run harness init

This automatically:
1. Syncs any new plan files from docs/exec-plans/active/
2. Runs stale detection
3. Prints current status (milestone, task, blockers, progress)

If a task was in_progress with uncommitted changes:
→ run harness validate. Green → commit. Red → fix first.

Context budget:
- AGENTS.md / CLAUDE.md + progress.json + current PLAN section: ≤ 30%
- Source files for current task: ≤ 30%
- Remaining ≥ 40% for code generation and reasoning
- Overloaded? → commit what works, start fresh session.

After harness init completes, proceed DIRECTLY to the Task Execution Loop.
Do not wait for user confirmation. Start working immediately.
```

- **Task Execution Loop** — Run this loop autonomously. Do NOT stop between tasks
  to ask the user for permission. Keep looping until the milestone is done or you
  hit a Human quality checkpoint.

```
## Task Execution Loop

Run this loop continuously. Do NOT pause between tasks.

<pkg-mgr> run harness next        # Find next unblocked task
<pkg-mgr> run harness start M1-003  # Claim it → auto-updates progress.json + PLAN.md

# Write code for the task. Load only relevant files.

<pkg-mgr> run harness validate    # lint:fix → lint → type-check → test
git add -A && git commit -m "[M1-003] <what you did>"

<pkg-mgr> run harness done M1-003   # Complete → auto-updates progress + PLAN + commit hash

# DO NOT STOP HERE. Immediately run harness next and continue.
# The loop ends when:
#   - harness next says "milestone complete" → run harness merge-gate
#   - harness next says "all tasks blocked" → report to user and wait
#   - A Human quality checkpoint is triggered (security, architecture, merge failure)

If validate fails 3x:
<pkg-mgr> run harness block M1-003 "reason it failed"
# CLI stashes changes, adds blocker. Run harness next to continue with next task.
```

- **Merge Gate** — When all tasks in a milestone are ✅:

```
## Milestone Merge Gate

<pkg-mgr> run harness merge-gate

This runs: validate:full + stale-check + changelog.
If green, follow the printed instructions to merge + tag.
```

- **Stale Detection** — Run anytime, or automatic via `harness init`:

```
## Stale Detection

<pkg-mgr> run harness stale-check

Automatically checks: .env.example sync, PLAN vs progress.json,
new modules not in ARCHITECTURE.md, unsynced plan files, dead doc links.
```

- **Adding New Work** — Plan mode → CLI handles the rest:

```
## Adding New Work

To add new work, the user enters plan mode:
- Claude Code: press Shift+Tab to enter plan mode
- Codex: switch to plan mode via the Codex UI

Describe what to build. The plan file saves to docs/exec-plans/active/.
Exit plan mode, then run:

<pkg-mgr> run harness init

The CLI detects the new plan. Parse it into PLAN.md + progress.json,
then resume the Task Execution Loop.

For tiny changes: just tell the agent to create a task directly.
```

- **Git Workflow** — Worktree per milestone rules (the workflow is standard but
  project name, branch names, and commands should use the real project name):

```
## Git Workflow — Worktree per Milestone

### Branch Strategy
Each milestone in PLAN.md gets its own git worktree and branch.
The CLI enforces this — task commands (next/start/done) refuse to run on main.

# From main repo root:
<pkg-mgr> run harness worktree:start M<n>
cd ../<project>-m<n>
<pkg-mgr> install
<pkg-mgr> run harness init   # registers agent, syncs state

# All work happens here with atomic commits
# Task commands only work inside a worktree — not on main

# Periodically rebase onto main (especially after other milestones merge):
<pkg-mgr> run harness worktree:rebase

# When complete and all tests pass:
<pkg-mgr> run harness merge-gate
cd ../<project>
<pkg-mgr> run harness worktree:finish M<n>
# → checks dependency order (blocks if deps not merged)
# → rebases onto main (reports conflicts if any)
# → merges, validates, cleans up worktree

### Atomic Commits
Every task follows this exact loop. No shortcuts. No skipping steps.

1. Write or modify code for ONE task
2. Run lint with auto-fix: <lint-fix-command>
3. If lint auto-fix changed files → review changes, stage them
4. Run lint check (no fix): <lint-check-command>
5. If lint errors remain → fix manually, go to step 4
6. Run type-check: <type-check-command>
7. If type errors → fix, go to step 4
8. Run relevant test(s): <test-command>
9. If tests fail → fix code, go to step 2 (full loop restart)
10. ALL green → commit immediately
11. Move to next task

Commit format: [M<n>-<task_id>] <what changed>

NEVER commit with lint warnings, type errors, or failing tests.
The loop restarts from step 2 on ANY failure — no partial fixes.

### Parallel Milestones
Independent milestones can run in parallel (one agent per worktree).
The CLI coordinates via progress.json agents array:
- worktree:start checks no other active agent has claimed the milestone
- init registers the agent with a heartbeat (updated on every command)
- worktree:status shows all agents, heartbeats, and merge readiness
- Stale agents (heartbeat >2h) are reclaimable

After another milestone merges into main, rebase your worktree:
  <pkg-mgr> run harness worktree:rebase

### Milestone Completion Checklist
Before merging back to main, run the FULL gate — every check must pass:

<lint-fix-command>              # auto-fix what it can
<lint-check-command>            # must be zero errors, zero warnings
<type-check-command>            # must be zero errors
<full-test-command>             # entire test suite must pass
<file-line-count-check>         # no file exceeds 500 lines

If ANY check fails → fix in the worktree, commit the fix, re-run ALL checks.
Only merge when every gate is green.

- [ ] Lint: zero errors, zero warnings
- [ ] Types: zero errors
- [ ] Tests: full suite passes
- [ ] No file exceeds 500 lines
- [ ] PLAN.md updated (tasks marked done, milestone status updated)
- [ ] Acceptance criteria from PRD verified for each completed story
- [ ] exec-plans/active/ plan moved to exec-plans/completed/
- [ ] Production ready: no TODO/FIXME/HACK in committed code
- [ ] Production ready: all errors handled (no unhandled promise rejections, no bare throws)
- [ ] Production ready: build produces zero warnings
- [ ] Production ready: no console.log in production paths (use logger)
```

### ARCHITECTURE.md (Dynamically Generated)

This file is the technical blueprint. Generate it entirely from the project's actual
domain structure, tech stack, and patterns. Include:

```markdown
# Architecture: <Project Name>

## Domain Map
Visual or text representation of the project's domains and how they relate.
For a web app this might be: Auth, Users, Products, Orders, Payments, Notifications.
For a CLI tool: Parser, Commands, Config, Output.
For an Agent / MCP server: Server, Tools, Resources, Prompts, API Client.
For a Desktop app: Main Process, Renderer, Preload, IPC, Shared Types.

## Dependency Layers
Strict ordering — each layer can only import from layers to its left:

Web App / API:
  Types → Config → Lib → Service → Controller/Handler → UI/CLI

CLI Tool:
  Types → Config → Lib → Commands → Entry Point

Agent / MCP:
  Types → Config → Lib → API Client → Tools/Resources → Server

Desktop (Electron):
  Shared → Preload → Main (IPC, lifecycle) | Renderer (UI)

Enforced by ESLint import rules (JS/TS) or equivalent linter. Violations fail lint.

## Package / Module Structure
Map of src/ directories to domains. Adapt to project type:

**Web App / API:**
src/
├── lib/          ← shared utilities (errors, logger, feature-flags, analytics, env)
├── modules/
│   ├── auth/     ← Auth domain (routes, service, model, tests)
│   ├── users/    ← Users domain
│   └── ...
├── middleware/    ← cross-cutting (error handler, auth guard, request logger)
└── config/       ← app config, env validation

**CLI Tool:**
src/
├── commands/     ← one file per command (init, deploy, config, etc.)
├── lib/          ← shared utilities (errors, logger, config loader, output formatters)
├── prompts/      ← interactive prompts (if applicable)
└── index.ts      ← entry point: parse args, dispatch

**Agent / MCP Server:**
src/
├── tools/        ← one file per MCP tool
├── resources/    ← MCP resources
├── prompts/      ← MCP prompt templates
├── lib/          ← shared utilities + external API clients
└── server.ts     ← MCP server entry (stdio/SSE transport)

**Desktop App (Electron):**
src/
├── main/         ← main process (Node.js — lifecycle, IPC, menus)
├── renderer/     ← renderer process (React/Vue — UI)
├── preload/      ← preload scripts (context bridge)
└── shared/       ← types shared between main and renderer

## Error Handling Pattern
- All application errors extend `AppError` from `src/lib/errors.ts`
- HTTP layer catches errors via global error middleware
- Error responses: `{ error: { code: "MACHINE_READABLE", message: "Human readable", details? } }`
- Log all errors with structured logger, never swallow silently

## Logging Pattern
- Use `src/lib/logger.ts` everywhere. Never `console.log` in production code.
- Request middleware injects `requestId` into every log entry
- Levels: debug (dev only), info (business events), warn (recoverable), error (failures)

## Feature Flag Pattern
- `src/lib/feature-flags.ts` — all new user-facing features ship behind a flag
- Flag lifecycle: create → enable for % → monitor → remove when stable
- Dead flags (enabled for 100% for >2 weeks) get cleaned up

## Analytics Pattern
- `src/lib/analytics.ts` — provider-agnostic interface
- Core events defined in a central events file
- Never call tracking provider directly — always go through the service

## Deploy Architecture
- Target: <chosen deploy target — e.g. Vercel, Cloudflare Pages, VPS (Hetzner), Fly.io, etc.>
- Method: <deployment method — e.g. Git push auto-deploy, Docker Compose + SSH, Kamal, Wrangler CLI, etc.>
- Build: <build command and output — e.g. `pnpm run build` → `.next/` or `dist/`>
- CI/CD: <pipeline provider — GitHub Actions / GitLab CI / platform auto-deploy>
- Config file: <platform config — vercel.json / wrangler.toml / fly.toml / docker-compose.yml / deploy.yml>
- Environment: <how env vars are injected — platform dashboard, .env files, Docker env, secrets manager>
- Health: /health and /health/ready endpoints
- Preview: <preview/staging deploy strategy — Vercel preview deploys / Fly.io staging app / Docker staging compose>

## Key Decisions
Link to docs/design-docs/ for detailed ADRs (Architecture Decision Records).
```

### PLAN.md — Granular Decomposition

The plan must be broken down as finely as possible. Each task should be a single
atomic unit of work — something one agent can complete in one session.

**Decomposition rules:**
- Each Epic from the PRD becomes a Milestone (or split further if the epic is large)
- Each User Story becomes a group of tasks within that milestone
- Each task must be completable in ≤ 4 hours of work
- If a task feels bigger than 4h, split it further
- Tasks must reference their parent story ID for traceability
- Every task must have a clear "done when" (from story acceptance criteria)

**Milestone granularity guidelines:**
- Prefer 5–15 tasks per milestone. More than 15 → split the milestone.
- Each milestone must be independently shippable (tests pass, lint clean)
- Dependencies between milestones must be explicit

```markdown
# Project Plan: <Project Name>

## Traceability
Requirements (PRD §4) → Epics (PRD §9) → Stories (PRD §9) → Tasks (below)

## Current Phase: <Phase Name>

## Milestones

### M1: <Name from Epic E1> (Target: <timeframe>)
**Status:** ⬜ Not Started
**Branch:** `milestone/M1`
**Worktree:** `../<project>-M1`
**Covers:** Epic E1 (FR-001, FR-002)
**Depends on:** None

| Task ID | Story | Task | Done When | Status | Commit |
|---------|-------|------|-----------|--------|--------|
| M1-001 | E1-S01 | Create user model + migration | Schema matches PRD data model, migration runs clean | ⬜ | — |
| M1-002 | E1-S01 | Implement signup endpoint | POST /auth/signup returns 201, validates email format | ⬜ | — |
| M1-003 | E1-S01 | Add password hashing | Passwords stored as bcrypt hash, never plaintext | ⬜ | — |
| M1-004 | E1-S01 | Write signup integration test | Test covers valid signup, duplicate email, weak password | ⬜ | — |
| M1-005 | E1-S02 | Implement email confirmation flow | Clicking link activates account, expired link returns 410 | ⬜ | — |
| M1-006 | E1-S02 | Write confirmation integration test | Test covers valid confirm, expired link, already confirmed | ⬜ | — |
| M1-007 | — | Setup CI for auth module | CI runs tests + lint on PR to milestone/M1 | ⬜ | — |

### M2: <Name from Epic E2> (Target: <timeframe>)
**Status:** ⬜ Not Started
**Branch:** `milestone/M2`
**Worktree:** `../<project>-M2`
**Covers:** Epic E2 (FR-003, FR-004)
**Depends on:** M1

| Task ID | Story | Task | Done When | Status | Commit |
|---------|-------|------|-----------|--------|--------|
| M2-001 | E2-S01 | ... | ... | ⬜ | — |
...

## Decision Log
| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|

## Known Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
```

**Example tasks for other project types (adapt to actual PRD):**

CLI Tool example milestones:
```markdown
### M1: Core CLI Scaffold + First Command
| Task ID | Story | Task | Done When | Status | Commit |
|---------|-------|------|-----------|--------|--------|
| M1-001 | E1-S01 | Set up argument parser (Commander/Yargs) | `<cli> --help` prints usage, `<cli> --version` prints version | ⬜ | — |
| M1-002 | E1-S01 | Implement config loader | Reads ~/.myapp/config.json, falls back to defaults, validates schema | ⬜ | — |
| M1-003 | E1-S01 | Implement `init` command | Creates config file, prints confirmation, errors if already exists | ⬜ | — |
| M1-004 | E1-S01 | Add output formatters (table/JSON/plain) | `--format json` returns valid JSON, `--format table` prints aligned table | ⬜ | — |
| M1-005 | E1-S01 | Add error handling + exit codes | Errors print to stderr, exit 1 on failure, exit 0 on success | ⬜ | — |
| M1-006 | — | Write unit tests for init + config | Tests cover: first run, existing config, invalid config, permissions | ⬜ | — |
```

Agent / MCP Server example milestones:
```markdown
### M1: MCP Server Scaffold + First Tool
| Task ID | Story | Task | Done When | Status | Commit |
|---------|-------|------|-----------|--------|--------|
| M1-001 | E1-S01 | Set up MCP server with stdio transport | Server starts, responds to `initialize` request | ⬜ | — |
| M1-002 | E1-S01 | Implement tool registry + schema validation | Tools listed in `tools/list`, input schemas validated | ⬜ | — |
| M1-003 | E1-S01 | Implement first tool: `search` | Tool accepts query, returns results, handles empty/error states | ⬜ | — |
| M1-004 | E1-S01 | Add structured error responses | Tool errors return proper MCP error codes, not raw exceptions | ⬜ | — |
| M1-005 | — | Write integration test (tool call lifecycle) | Test: initialize → tools/list → tools/call → validate response | ⬜ | — |
```

### Scaffold Generation

Generate actual source files appropriate to the chosen stack. Not empty dirs.

**BEFORE generating any config file, read the reference templates:**
- `references/gitignore-templates.md` — .gitignore assembled per stack
- `references/eslint-configs.md` — ESLint flat configs per framework
- `references/project-configs.md` — tsconfig, prettier, vitest, Docker, CI, Python configs
- `references/harness-cli.md` — the harness CLI, JSON Schema, git hooks, lint-staged, assembly checklist
- `references/execution-runtime.md` — agent guidelines: parallel protocol, context budget, quality gates

Never write configs or scripts from memory. Always reference these files and adapt.
The templates use the strictest settings — never downgrade. If strict rules cause errors,
fix the code, not the config.

**Mandatory test & lint infrastructure (every project, no exceptions):**

For JS/TS projects, always generate:
- `eslint.config.js` (flat config) with strict rules appropriate to the framework
- `.prettierrc` + `.prettierignore`
- `tsconfig.json` with `strict: true` if TypeScript
- Test framework config (vitest.config.ts, jest.config.ts, etc.)
- NPM scripts in package.json:
  ```json
  {
    "scripts": {
      "harness": "tsx scripts/harness.ts",
      "lint": "eslint . --report-unused-disable-directives --max-warnings 0",
      "lint:fix": "eslint . --fix",
      "type-check": "tsc --noEmit",
      "test": "vitest run",
      "test:integration": "vitest run --project integration",
      "test:e2e": "vitest run --project e2e",
      "prepare": "husky"
    }
  }
  ```
  (Adapt command prefix to chosen package manager: `pnpm`, `bun`, or `npm run`)

**Harness CLI (every project — see `references/harness-cli.md`):**

Add `tsx` as a dev dependency: `<pkg-mgr> add -D tsx`

Generate the modular CLI structure: `scripts/harness.ts` (thin router, ~50 lines) +
`scripts/harness/` directory with 6 focused modules (config, types, state, worktree,
tasks, validate, quality — each under 350 lines). See `references/harness-cli.md` for
the exact file-by-file implementation. The CLI handles:
- `harness init` → session boot (sync plans, stale check, register agent, print status)
- `harness next` → find next unblocked task (scoped to current worktree's milestone)
- `harness start <id>` → claim task, auto-update progress.json + PLAN.md
- `harness validate` → lint:fix → lint → type-check → test
- `harness validate:full` → + integration + e2e + file-guard
- `harness done <id>` → complete task, auto-update progress.json + PLAN.md + commit hash
- `harness block <id> <reason>` → mark blocked → 🚫
- `harness reset <id>` → revert task to ⬜ (undo start or unblock)
- `harness learn <cat> <msg>` → log a learning to progress.json + learnings.md
- `harness merge-gate` → full validation + changelog
- `harness worktree:start/finish/rebase/status` → worktree lifecycle + push to remote
- `harness stale-check` / `file-guard` / `schema` / `changelog`

Plus `scripts/check-commit-msg.ts` (needs file path arg, kept separate for hooks).

The CLI uses only `node:` built-in modules — zero external deps beyond `tsx`.
Agent never touches progress.json or PLAN.md manually — the CLI handles all state.

**Non-JS/TS projects (Python, Go, Rust):**
The harness CLI is written in TypeScript and requires `tsx` (Node.js). For non-JS projects:

1. **Recommended:** Install Node.js as a dev dependency (most dev machines already have it).
   Add `scripts/harness.ts` + `scripts/harness/` as-is. The harness CLI manages docs and
   git workflow — it doesn't need to understand the project's source language.
   - Python: `pip install nodeenv && nodeenv .node_env` or just have Node installed globally
   - Go / Rust: Node.js installed alongside Go/Rust toolchain

2. **Alternative:** Generate a simplified `Makefile`-based harness that wraps the core
   commands using shell scripts. Less feature-rich (no agent registration, no worktree
   enforcement) but zero Node.js dependency:
   ```makefile
   harness-validate: lint type-check test
   harness-next: @python3 scripts/harness_next.py  # or shell script
   harness-status: @cat docs/progress.json | python3 -m json.tool
   ```
   If using this approach, the full TypeScript CLI features (agent lifecycle, worktree
   enforcement, stale-check, schema validation) are not available. Note this tradeoff
   in AGENTS.md / CLAUDE.md.

3. **Validate commands** must be adapted in `scripts/harness/validate.ts`:
   - Python: `ruff check .` → `ruff check --fix .` → `mypy src/` → `pytest`
   - Go: `golangci-lint run ./...` → `go vet ./...` → `go test -race ./...`
   - Rust: `cargo clippy -- -D warnings` → `cargo check` → `cargo test`
   The `validate.ts` module runs `${PKG} run lint`, `${PKG} run test`, etc. — it delegates
   to whatever scripts are defined in package.json (JS) or Makefile (non-JS). Make sure
   the project's lint/test/type-check commands are wired up correctly.

**Schemas (included in `references/harness-cli.md`):**

Generate `schemas/progress.schema.json` — validated by `harness schema` command
and by the pre-commit hook.

For Python projects, always generate:
- `ruff.toml` or `pyproject.toml [tool.ruff]` config
- `pyproject.toml [tool.mypy]` with strict mode
- pytest config
- Scripts or Makefile: `lint`, `lint-fix`, `type-check`, `test`, `validate`

For Go projects: `golangci-lint` config, `go vet`, `go test ./...`
For Rust projects: `clippy.toml`, `cargo clippy`, `cargo test`

**The `validate` script is the single gate command.** It runs lint + type-check + tests
in sequence. Agents run this before every commit. CI runs this on every PR.

**Pre-commit hooks (every JS/TS project):**

Generate husky with THREE hooks (see `references/harness-cli.md` for details):

- `.husky/pre-commit` — runs lint-staged + `harness file-guard --staged` + `harness schema`
- `.husky/commit-msg` — runs `check-commit-msg.ts` (rejects non-conforming commits)
- `.husky/pre-push` — runs `harness validate`

`lint-staged` config in package.json:
  ```json
  {
    "lint-staged": {
      "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
      "*.{json,md,yml,yaml}": ["prettier --write"]
    }
  }
  ```
- Setup: `"prepare": "husky"`
- **4-layer enforcement**: pre-commit → commit-msg → pre-push → CI

For Python: use `pre-commit` framework with ruff + mypy hooks.

**Claude Code + Codex configuration (every project):**

Generate BOTH config files to enable **autonomous execution** — the agent loops
through tasks without asking permission for routine commands:

**Claude Code — `.claude/settings.json`:**
```json
{
  "plansDirectory": "./docs/exec-plans/active",
  "permissions": {
    "allowedTools": [
      "Read", "Write",
      "Bash(git *)",
      "Bash(<package-manager> *)",
      "Bash(npx tsx scripts/harness.ts *)",
      "Bash(npx tsx scripts/check-commit-msg.ts *)",
      "Bash(npx lint-staged)",
      "Bash(npx prisma *)",
      "Bash(npx drizzle-kit *)"
    ],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

**Codex — `.codex/config.toml`:**
```toml
# Codex reads AGENTS.md automatically from project root.
# Plans directory not natively configurable — handled via AGENTS.md.

approval_policy = "never"
# This allows Codex to run harness commands, git, and package manager without prompts.
# For supervised mode: approval_policy = "on-request"

[sandbox]
sandbox_mode = "workspace-write"

[project_doc]
project_doc_max_bytes = 65536
```

**What this enables:**

- **Claude Code:** The `allowedTools` list pre-approves ALL harness commands, git,
  and the package manager. Commands not on the list still require approval.
- **Codex:** `approval_policy = "never"` + `sandbox_mode = "workspace-write"` lets
  Codex run all commands within the workspace without prompts.
- **Both:** The agent loops through tasks autonomously. It only pauses at Human
  quality checkpoints (security changes, merge failures, blocked tasks).

The Task Execution Loop runs ~8 shell commands per task. Without pre-approval,
you'd press Y/Enter ~8 times per task. With this config, the agent loops autonomously.

**The user's actual experience:**
```
You:    "Begin working on M1"
Agent:  runs harness init → harness next → harness start → writes code →
        harness validate → git commit → harness done → harness next → ...
        (loops automatically, no permission prompts)
You:    check back whenever you want:
        - <pkg-mgr> run harness status    (cross-platform, recommended)
        - git log --oneline
Agent:  pauses ONLY at Human quality checkpoints:
        - security-sensitive changes
        - merge gate failures
        - blocked tasks (3 validate failures)
        - new module architecture decisions
```

**Why two configs (same outcome, different mechanism):**
- **Claude Code:** uses `allowedTools` whitelist (per-command granularity) + native
  `plansDirectory` for plan mode output
- **Codex:** uses `approval_policy = "never"` (blanket autonomy within sandbox) +
  AGENTS.md instruction for plan file location
- **Windows:** both configs work identically on Windows. All harness commands run
  through `npx tsx` (Node.js) — no bash dependency.

Both agents end up with plan files in the same location → harness init detects and
syncs them identically.

**Environment management (every project):**

Generate one `.env.example` per environment if the user selected multiple environments
(development / staging / production) in Step 4. Each file contains ALL required keys
as placeholder-only values — never real secrets:

```
.env.example              ← base template (always generated)
.env.development.example  ← dev-specific keys (if staging selected)
.env.staging.example      ← staging-specific keys (if staging selected)
.env.production.example   ← production-specific keys (always)
```

Each `.env.example` must comment each variable with where to get it:

```env
# ── Database ─────────────────────────────────────────────────────
# Local: postgresql://postgres:password@localhost:5432/myapp_dev
# Production: get from Railway / Supabase / PlanetScale dashboard
DATABASE_URL=

# ── Auth (Better Auth) ────────────────────────────────────────────
# Generate: openssl rand -base64 32
BETTER_AUTH_SECRET=
# Your server's public URL — used for OAuth callbacks
BETTER_AUTH_URL=http://localhost:3000

# ── OAuth Providers ───────────────────────────────────────────────
# Google: console.cloud.google.com → APIs & Services → Credentials
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ── Error tracking ────────────────────────────────────────────────
# Sentry: sentry.io → Project Settings → Client Keys (DSN)
SENTRY_DSN=

# ── Feature flags ─────────────────────────────────────────────────
FEATURE_FLAG_KEY=
```

Rules:
- `.gitignore` MUST include `.env`, `.env.local`, `.env.*.local`, `.env.development`, `.env.staging`, `.env.production` from line one
- `src/lib/env.ts` — typed env loader that validates ALL required vars at startup. Never use `process.env.X` directly in application code — always go through the typed loader
- For mobile (Expo): client-side vars use `EXPO_PUBLIC_` prefix (inlined at build time). Document which vars are public vs server-only in `.env.example`
- Where to set vars in production: document in `docs/PRD.md` or `docs/deployment.md` with links to the relevant platform dashboards (Vercel env → settings page, EAS → eas.json env field or EAS dashboard)

---

### progress.json Structure

Always generate `docs/progress.json` with this annotated structure so agents can
read and debug it without guessing:

```json
{
  "_comment": "Machine-readable state. Managed by harness CLI — never edit manually.",
  "project": "my-project",
  "version": "1.0.0",
  "last_updated": "2025-01-15T10:00:00Z",
  "last_agent": "claude-code",
  "current_milestone": "M1",
  "current_task": null,
  "agents": [
    {
      "id": "agent-macbook-12345",
      "milestone": "M1",
      "worktree": "../my-project-m1",
      "branch": "milestone/m1",
      "started_at": "2025-01-15T10:00:00Z",
      "heartbeat": "2025-01-15T12:30:00Z"
    }
  ],
  "active_milestones": [
    {
      "id": "M1",
      "title": "Core Authentication",
      "status": "in_progress",
      "branch": "milestone/M1",
      "worktree": "../my-project-M1",
      "depends_on": [],
      "started_at": "2025-01-15T10:00:00Z",
      "completed_at": null,
      "tasks": [
        {
          "id": "M1-001",
          "story": "E1-S01",
          "title": "Set up Better Auth with Prisma adapter",
          "status": "done",
          "done_when": "Auth tables migrated, /api/auth/* routes respond 200",
          "started_at": "2025-01-15T10:00:00Z",
          "completed_at": "2025-01-15T12:30:00Z",
          "commit": "a3f91bc",
          "blocked_reason": null
        },
        {
          "id": "M1-002",
          "story": "E1-S02",
          "title": "Build sign-in and sign-up screens",
          "status": "in_progress",
          "done_when": "Both screens render, email/password auth flow works end-to-end",
          "started_at": "2025-01-15T12:31:00Z",
          "completed_at": null,
          "commit": null,
          "blocked_reason": null,
          "depends_on": ["M1-001"]
        }
      ]
    }
  ],
  "completed_milestones": [],
  "blockers": [],
  "learnings": [],
  "dependency_graph": {
    "M1-002": { "depends_on": ["M1-001"], "blocks": [] }
  },
  "synced_plans": [],
  "stale_checks": {
    "last_run": null,
    "issues": []
  }
}
```

Field meanings for agents:
- `last_updated`: ISO timestamp, auto-set by CLI on every saveProgress
- `last_agent`: who last modified — `"claude-code"`, `"codex"`, or `"human"`
- `current_milestone`: object with milestone counters (id, name, tasks_done, etc.)
- `current_task`: object for the task currently being worked on, or null
- `status` on a task: `⬜` = not started, `🟡` = in progress (claimed by agent), `✅` = done, `🚫` = blocked
- `depends_on` (task): task IDs that must be ✅ before this task can be started. `harness next` respects this
- `depends_on` (milestone): milestone IDs that must be merged before this milestone can merge. `harness worktree:finish` enforces this
- `worktree`: relative path to the git worktree for this milestone
- `agents`: array of currently active agents — each agent registers on `harness init`, heartbeat updates on every command, stale after 2h
- `blockers`: array of blocked tasks with reasons
- `learnings`: array of logged learnings (via `harness learn`)
- `dependency_graph`: task-level dependency map — keys are task IDs, values have `depends_on` and `blocks` arrays
- `synced_plans`: filenames of exec-plans already parsed into PLAN.md



**Docker (for web app / API projects):**

- `Dockerfile` — multi-stage build (build stage + production stage), minimal image
- `docker-compose.yml` — one-command local dev environment:
  ```yaml
  services:
    app:
      build: .
      ports: ["3000:3000"]
      env_file: .env
      volumes: ["./src:/app/src"]  # hot reload
    db:
      image: postgres:16-alpine    # or whatever DB was chosen
      env_file: .env
      ports: ["5432:5432"]
      volumes: ["db_data:/var/lib/postgresql/data"]
  volumes:
    db_data:
  ```
- Include `docker-compose up -d` in the Quick Start section of AGENTS.md / CLAUDE.md
- Skip Docker for CLI tools and simple libraries unless user requests it

**Error handling infrastructure:**

Generate these files with patterns appropriate to the chosen stack:

- `src/lib/errors.ts` — Unified error class hierarchy:
  - Base `AppError` class with `statusCode`, `code`, `message`, `isOperational`
  - Subclasses: `ValidationError`, `NotFoundError`, `AuthError`, `ConflictError`
  - Error factory function: `createError(code, message, details?)`
  - Every error has a machine-readable `code` (e.g., `AUTH_EXPIRED_TOKEN`)

- `src/lib/logger.ts` — Structured JSON logging:
  - Fields: `timestamp`, `level`, `message`, `requestId`, `context`
  - Levels: `debug`, `info`, `warn`, `error`, `fatal`
  - In dev: pretty-print. In prod: JSON to stdout.
  - Never log sensitive data (passwords, tokens, PII)

- `src/middleware/error-handler.ts` — Global error boundary:
  - Catches all unhandled errors
  - Maps AppError subclasses to HTTP status codes
  - Returns consistent error response format:
    `{ error: { code, message, details? } }`
  - Logs error with full context (requestId, stack, user)
  - In dev: includes stack trace. In prod: hides internals.

**Analytics (GA / Posthog — for web apps):**

- `src/lib/analytics.ts` — Analytics service abstraction:
  - `trackEvent(name, properties?)`, `trackPageView(path)`, `identifyUser(id, traits?)`
  - Provider-agnostic interface — swap GA for Posthog without touching app code
  - Loads measurement ID from env (`GA_MEASUREMENT_ID` or `POSTHOG_KEY`)
  - Respects Do Not Track / cookie consent
  - For SSR frameworks (Next.js): handle client-side only initialization
- Include GA/Posthog script setup in the root layout/template

**Health checks & monitoring (for web apps / APIs):**

- `GET /health` endpoint — returns `{ status: "ok", timestamp, version, uptime }`
- `GET /health/ready` — checks DB connection, external service availability
- Sentry integration:
  - `src/lib/sentry.ts` — init from env `SENTRY_DSN`
  - Wraps error handler to auto-report unhandled errors
  - Source maps uploaded in CI (add to deploy workflow)
- These endpoints are the first thing monitoring services hit

**Feature flags:**

- `src/lib/feature-flags.ts` — Feature flag service:
  - Simple local flags for v1: `flags.json` or env-based
  - Interface: `isEnabled(flagName, context?)` → boolean
  - Designed to swap in a remote provider later (LaunchDarkly, Flagsmith, Unleash)
  - Every new user-facing feature gets a flag
  - Flags are the mechanism for gradual rollout — ship to main behind a flag,
    enable for % of users, monitor, then remove flag when stable

**API documentation (for backend projects):**

- OpenAPI/Swagger:
  - Generate `openapi.yaml` or use code-first annotations (e.g., zod-to-openapi)
  - Serve Swagger UI at `/docs` in development
  - Auto-generate from route definitions — never manually maintain the spec
- Storybook (for frontend projects with component libraries):
  - `.storybook/` config
  - One example story for the first component
  - `storybook` script in package.json

**Project documentation site (docs/site/):**

Generate a GitBook-style documentation structure:

- `docs/site/SUMMARY.md` — sidebar navigation / table of contents:
  ```markdown
  # Summary

  - [Introduction](README.md)
  - [Getting Started](getting-started.md)
    - [Installation](getting-started.md#installation)
    - [Configuration](getting-started.md#configuration)
    - [First Run](getting-started.md#first-run)
  - [Architecture](architecture.md)
    - [Domain Map](architecture.md#domain-map)
    - [Dependency Layers](architecture.md#dependency-layers)
  - [API Reference](api-reference.md)
  - [Deployment](deployment.md)
  - [Contributing](contributing.md)
  ```
- `docs/site/README.md` — project introduction, what it does, who it's for
- `docs/site/getting-started.md` — installation, config, first run
- `docs/site/architecture.md` — mirrors ARCHITECTURE.md in user-friendly prose
- `docs/site/api-reference.md` — links to OpenAPI docs or manual reference
- `docs/site/deployment.md` — deploy instructions for chosen platform
- `docs/site/contributing.md` — how to contribute, branch strategy, PR conventions

This structure is compatible with GitBook, Docusaurus, VitePress, or plain markdown
reading. The SUMMARY.md acts as a universal sidebar. Expand pages as the project grows.

**Also include at minimum:**
- Entry point file with a working starter (hello world level)
- One example test that passes
- `.gitignore` — generate from `references/gitignore-templates.md`. Assemble by combining
  the Universal block + the stack-specific block(s). This must be the FIRST file committed
  to the repo, before any code. Verify `.env` patterns are present.
- CI workflows that run `validate` on every PR and `validate:full` + deploy on merge
- `docs/frontend-design.md` — **MUST be generated for every project that has a frontend**.
  Read `/mnt/skills/public/frontend-design/SKILL.md` at generation time and copy its
  full content into `docs/frontend-design.md` in the output project. This makes the
  frontend design skill available to Claude Code and Codex, which don't have access to
  claude.ai's skill paths. Iron Rule 5 in AGENTS.md / CLAUDE.md points to this file.

For monorepos, generate workspace config (pnpm-workspace.yaml / turbo.json / etc.)
with at least one package or app entry.

---


