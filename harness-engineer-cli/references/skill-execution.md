## Phase 4: Execution Runtime

Everything from "artifacts generated" to "project complete" is driven by the
harness CLI. For agent guidelines (context budget, parallel coordination, quality gates),
see `references/execution-runtime.md`.

### The Agent's Entire Workflow (CLI commands)

```bash
# ── From main repo root: set up worktree for a milestone ──────────────────────
<pkg-mgr> run harness worktree:start M1
# → checks no other agent has claimed M1 (heartbeat-based)
# → creates branch milestone/m1
# → runs: git worktree add ../project-m1 milestone/m1
# → updates progress.json with branch + worktree path
# → prints: cd "../project-m1" && <pkg-mgr> install && <pkg-mgr> run harness init

# ── Inside the milestone worktree: task execution loop ────────────────────────
cd ../project-m1
<pkg-mgr> install
<pkg-mgr> run harness init        # sync plans, stale check, register agent, print status

# Task loop (repeat until milestone is done)
# NOTE: next/start/done REFUSE to run on main — worktree is enforced by CLI
<pkg-mgr> run harness next        # → "M1-003: Implement email confirmation"
<pkg-mgr> run harness start M1-003

# Write code for the task

<pkg-mgr> run harness validate    # → lint:fix → lint → type-check → test
git add -A && git commit -m "[M1-003] implement email confirmation flow"
<pkg-mgr> run harness done M1-003

# If validate fails 3x:
<pkg-mgr> run harness block M1-003 "bcrypt build fails on Alpine"
<pkg-mgr> run harness learn dependency "bcrypt native fails on Alpine — use bcryptjs"

# If you need to undo a start (code is wrong, want to restart clean):
<pkg-mgr> run harness reset M1-003   # reverts 🟡 back to ⬜

# Periodically rebase onto main (especially if other milestones merged):
<pkg-mgr> run harness worktree:rebase  # → fetches main, rebases, reports conflicts

# When all milestone tasks are done:
<pkg-mgr> run harness merge-gate  # → validate:full + stale-check + changelog
                                  # → prints: run harness worktree:finish M1

# ── Back in main repo root: merge + clean up ──────────────────────────────────
cd ../project                     # main repo root
<pkg-mgr> run harness worktree:finish M1
# → checks dependency order (blocks if M1 depends on unmerged milestones)
# → rebases milestone/m1 onto latest main (detects conflicts early)
# → git merge --no-ff milestone/m1
# → validate:full on main
# → deregisters agent from progress.json
# → git worktree remove ../project-m1
# → git branch -d milestone/m1
# → moves M1 from active_milestones → completed_milestones in progress.json
# → git push origin main (syncs remote)
# → prints: git tag v<version> && git push --tags

# If rebase conflicts during worktree:finish:
# → CLI aborts and shows conflicting files
# → Option A: manual rebase inside worktree, then re-run worktree:finish
# → Option B: worktree:finish M1 --force (skip rebase, merge directly)

# Human decides version number, then:
git tag v1.0.0
git push --tags

# ── Check overall status at any time from main repo root ──────────────────────
<pkg-mgr> run harness worktree:status
# → shows all worktrees, registered agents, heartbeat ages, merge readiness
```

That's it. The CLI handles state management, dependency resolution, plan syncing,
stale detection, schema validation, and changelog generation. The agent never
manually edits progress.json or PLAN.md status fields.

### Database Migration Flow

Migrations are a common point of failure in the task loop. These rules apply
regardless of which ORM or migration tool the project uses.

**Universal migration rules for agents:**
- Schema changes always come BEFORE the code that uses them - run migration first
- If migration fails 3x, run `harness block <id> "migration fails: <e>"`
- Migration files are versioned - commit them with the task that created them
- Never skip migration history in CI or production
- Rolling back: write a new forward migration to undo (most tools cannot auto-rollback)
- In parallel worktrees: migrations may conflict on merge. Rebase and re-run before finish

**Prisma:**
```bash
npx prisma migrate dev --name <n>   # dev: create + apply
npx prisma migrate deploy           # CI/prod: apply only (idempotent)
npx prisma migrate reset            # dev only: drops data and re-applies
npx prisma migrate status           # check status
```

**Drizzle:**
```bash
npx drizzle-kit generate    # generate migration SQL from schema
npx drizzle-kit migrate     # apply pending migrations
npx drizzle-kit push        # dev only: push schema directly
```

**TypeORM:**
```bash
npx typeorm migration:generate -d src/data-source.ts src/migrations/AddUsers
npx typeorm migration:run -d src/data-source.ts
npx typeorm migration:revert -d src/data-source.ts
```

**Django (Python):**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

**Raw SQL / custom:**
- Keep files in `migrations/` with timestamp prefixes, apply in order
- Track applied migrations in a `_migrations` table
- Commit with the task: `[M1-001] add user table migration`

### Parallel Worktree

- One agent, one worktree — enforced by CLI (worktree:start checks agents array)
- Independent milestones can run in parallel
- progress.json `agents` array is the coordination point — agents self-register on `init`
- Agent heartbeat updated on every command (next/start/done) — stale after 2h
- Merge order follows dependency order — `worktree:finish` blocks if deps aren't merged
- After another milestone merges into main, rebase with `worktree:rebase`
- `worktree:status` shows all agents, heartbeats, and merge readiness from main root

### Worktree Enforcement

The CLI **refuses** to run task commands (`next`, `start`, `done`) on the main branch.
This prevents agents from accidentally working directly on main without worktree isolation.
If an agent tries to run `harness start M1-001` on main, the CLI will error with instructions
to create a worktree first. This is a hard gate — there is no override flag.

### Context Budget

| Zone | Budget |
|------|--------|
| System prompt + AGENTS.md | ≤ 15% |
| progress.json + PLAN section | ≤ 15% |
| Source files for current task | ≤ 30% |
| Working memory (code + reasoning) | ≤ 40% |

Never load entire codebase, PLAN, or PRD. Only current task's files.
Overloaded? → commit, `harness done`, start fresh session.

### Quality Checkpoints

| Event | Mode |
|-------|------|
| Task passes validate | **Auto** → commit, done, next |
| Task failed 3x | **Human** → block, report |
| Milestone merge-gate passes | **Auto** → merge, tag |
| Merge-gate fails | **Human** → report, wait |
| Security-sensitive change | **Human** → always review |
| Dependency conflict | **Auto** → delete + rebuild (Iron Rule 3) |

### Testing Tiers

| Tier | Runs when | CLI command |
|------|-----------|-------------|
| Unit | Every task | `harness validate` |
| Integration | Milestone merge | `harness validate:full` |
| E2E | Milestone merge | `harness validate:full` |
| File guard (500 lines) | Every commit + merge | `harness file-guard` |

### CI Integration

**ci.yml (every PR):** `harness validate` + `dependency-audit`
**deploy.yml (merge to main):** `harness validate:full` + build + deploy

### Production Readiness Checklist

Every milestone merge must meet production standards. These checks are part of the
merge-gate and are enforced by code review, not just automated tools.

**Code quality (enforced by validate + file-guard):**
- Zero lint errors, zero lint warnings
- Zero type errors
- All tests pass (unit + integration + e2e)
- No file exceeds 500 lines

**Error handling (agent responsibility — verify before merge-gate):**
- Every external call (API, DB, file I/O, network) wrapped in try/catch
- Every endpoint/command validates input before processing
- Error responses are structured: `{ error: { code, message, details? } }`
- No unhandled promise rejections (use async error boundaries)
- No bare `throw new Error('...')` — use typed error classes from `src/lib/errors.ts`

**Observability (agent responsibility — verify in code review):**
- Structured logger used everywhere (`src/lib/logger.ts`) — zero `console.log` in production paths
- Every error logged with context: request ID, operation, relevant IDs
- Health endpoint responds correctly (if applicable)
- Feature flags wrap all new user-facing features

**Code hygiene (agent responsibility — auto-checked where possible):**
- No `TODO`, `FIXME`, `HACK`, `XXX` comments in committed code
  - If something needs fixing, it's a task in PLAN.md, not a comment
- No hardcoded URLs, ports, credentials, or magic numbers
- No dead code (unused imports, unreachable branches, commented-out blocks)
- Build produces zero warnings (TypeScript `noEmit`, bundler warnings, etc.)

**Documentation (agent responsibility — tracked as milestone tasks):**
- README/docs accurately reflect current state of the code
- API endpoints documented (or auto-generated from OpenAPI/tRPC)
- ARCHITECTURE.md updated if new modules were added
- Changelog generated via `harness changelog`

**What "production ready" means for each project type:**
- Web App: page loads in <2s, errors show user-friendly messages, CSP headers set
- API: every endpoint returns correct HTTP status codes, rate limiting configured
- CLI: exit codes are correct (0/1/2), `--help` is accurate, errors go to stderr
- Agent/MCP: all tools return structured MCP errors, input schemas validate correctly
- Mobile: app doesn't crash on network loss, loading states shown, deep links work

### Versioning and Release Strategy

Every project must have an explicit version scheme. Generate this in `AGENTS.md` and
`docs/PLAN.md` from the start:

**Semantic versioning** (`MAJOR.MINOR.PATCH`):
- `PATCH` — bug fixes, no API changes → OTA update (mobile) or hotfix deploy
- `MINOR` — new features, backward-compatible → standard milestone release
- `MAJOR` — breaking changes → milestone with migration guide

**Version lives in `package.json`** (or `pyproject.toml` / `Cargo.toml`).
`harness changelog` reads commit messages tagged `[Mn-id]` to generate release notes.

**Git tagging convention** — `harness merge-gate` tags automatically on milestone completion:
```
v1.0.0          ← production release
v1.0.0-rc.1     ← release candidate (staging)
v0.9.0          ← pre-1.0 development
```

**For mobile (Expo/EAS):**
- `version` in `package.json` = semantic version shown in stores
- `ios.buildNumber` / `android.versionCode` = auto-incremented by EAS (`"autoIncrement": true` in `eas.json`)
- Never manually increment build numbers — EAS manages this
- OTA updates via EAS Update do NOT change the version — they're transparent patches

**Tagging workflow in AGENTS.md:**
```
harness merge-gate           # validate:full + stale-check + changelog
git tag v<new-version>       # after human reviews changelog
git push --tags              # triggers deploy.yml
```

**Who decides the version number:** Human, not the agent.
The agent runs `harness changelog`, shows the generated notes, and asks:
> "Milestone M3 is complete. Based on the changes, I'd suggest version X.Y.Z.
> Please confirm or choose a different version before I tag and push."

---

## Phase 6: Documentation Site (Evolving)

The `docs/site/` directory grows with the project. Documentation updates are
milestone tasks, not afterthoughts.

### When to update

- **Every milestone**: getting-started.md if setup changed, architecture.md if new modules
- **Every new endpoint**: api-reference.md (or auto-generate from OpenAPI)
- **Every new feature**: user-facing doc if externally visible
- **Every deploy change**: deployment.md

### Documentation tasks in PLAN.md

Every milestone includes doc tasks:

| Task ID | Story | Task | Done When |
|---------|-------|------|-----------|
| M1-008 | — | Update getting-started.md | Doc covers auth setup |
| M1-009 | — | Update SUMMARY.md | New sections linked, no dead links |

### Compatible with

GitBook, Docusaurus, VitePress, or plain GitHub markdown.
SUMMARY.md is the universal sidebar. Choose publishing platform later.

---

## Principles

1. **Map, not encyclopedia** — AGENTS.md / CLAUDE.md stay concise. Deep info in linked docs.
2. **Dual-agent identical** — Always generate BOTH files with identical content.
3. **Iron rules templated, everything else dynamic** — 6 iron rules are fixed. Everything else from the actual project.
4. **Everything in the repo** — If it matters, it's a versioned file. No tribal knowledge.
5. **Rules are code, not prose** — harness CLI + hooks + CI = 4-layer enforcement. Agent runs commands, not checklists.
6. **Secrets never touch git** — .env in .gitignore from day zero. `harness stale-check` detects drift.
7. **User value first** — Every requirement delivers clear user or business value.
8. **Testable & traceable** — Requirements → Epics → Stories → Tasks. Every task has "done when."
9. **Granular decomposition** — ≤ 4h per task. If bigger, split.
10. **Code is cheap** — Delete and rewrite. Assume infinite tokens. First principles only.
11. **Worktree isolation** — Each milestone in its own worktree. Atomic commits. Merge only when green.
12. **CLI handles state** — Agent never manually edits progress.json or PLAN.md status. `harness start/done/block` does it.
13. **Schema-validated** — progress.json has a JSON Schema. Hooks reject invalid writes.
14. **Commits are parseable** — [Mn-id] format enforced by hook. `harness changelog` auto-generates release notes.
15. **Errors are structured** — Unified error classes, JSON logging, global error boundary.
16. **Ship behind flags** — New user-facing features go behind a feature flag.
17. **Observe everything** — Analytics, error tracking, health checks, structured logs.
18. **Docs evolve with code** — Doc updates are milestone tasks, not afterthoughts.
19. **Context is finite** — ≤40% context utilization. Never load more than the current task needs.
20. **Learnings compound** — Problems + solutions logged. Future sessions inherit past wisdom.
21. **Staleness is a bug** — `harness stale-check` catches it. Don't wait for humans.
22. **Parallel by default** — Independent milestones run in parallel. One agent, one worktree.
23. **Modularize proactively, not reactively** — Don't wait for 500 lines. Split at ~250 if a file has multiple responsibilities. Every module = one purpose. The CLI itself models this: 1 entry point + 6 focused modules, none exceeding 350 lines. If the CLI follows its own rule, so does all project code.
24. **Frontend = frontend-design skill** — All frontend reads `docs/frontend-design.md` first.
25. **The loop is perpetual** — Bootstrap, execute, idle, add work, repeat forever.
26. **Production ready is the only standard** — Every milestone ships. No "it works locally." Error handling, input validation, structured logging, zero build warnings, no TODO/FIXME in committed code. If it's not production ready, the task is not done.

---

## Post-Generation

After creating all files:

1. Present the file tree overview
2. Show a concise summary of what was generated: stack, auth, environments, monorepo structure
3. Highlight four files the user must review:
   - `docs/PRD.md` — requirements and acceptance criteria
   - `docs/PLAN.md` — milestones, tasks, dependencies, "done when" conditions
   - `AGENTS.md` / `CLAUDE.md` — agent rules and iron rules (including Production Ready Standard)
   - `docs/progress.json` — dependency graph and task order
4. Ask the user to review `docs/PLAN.md` specifically and confirm:
   - Are the milestones in the right order?
   - Is the task granularity right? (each task should be ≤ 4h)
   - Are the "done when" conditions measurable?
   - Are the dependencies between tasks correct?
5. Remind the user: **"Every milestone is built to production standards. Iron Rule 7
   (Production Ready Standard) means every merge includes error handling, input validation,
   structured logging, zero build warnings, and no TODO/FIXME in committed code.
   The agent enforces this at every merge-gate."**

Then present the explicit approval gate:

> **"The scaffold is ready. Before I hand off to Claude Code / Codex, please review
> PLAN.md and confirm you're happy with the milestones and task breakdown.
> Once you approve, the agent will begin executing automatically from M1-001.
> Type 'approved' or let me know what you'd like to change."**

**Do not provide the handoff instructions until the user explicitly approves the plan.**

After approval, provide the Step-by-step handoff instructions (git init, install deps,
open in agent). Make clear that once the user opens the project in Claude Code / Codex
and says "begin", the agent will execute autonomously until a Human quality checkpoint
is triggered.

---

## Handoff to Claude Code / Codex

### What is the skill vs what is the project

```
harness-engineer-cli/                <← THIS IS THE SKILL (stays in claude.ai)
├── SKILL.md                    ← Instructions for generating the project
└── references/                 ← Templates used DURING generation
    ├── harness-cli.md          ← CLI source + schema + hooks → becomes scripts/harness.ts
    ├── eslint-configs.md       ← ESLint templates → becomes eslint.config.js
    ├── project-configs.md      ← tsconfig/prettier/vitest/Docker templates → becomes real files
    ├── gitignore-templates.md  ← .gitignore templates → becomes .gitignore
    └── execution-runtime.md    ← Agent guidelines (context budget, parallel, quality gates)

my-project/                     ← THIS IS THE OUTPUT (goes to the agent)
├── AGENTS.md                   ← Codex reads this — has EVERYTHING it needs
├── CLAUDE.md                   ← Claude Code reads this — identical to AGENTS.md
├── ...all other generated files
```

The references/ folder is the "mold." The generated project is the "cast."
Once generated, the mold is not needed. All templates have been materialized into
real config files. All protocols have been written into AGENTS.md and CLAUDE.md.

### What the user does after generation

**Step 1: Review in claude.ai**
- Review PRD.md — are requirements correct?
- Review PLAN.md — are tasks granular enough? Dependencies correct?
- Review AGENTS.md / CLAUDE.md — do the commands match your environment?
- Review progress.json — is the dependency graph accurate?
- Request changes until satisfied.

**Step 2: Set up the project**
```bash
# Option A: Init new repo
mkdir my-project && cd my-project
git init
# Copy all generated files here
git add -A
git commit -m "scaffold: initial project setup from harness bootstrapper"

# Option B: Push to GitHub first
gh repo create my-project --private
# Copy files, push
git add -A && git commit -m "scaffold: initial project setup" && git push
```

**Step 3: Install dependencies**
```bash
# The exact command is in AGENTS.md / CLAUDE.md Quick Start section
<package-manager> install
```

**Step 4: Verify scaffold works**
```bash
# Run validate via the harness CLI
<package-manager> run harness validate
# This should pass — the scaffold includes a hello-world test
```

**Step 5: Open in your agent**
```bash
# Claude Code
claude .
# Automatically reads CLAUDE.md on startup

# Codex
codex .
# Automatically reads AGENTS.md on startup
```

Both agents read the same content. The only difference is which filename they look for.

**Step 6: Start execution**

Tell the agent:
> "Read the Session Init section and begin working on the first milestone."

Or for parallel execution:
> "Read Session Init. Start milestone M1 in a worktree."

The agent will:
1. Read AGENTS.md / CLAUDE.md (already done at startup)
2. Read docs/progress.json → see M1 is first, all tasks ⬜
3. Create worktree: `git worktree add ../my-project-M1 -b milestone/M1`
4. Pick the first unblocked task (M1-001)
5. Begin the Task Execution Loop autonomously

**Step 7: Monitor**

You can check progress at any time:
- `cat docs/progress.json` — machine-readable status
- `cat docs/PLAN.md` — human-readable task board
- `git log --oneline` — commit history with [M1-001] prefixes
- `cat docs/learnings.md` — what the agent learned along the way

The agent will pause and ask for your input at Quality Checkpoints marked **Human**
(security changes, architecture decisions, merge gate failures).

### What the agent does NOT need

- `references/` folder — templates already materialized into real files
- `SKILL.md` — that's the generation recipe, not the execution instructions
- Any claude.ai conversation history — everything is in the repo files
- External docs or wikis — all knowledge is in the repo (harness principle #4)

---

## Ongoing Development — Adding New Work

The initial bootstrap creates Milestones M1, M2, M3... from the PRD. But a project
doesn't end there. New features, bugs, tech debt, and pivots happen continuously.

The execution loop is designed to be **perpetual** — it doesn't care whether a milestone
was generated during bootstrap or added 6 months later. Same flow, same rules.

### Two paths to add new work

**Path A: Directly in Claude Code or Codex (recommended for most new work)**

The smoothest flow uses **plan mode** as the entry point:

1. Open Claude Code or Codex in the project
2. Enter plan mode:
   - Claude Code: `Shift+Tab`
   - Codex: enter plan mode per its current UI
3. Describe what you want: "I want to add user profile editing with avatar upload"
4. Agent generates a plan → saved to `docs/exec-plans/active/`
   - Claude Code: automatic via `.claude/settings.json` plansDirectory
   - Codex: follows AGENTS.md instruction to write plans there
5. Review the plan, edit if needed, approve execution
6. Switch back to normal/execution mode
7. Tell the agent: "Sync the new plan and start working on it"
8. The agent's Session Init detects the plan file and:
   - Parses it into PRD updates + new Milestone in PLAN.md
   - Builds dependency graph in progress.json
   - Creates worktree → enters Task Execution Loop
   - Same flow as initial development, identical rules

For tiny changes (1-2 files, obvious diff, no plan needed):
> "Add a dark mode toggle to the settings page. Create a task for it."

**Path B: Back to claude.ai (large changes, multiple milestones, pivots)**

Come back to this skill and say:
> "Here's my existing project [upload key files]. I want to add [requirements]."

Upload these files for context:
- `AGENTS.md` / `CLAUDE.md` — current project rules (either one, they're identical)
- `docs/PRD.md` — current requirements
- `docs/PLAN.md` — current plan + completed milestones
- `docs/progress.json` — current state
- `ARCHITECTURE.md` — current architecture

The skill will:
1. Skip Phase 1 Steps 1-2 (project type + vision already known)
2. Run a mini Product Deep Dive focused on the NEW requirements
3. Optionally do web search for the new feature area
4. Generate updated PRD.md with new FRs, Epics, Stories appended
5. Generate new Milestones in PLAN.md (preserving completed ones)
6. Update progress.json with new dependency graph
7. User copies updated files back to project, commits them
8. The agent picks up the changes on next session init

### What the agent does when all milestones are complete

The agent's Session Init reads progress.json. If ALL milestones are in
`completed_milestones` and there are no active milestones:

```
## Idle Protocol (all milestones complete)

If progress.json shows no active milestone and no remaining tasks:

1. Run a final stale detection pass on all docs
2. Fix any stale docs, commit
3. Run validate:full on main — confirm everything is green
4. Report to the user:
   "All milestones complete. Project is green. Ready for new work."
5. WAIT for user input — do NOT invent new tasks

When the user provides new requirements:
- Follow the "Add New Work" protocol (Path A above)
- Create a new milestone, update PRD + PLAN + progress.json
- Resume the normal Task Execution Loop
```

### New work types

The same milestone/task structure handles all types of work:

| Type | How to add | Priority |
|------|-----------|----------|
| **New feature** | New Epic in PRD → New Milestone in PLAN | MoSCoW from PRD |
| **Bug fix** | Add FR with "Bug:" prefix → Task in nearest milestone or new milestone | Must (if user-facing) |
| **Tech debt** | Add to docs/tech-debt/ → Create milestone when prioritized | Should/Could |
| **Refactor** | Add FR or tech debt item → Tasks with "Refactor:" prefix | Should |
| **Dependency update** | Task in current or new milestone | Must (if security) |
| **Performance** | Add NFR → Tasks with benchmarks as "Done When" | Based on impact |

### Continuous project lifecycle

```
Bootstrap (claude.ai)
  → Phase 1-3: Generate everything
  → Handoff to Claude Code / Codex

Sprint 1 (Claude Code / Codex)
  → Phase 4: Execute M1, M2, M3...
  → Phase 5: Test continuously
  → Phase 6: Update docs

All initial milestones done
  → Idle Protocol: report green, wait

User adds new work (Claude Code / Codex or claude.ai)
  → Update PRD + PLAN + progress.json
  → New milestone(s) created

Sprint 2 (Claude Code / Codex)
  → Same Phase 4-6 loop on new milestones
  → Same iron rules, same testing, same worktree flow

Repeat forever.
```

The repo is the single source of truth. The execution loop doesn't know or care
whether it's running for the first time or the hundredth time. As long as there's
a milestone with ⬜ tasks in PLAN.md and a matching entry in progress.json,
the agent knows what to do.

### What if the user wants to re-generate or modify?

Come back to claude.ai with this skill. You can:
- "Update my PRD with these new requirements" → re-generate PRD.md + PLAN.md
- "Add a new milestone for X" → update PLAN.md + progress.json dependency graph
- "Change the tech stack from X to Y" → regenerate scaffold + configs
- "My AGENTS.md / CLAUDE.md is out of date" → re-generate from current project state

After re-generation, copy the updated files into the project repo and commit them.
The agent will pick up the changes on next session init.
