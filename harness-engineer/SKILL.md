---
name: harness-engineer
description: >
  Bootstrap a complete agent-first project OR retrofit an existing project with the harness
  framework — AGENTS.md, CLAUDE.md, execution plans, PRD, and automation scripts, all based
  on Harness Engineering principles. Use this skill whenever the user wants to start a new
  project, initialize a codebase, create a project scaffold, set up a monorepo, or says
  anything like "new project", "bootstrap", "init", "scaffold", "start building", "project setup",
  "create an app", "set up a repo". ALSO trigger when the user wants to add harness to an
  existing project, says "retrofit", "add AGENTS.md to my project", "set up harness for my repo",
  "convert my project", or mentions AGENTS.md, harness engineering, agent-first development.
  Even if the user just describes an idea and wants to "get started", this is the skill to use.
---

# Harness Engineer

This skill creates a complete, agent-first project foundation based on Harness Engineering
principles. It works in TWO modes:

- **Greenfield** — New project from scratch. Full product discovery, PRD, scaffold, everything.
- **Retrofit** — Existing project. Analyze the codebase, add harness layer on top. No scaffold
  generation, no long-task bootstrap. Future work flows through plan mode.

The philosophy: AGENTS.md is a **table of contents, not an encyclopedia**. Keep it concise,
pointing to deeper sources of truth. All project knowledge lives in the repo as versioned,
discoverable artifacts — because if an agent can't see it, it doesn't exist.

---

## Mode Selection

First, determine which mode to use. If the user uploads files or mentions an existing
project, use Retrofit. If they describe something new, use Greenfield.

If unclear, ask:

**ask_user_input:**
1. **Mode** (single_select): What's the starting point?
   - Options: `New project from scratch`, `Add harness to an existing project`

If **New project from scratch** → go to [Greenfield Workflow](#greenfield-workflow)
If **Add harness to existing project** → go to [Retrofit Workflow](#retrofit-workflow)

---

## Retrofit Workflow

For existing projects. The goal is NOT to rewrite or re-scaffold the project. The goal
is to add the harness layer — the docs, scripts, hooks, configs, and conventions that
let agents work autonomously on future tasks.

### Retrofit Step 1: Analyze the Existing Project

Ask the user to upload or describe their project. Key files to request:

- `package.json` / `pyproject.toml` / `go.mod` (to understand stack + deps)
- Source directory structure (`ls src/` or equivalent)
- Any existing README, docs, or config files
- `.gitignore` (to see what's already there)
- Any existing CI workflows (`.github/workflows/`)
- Any existing linter/formatter configs (eslint, prettier, tsconfig, etc.)

If the user has uploaded files, read them directly.
If the user describes verbally, ask clarifying questions about:

**ask_user_input:**
1. **Tech stack** (multi_select): What does this project use?
   - Adapt options based on what you can see from uploaded files
   - Example: `TypeScript`, `React / Next.js`, `Node.js API`, `Python`, `Go`

2. **Package manager** (single_select, JS/TS only):
   - Options: `pnpm`, `bun`, `npm`
   - Auto-detect from lockfile if uploaded

Then analyze:
- What framework and runtime? (detect from deps)
- What's the source directory structure? (detect module/domain boundaries)
- What tests exist? (detect test framework, test directory)
- What CI exists? (detect workflows)
- What linting/formatting exists? (detect configs)
- What's the dependency layer structure? (detect import patterns)

### Retrofit Step 2: Generate Harness Layer

Based on the analysis, generate ONLY the harness files. Do NOT touch existing source code,
tests, or configs unless they conflict with the harness.

**Always generate (regardless of what exists):**

```
Files to ADD to the existing project:
├── AGENTS.md                    ← dynamically generated from analysis
├── CLAUDE.md                    ← identical to AGENTS.md
├── ARCHITECTURE.md              ← generated from actual source structure
├── docs/
│   ├── PRD.md                   ← lightweight — document what EXISTS, not what to build
│   ├── PLAN.md                  ← empty milestones section, ready for new work
│   ├── progress.json            ← initialized with project state
│   ├── learnings.md             ← empty, ready for agent learnings
│   ├── frontend-design.md       ← if project has frontend
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   ├── tech-debt/
│   │   └── .gitkeep
│   └── site/                    ← doc site skeleton
│       ├── SUMMARY.md
│       └── README.md
├── scripts/                     ← all harness scripts (.ts)
│   ├── validate.ts
│   ├── validate-full.ts
│   ├── file-guard.ts
│   ├── stale-check.ts
│   ├── progress-sync.ts
│   ├── validate-schema.ts
│   ├── check-commit-msg.ts
│   └── changelog.ts
├── schemas/
│   └── progress.schema.json
├── .claude/
│   └── settings.json
└── .codex/
    └── config.toml
```

**Conditionally generate (only if not already present):**

| File | Generate if... | Skip if... |
|------|---------------|-----------|
| `.gitignore` | Missing or doesn't have .env patterns | Already comprehensive |
| `.env.example` | Missing | Already exists |
| `eslint.config.js` | No ESLint config exists | Already has ESLint (preserve theirs) |
| `.prettierrc` | No Prettier config exists | Already has Prettier (preserve theirs) |
| `tsconfig.json` | No tsconfig exists | Already has one (preserve theirs) |
| `.husky/` hooks | No husky setup exists | Already has hooks (merge, don't replace) |
| CI workflows | No CI exists | Already has CI (augment, don't replace) |
| `Dockerfile` | No Docker setup exists | Already has Docker (preserve theirs) |
| `docker-compose.yml` | No compose exists | Already has one (preserve theirs) |

**Rule: NEVER overwrite existing configs.** If the project already has ESLint, tsconfig,
Prettier, CI, Docker — keep theirs. Only add the harness-specific files that don't exist.

If an existing config conflicts with Iron Rules (e.g., ESLint is on `warn` instead of
`error` for `no-explicit-any`), note it in a `docs/tech-debt/harness-alignment.md` file
as a suggestion, but do NOT force the change.

### Retrofit Step 3: Adapt AGENTS.md / CLAUDE.md to the Existing Project

The Iron Rules template is copied verbatim (same as greenfield).

Everything else is generated from what ACTUALLY exists:

- **Project overview** — describe what this project does based on README/package.json/source
- **Quick start** — the REAL commands this project uses (detect from existing scripts)
- **Repository map** — point to the actual directories and files that exist
- **Architecture rules** — derive from the actual import patterns and module structure
- **Dev environment tips** — based on the actual dev workflow (existing scripts, Docker, etc.)
- **Testing instructions** — whatever test framework and commands they already use
  + add the new harness scripts (`validate`, `stale-check`, etc.)
- **Session Init / Task Loop / Merge Gate / Stale Detection** — standard templates,
  with commands adapted to the existing package manager and test runner
- **Plan File Convention** — standard, pointing to `docs/exec-plans/active/`

### Retrofit Step 4: Generate Lightweight PRD

For a retrofit, the PRD is a **snapshot of what exists**, not a design document.
It's shorter than a greenfield PRD.

```markdown
# Product Requirements Document: <Project Name>

## 1. Overview
What this product currently does, based on analysis of the codebase.

## 2. Current State
- Tech stack: <detected>
- Key modules/domains: <detected from src/>
- Test coverage: <detected — what exists>
- CI/CD: <detected — what's set up>
- Deploy target: <detected or ask user>

## 3. Existing Features (as-is)
Brief inventory of what's already built, organized by module/domain.
Not a design doc — just a map of what exists for agent context.

| Module | Description | Has Tests? |
|--------|------------|-----------|
| auth   | JWT-based authentication | Yes (12 tests) |
| users  | User CRUD + profiles | Partial (3 tests) |
| ...    | ... | ... |

## 4. Tech Debt (detected)
Issues found during analysis:
- Files over 500 lines: <list>
- Missing test coverage: <modules without tests>
- Missing .env.example entries: <vars in code but not in example>
- Stale docs: <any detected>

## 5. Future Work
(Empty — to be filled via plan mode when user adds new work)

## 6. Tech Stack
| Layer | Choice | Detected From |
|-------|--------|--------------|
```

### Retrofit Step 5: Initialize progress.json

```json
{
  "project": "<detected project name>",
  "last_updated": "<now>",
  "last_agent": "human",
  "current_milestone": null,
  "current_task": null,
  "completed_milestones": [],
  "blockers": [],
  "learnings": [],
  "dependency_graph": {},
  "synced_plans": [],
  "agents": [],
  "stale_check": {
    "last_run": null,
    "stale_files": []
  }
}
```

No milestones, no tasks, no dependency graph — the project already exists.
All future work enters through plan mode → progress-sync → Task Execution Loop.

### Retrofit Step 6: Wire Scripts into Existing package.json

Add the harness scripts to the EXISTING package.json. Do NOT replace existing scripts.

```
Merge into existing "scripts":
  "validate": "tsx scripts/validate.ts",
  "validate:full": "tsx scripts/validate-full.ts",
  "file-guard": "tsx scripts/file-guard.ts",
  "stale-check": "tsx scripts/stale-check.ts",
  "progress-sync": "tsx scripts/progress-sync.ts",
  "validate-schema": "tsx scripts/validate-schema.ts",
  "changelog": "tsx scripts/changelog.ts"

Add to devDependencies:
  "tsx": "^4.0.0"

If "prepare" script exists → append husky to it
If "prepare" doesn't exist → add "prepare": "husky"
```

Adapt `validate.ts` to call the project's EXISTING lint/test/type-check commands,
not the harness defaults. For example, if the project uses `jest` instead of `vitest`,
validate.ts should run `jest`. Read from the existing `"test"` script in package.json.

### Retrofit Step 7: Present and Review

Present to the user:
1. File tree of what will be ADDED (not what exists)
2. List of existing configs that were PRESERVED (not overwritten)
3. Tech debt items detected
4. The generated AGENTS.md / CLAUDE.md for review
5. Ask: "Does this look right? Should I adjust anything?"

After confirmation, the user:
1. Copies the generated files into their existing project
2. Runs `<pkg-mgr> install` (to pick up tsx + husky)
3. Commits: `[scaffold] add harness framework`
4. Opens Claude Code / Codex → agent reads AGENTS.md / CLAUDE.md → ready

### After Retrofit: How It Works

The project now has the full harness layer but NO pending milestones.
The flow is entirely plan-mode-driven:

```
User opens Claude Code / Codex
  → Agent reads AGENTS.md / CLAUDE.md (Session Init)
  → Reads progress.json (no active milestones)
  → Runs stale-check (flags any issues)
  → Reports: "Harness active. No pending work. Ready for new tasks."

User enters plan mode
  → Describes new feature / fix / refactor
  → Plan file saved to docs/exec-plans/active/
  → Switch to normal mode

Agent detects new plan (progress-sync)
  → Parses plan into PRD update + new Milestone in PLAN.md
  → Updates progress.json with dependency graph
  → Creates worktree → Task Execution Loop
  → Same iron rules, same testing, same atomic commits
  → Milestone done → merge gate → tag → idle

Repeat.
```

No long-task bootstrap. No initial milestone grind. The project is already built.
The harness just gives agents the rails to do future work safely.

---

## Greenfield Workflow

For new projects from scratch. Full product discovery → PRD → scaffold → execution.

### Greenfield Workflow Overview

```
Phase 1: Product Discovery (interactive — 4 steps)
  Step 1: Product Type + Vision → ask_user_input + open-ended prose
  Step 2: Product Deep Dive → structured product review interview
  Step 3: Research → web search for competitors, tech stacks, best practices
  Step 4: Tech Stack Choices → ask_user_input informed by research

Phase 2: Product Requirements Review (generate PRD)
  → FRs with acceptance criteria, NFRs, MoSCoW prioritization
  → User journeys decomposed into epics → stories
  → Traceability: Requirement → Epic → Story → Task

Phase 3: Generate Project Artifacts
  → AGENTS.md + CLAUDE.md, ARCHITECTURE.md, PLAN.md, progress.json
  → Scaffold with full lint/test/CI/Docker/env infrastructure
  → Dependency graph, learnings log skeleton

Phase 4: Execution Runtime (long-task loop — see references/execution-runtime.md)
  → Session init protocol (progressive context loading)
  → Task execution loop (pick → execute → validate → commit → update)
  → Progress tracking via progress.json (cross-session memory)
  → Parallel worktree coordination (multi-agent)
  → Context budget management (≤40% utilization)
  → Quality checkpoints (auto vs human review gates)
  → Stale detection + agent learnings log
  → Dependency graph for task parallelism

Phase 5: Automated Testing (embedded in Phase 4 task loop)
  → Per-task: lint:fix → lint → type-check → unit test (validate)
  → Per-milestone: + integration + e2e tests (validate:full)
  → Product acceptance: verify PRD criteria covered by tests
  → CI: validate on PR, validate:full + deploy on merge to main

Phase 6: Documentation Site (evolves with project)
  → docs/site/ in GitBook-compatible format
  → Updated every milestone — doc tasks tracked in PLAN.md

Ongoing: Perpetual Development Loop
  → All milestones done → Idle Protocol → wait for user
  → User adds new work (in Claude Code / Codex or via claude.ai)
  → Update PRD + PLAN + progress.json → new milestone
  → Same Phase 4-6 loop restarts. Repeat forever.
```

---

## Phase 1: Product Discovery (Interactive)

### Step 1: Product Type + Vision

Use `ask_user_input` for the product type, then ask an open-ended follow-up.

**ask_user_input:**
1. **Project type** (single_select): What are you building?
   - Options: `Web App`, `Mobile (iOS/Android)`, `Desktop App`, `CLI Tool`, `Agent Tool / MCP Server`

**Then ask in prose (open-ended, do NOT use ask_user_input):**
> "Tell me about this product — who is it for, what problem does it solve, and what does
> success look like for the first version?"

Wait for the user's response before proceeding.

### Step 2: Product Deep Dive

Based on the user's vision, conduct a structured product review interview. The goal is to
extract enough information to write a rigorous PRD. Ask in prose — this is a conversation,
not a form.

Cover these areas (adapt based on what the user already told you — skip what's known):

**Users & Value:**
- Who are the primary user types? (e.g., end user, admin, API consumer)
- For each user type, what's the #1 thing they need to accomplish?
- What's the current alternative? (competitors, manual process, nothing)

**Core Journeys:**
- Walk me through the main thing a user does, step by step
- What are the critical decision points or error states?
- What does "done" look like for the user?

**Scope & Priority:**
- What are the absolute must-haves for v1? (things you'd delay launch for)
- What would be nice but can wait for v2?
- What are you explicitly NOT building?

**Constraints:**
- Any hard technical constraints? (must run offline, must support X platform, etc.)
- Performance requirements? (response time, concurrent users, data volume)
- Security/compliance needs? (auth, encryption, GDPR, HIPAA, etc.)

Don't ask all of these at once — have a natural conversation. Usually 2-3 exchanges
cover everything. Extract what you can from earlier messages and only ask what's missing.

### Step 3: Research — Web Search

Based on everything from Steps 1-2, run **2–5 web searches** to gather:

- **Competitors / similar products**: What exists? What's their stack? What do users love/hate?
- **Architecture patterns**: What's the proven approach for this type of product?
- **Tech stack recommendations**: What's current, well-supported, and fits the constraints?
- **Relevant APIs / services**: Auth, payments, hosting, etc.

Synthesize into a brief conversational summary: what you found, common patterns, and
your recommendations. This informs the user before they make tech stack decisions.

### Step 4: Refine — Tech Stack Choices

Use `ask_user_input` with options tailored by research. No generic lists.

**ask_user_input call 1 (adapt options to research results):**

1. **Tech layers** (multi_select): Which layers does this project need?
   - Options: `Frontend`, `Backend / API`, `Database`, `CI/CD Pipeline`

2. **Framework / stack** (multi_select): Based on research, here are the top fits:
   - Populate with 3–4 researched recommendations specific to this product
   - Example for Web App SaaS: `Next.js + Tailwind`, `Remix + Prisma`, `Nuxt 3 + tRPC`, `Other`
   - Example for CLI Tool: `Node.js (Commander.js)`, `Python (Click/Typer)`, `Go (Cobra)`, `Rust (Clap)`
   - Example for Agent Tool: `MCP Server (TypeScript)`, `LangGraph (Python)`, `CrewAI`, `Other`

3. **Database** (single_select, only if Database selected):
   - Example: `PostgreSQL + Prisma`, `Supabase`, `MongoDB`, `SQLite`

**ask_user_input call 2 (JS/TS projects only):**

4. **Package manager** (single_select): Which package manager?
   - Options: `pnpm`, `bun`, `npm`
   - Skip for Python/Go/Rust projects

**ask_user_input call 3 (deploy + ops):**

5. **Deploy target** (single_select): Where will this run?
   - Populate with 2–4 options relevant to the project type based on research
   - Example for Web App: `Vercel`, `Fly.io`, `AWS (ECS/Lambda)`, `Railway`
   - Example for CLI Tool: `npm registry`, `Homebrew`, `GitHub Releases`
   - Example for Mobile: `App Store`, `Google Play`, `TestFlight + Play Console`
   - Example for Agent Tool: `Docker self-hosted`, `Cloud Run`, `Fly.io`

6. **Monitoring & analytics** (multi_select): Which operational layers do you want?
   - Options: `Error tracking (Sentry)`, `Analytics (Google Analytics / Posthog)`, `Health checks + uptime`, `Structured logging`

---

## Phase 2: Product Requirements Review

After discovery, generate a rigorous PRD. This is NOT a loose feature list — it's a
structured product document with traceability from requirements down to tasks.

### Core Principles for Requirements

1. **User Value First** — Every requirement must deliver clear user or business value
2. **Testable & Measurable** — All requirements have explicit acceptance criteria
3. **Prioritized Ruthlessly** — Use MoSCoW: Must / Should / Could / Won't
4. **Traceable** — Clear path: Requirement → Epic → Story → Task in PLAN.md

### PRD.md Structure

```markdown
# Product Requirements Document: <Project Name>

## 1. Overview
One paragraph: what the product does, the problem it solves, target users.

## 2. User Personas
For each user type identified in discovery:
| Persona | Role | Primary Goal | Pain Point |
|---------|------|-------------|------------|

## 3. User Journeys
For each persona, describe 2-3 key journeys:

**Journey: <Name>**
Persona: <who>
Trigger: <what starts this journey>
Steps:
1. User does X → System responds Y
2. User does A → System responds B
3. ...
Success state: <what "done" looks like>
Error states: <what can go wrong and how system handles it>

## 4. Functional Requirements

Each FR must have: ID, description, acceptance criteria, priority, and parent journey.

| ID | Requirement | Acceptance Criteria | Priority | Journey |
|----|-------------|-------------------|----------|---------|
| FR-001 | User can sign up with email | - Email validated - Confirmation sent within 5s - Account active after confirm | Must | Onboarding |
| FR-002 | ... | ... | Should | ... |

Priority uses MoSCoW:
- **Must** — Launch blocker. Product doesn't work without it.
- **Should** — Important. Delay is painful but survivable.
- **Could** — Nice to have. First to cut if behind schedule.
- **Won't (v1)** — Explicitly out of scope for this version.

## 5. Non-Functional Requirements

| ID | Category | Requirement | Metric | Priority |
|----|----------|-------------|--------|----------|
| NFR-001 | Performance | Page load time | < 2s on 3G | Must |
| NFR-002 | Security | Auth tokens | JWT with refresh, 15min expiry | Must |
| NFR-003 | Accessibility | WCAG compliance | Level AA | Should |
| NFR-004 | Analytics | User behavior tracking | GA4 / Posthog core events instrumented | Must |
| NFR-005 | Monitoring | Error tracking | Sentry integrated, <5min alert latency | Must |
| NFR-006 | Monitoring | Health checks | /health endpoint, uptime monitoring | Must |
| NFR-007 | Observability | Structured logging | JSON logs with request ID, level, timestamp | Must |
| NFR-008 | Release | Feature flags | Flag service integrated, flags for all new features | Should |

Populate actual NFRs based on project discovery. The above are COMMON defaults —
include them unless the project explicitly doesn't need them (e.g., CLI tools
don't need GA or health endpoints). Always ask during Step 2 if unclear.

## 6. Tech Stack
| Layer | Choice | Rationale |
|-------|--------|-----------|

## 7. Data Model
Key entities, their relationships, and core fields. Expand in design docs later.

## 8. API Surface (if applicable)
Key endpoints/commands with method, path, brief description, and auth requirement.

## 9. Epics & Stories Breakdown

Decompose FRs into epics, then into user stories. This is the bridge to PLAN.md.

### Epic E1: <Name> (covers FR-001, FR-002)
| Story ID | As a... | I want to... | So that... | Acceptance Criteria | Estimate |
|----------|---------|-------------|-----------|-------------------|----------|
| E1-S01 | new user | sign up with email | I can access the app | - Valid email required - Password 8+ chars - Confirmation email sent | S |
| E1-S02 | new user | confirm my email | my account is activated | - Click link → account active - Link expires in 24h | S |

Estimates: XS (< 1h), S (1-4h), M (4-8h), L (1-2d), XL (2-5d)

### Epic E2: <Name> (covers FR-003, FR-004)
...

## 10. Out of Scope (v1)
Explicit list of what we're NOT building. Reference Won't items from FRs.

## 11. Open Questions
Unresolved decisions that need input before implementation.
```

### After generating PRD

Present the PRD to the user and explicitly ask them to review:
- Are the Must-have FRs correct? Anything missing or over-scoped?
- Do the user journeys match what you had in mind?
- Any acceptance criteria that need adjusting?

Incorporate feedback before moving to Phase 3.

---

## Phase 3: Generate Project Artifacts

### File Structure

```
<project-name>/
├── AGENTS.md                    ← Codex reads this (identical to CLAUDE.md)
├── CLAUDE.md                    ← Claude Code reads this (identical to AGENTS.md)
├── ARCHITECTURE.md              ← domain map, dependency layers, patterns
├── docs/
│   ├── PRD.md                   ← product requirements (from Phase 2)
│   ├── PLAN.md                  ← granular milestones + tasks
│   ├── progress.json            ← machine-readable cross-session state
│   ├── learnings.md             ← agent learnings log (human-readable)
│   ├── frontend-design.md       ← frontend design skill (read before any UI work)
│   ├── design-docs/
│   │   └── .gitkeep
│   ├── exec-plans/
│   │   ├── active/
│   │   │   └── 001-initial-setup.md
│   │   └── completed/
│   │       └── .gitkeep
│   ├── tech-debt/
│   │   └── .gitkeep
│   └── site/                    ← project documentation site (GitBook style)
│       ├── SUMMARY.md
│       ├── README.md
│       ├── getting-started.md
│       ├── architecture.md
│       └── api-reference.md
├── src/
│   ├── lib/
│   │   ├── errors.ts
│   │   ├── logger.ts
│   │   ├── feature-flags.ts
│   │   ├── analytics.ts
│   │   └── env.ts
│   ├── middleware/
│   │   └── error-handler.ts
│   └── ...
├── scripts/
│   ├── validate.ts              ← single gate: lint → type-check → test
│   ├── validate-full.ts         ← extended gate: + integration + e2e + file-guard
│   ├── file-guard.ts            ← 500-line limit enforcer
│   ├── stale-check.ts           ← detects stale docs, env, plans
│   ├── progress-sync.ts         ← syncs exec-plans/active/ → PLAN.md
│   ├── validate-schema.ts       ← validates progress.json against schema
│   ├── check-commit-msg.ts      ← commit message format enforcer
│   └── changelog.ts             ← generates release notes from commits
├── schemas/
│   └── progress.schema.json     ← JSON Schema for progress.json
├── tests/
│   ├── unit/                    ← per-task tests (run in task loop)
│   ├── integration/             ← cross-module (run at milestone merge)
│   └── e2e/                     ← full user journeys (run at milestone merge)
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .env.example
├── .gitignore
├── .claude/
│   └── settings.json             ← plansDirectory → docs/exec-plans/active/
├── .codex/
│   └── config.toml               ← Codex project-level config
├── .husky/
│   ├── pre-commit               ← lint-staged + file-guard + schema (via tsx)
│   ├── commit-msg               ← [Mn-id] format enforcer (via tsx)
│   └── pre-push                 ← full validate (via tsx)
├── Dockerfile
├── docker-compose.yml
├── package.json / pyproject.toml / go.mod / Cargo.toml
└── README.md
```

---

## Artifact Generation Rules

### AGENTS.md + CLAUDE.md (Identical Content)

These two files have **the same content**. Generate one, copy to the other.
AGENTS.md is for Codex. CLAUDE.md is for Claude Code. Same rules, no divergence.

#### What is TEMPLATED (copy verbatim into every project):

Only the Iron Rules section is fixed:

```
## Iron Rules — Non-Negotiable

These rules are absolute. No exceptions. No workarounds. No "just this once."

### 1. 500-Line Hard Ceiling
No single file may exceed 500 lines. If approaching the limit, split it.
Extract modules, create sub-components, decompose. This is a wall, not a guideline.

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

- **Session Init Protocol** — This is what the agent does FIRST when starting a session.
  Generate with the real file paths for THIS project:

```
## Session Init — Do This First, Every Time

When you start a session, follow these steps in order. Do NOT skip any step.

1. You already read this file (AGENTS.md / CLAUDE.md). Good.
2. Read `docs/progress.json` — find out:
   - What milestone is current?
   - What task is in progress or next?
   - Are there any blockers?
   - Any relevant learnings for the current task?
3. Sync new plans: <pkg-mgr> run progress-sync  ← runs scripts/progress-sync.ts
   - If new plan files detected in docs/exec-plans/active/:
     → Script reports them. Parse and add as new milestones in PLAN.md
     → Update progress.json dependency graph
     → Add plan filename to synced_plans array in progress.json
     → Commit: [docs] sync plan: <plan file name>
4. Read the CURRENT MILESTONE section of `docs/PLAN.md` (not the entire file).
5. If a task was in_progress:
   - Check for uncommitted changes (git status)
   - If dirty: run validate. Green → commit and continue. Red → fix first.
6. If no task in progress: pick the next ⬜ task where all dependencies are ✅.
7. Load ONLY the source files relevant to that task. Do not load the entire codebase.

Context budget:
- Steps 1-4: ≤ 30% of your context window
- Source files for current task: ≤ 30%
- Remaining ≥ 40% reserved for code generation and reasoning
- If you feel overloaded (repeating yourself, forgetting rules): stop, commit what
  works, update progress.json, and start a fresh session.
```

- **Task Execution Loop** — The autonomous work cycle. Generate with THIS project's
  actual validate commands:

```
## Task Execution Loop

Repeat this loop until the milestone is complete or you need human input.

### Pick
Find the next task in PLAN.md where status is ⬜ and all depends_on are ✅.
If no task is available: milestone is done → go to Merge Gate.
If all remaining tasks are blocked: pause and request human review.

### Claim
- Update docs/progress.json: set current_task with id, description, status: "in_progress"
- Update PLAN.md: mark task 🟡
- Commit: [M<n>-<id>] start: <description>

### Execute
Write / modify code to satisfy the "Done When" criteria in PLAN.md.
Load only the files you need. Stay within context budget.

### Validate
Run the full validation loop:
1. <pkg-mgr> run validate       ← runs scripts/validate.ts (lint:fix → lint → type → test)
If it fails → fix code → re-run. Script handles the full loop.
Max 3 retries. If still failing after 3 attempts:
- git stash
- Add task to blockers in progress.json with error details
- Log in learnings if you figured out something useful
- Pick the next unblocked task

### Commit
- git add + commit: [M<n>-<id>] <what was done>
- Update PLAN.md: mark task ✅, fill Commit column with hash
- Update progress.json: increment tasks_done, clear current_task
- If you learned something unexpected, add to learnings

### Repeat
Go back to Pick.
```

- **Merge Gate** — What to do when all tasks in a milestone are complete:

```
## Milestone Merge Gate

When all tasks in the current milestone are ✅:

1. Run: <pkg-mgr> run validate:full  ← scripts/validate-full.ts (unit + integration + e2e + file-guard)
2. Run: <pkg-mgr> run stale-check    ← scripts/stale-check.ts (catch stale docs)
3. Check: all acceptance criteria from PRD verified by tests
4. Check: docs/site/ updated for any new features
5. If ALL green:
   - Generate changelog: <pkg-mgr> run changelog > CHANGELOG.md
   - cd ../<project>
   - git merge milestone/M<n>
   - git tag v<version>-M<n>
   - Run validate:full on main (catches merge conflicts)
   - Update progress.json: move milestone to completed_milestones
   - Move exec-plans/active/ → exec-plans/completed/
   - git worktree remove ../<project>-M<n>
6. If ANYTHING fails: fix in worktree, commit, re-run from step 1.
7. If merge gate fails 2x: request human review.
```

- **Stale Detection** — When and how to check for stale docs:

```
## Stale Detection

Run at: session start, every ~10 commits, and milestone completion.
Command: <pkg-mgr> run stale-check    ← runs scripts/stale-check.ts

The script automatically checks:
- .env.example vs env vars used in source code
- PLAN.md vs progress.json task count sync
- New modules in src/modules/ not in ARCHITECTURE.md
- New plan files not synced in progress.json
- Dead links in docs/site/SUMMARY.md

If the script exits non-zero → fix the stale items, commit, continue.
If a fix requires judgment → flag for human review in progress.json blockers.
```

- **Idle Protocol + Add New Work** — What to do when all milestones are complete,
  and how to handle new requirements:

```
## When All Milestones Are Complete

If progress.json shows no active milestone and no ⬜ tasks remain:

1. Run a final stale detection pass on all docs
2. Fix any stale docs, commit
3. Run validate:full on main — confirm everything green
4. Report: "All milestones complete. Project is green. Ready for new work."
5. WAIT for user input — do NOT invent new tasks

## Adding New Work

The recommended workflow for adding new work is **plan mode first**:

**Claude Code:**
1. Switch to plan mode (Shift+Tab)
2. Describe what you want to build
3. Claude generates a plan file → saved to docs/exec-plans/active/ automatically
4. Review the plan, edit if needed (Ctrl+G to approve)
5. Switch back to normal mode (Shift+Tab)

**Codex:**
1. Enter plan mode (Codex creates a read-only planning session)
2. Describe what you want to build
3. Codex generates a plan → per AGENTS.md instruction, writes to docs/exec-plans/active/
4. Review the plan, approve execution

**Both agents, after plan is created:**
6. On next Session Init, the agent detects the new plan file and:
   - Parses the plan
   - Adds new FRs to PRD.md with acceptance criteria
   - Creates new Epic + Stories in PRD.md §9
   - Creates new Milestone in PLAN.md with tasks (≤ 4h each)
   - Updates progress.json dependency graph
   - Commits: [docs] sync plan: <plan file name>
   - Begins the normal Task Execution Loop

For quick changes that don't need a plan (1-2 files, obvious diff):
- Just tell the agent directly: "Add [feature]. Create a task for it."
- The agent adds it to the current milestone or creates a mini-milestone
- Same loop applies
```

- **Git Workflow** — Worktree per milestone rules (the workflow is standard but
  project name, branch names, and commands should use the real project name):

```
## Git Workflow — Worktree per Milestone

### Branch Strategy
Each milestone in PLAN.md gets its own git worktree and branch:

git worktree add ../<project>-M<n> -b milestone/M<n>
cd ../<project>-M<n>
# All work happens here with atomic commits
# When complete and all tests pass:
cd ../<project>
git merge milestone/M<n>
git worktree remove ../<project>-M<n>

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

## Dependency Layers
Strict ordering — each layer can only import from layers to its left:
Types → Config → Lib → Service → Controller/Handler → UI/CLI

Enforced by ESLint import rules. Violations fail lint.

## Package / Module Structure
Map of src/ directories to domains:
src/
├── lib/          ← shared utilities (errors, logger, feature-flags, analytics, env)
├── modules/
│   ├── auth/     ← Auth domain (routes, service, model, tests)
│   ├── users/    ← Users domain
│   └── ...
├── middleware/    ← cross-cutting (error handler, auth guard, request logger)
└── config/       ← app config, env validation

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
- Target: <chosen deploy target>
- Build: <build command and output>
- Environment: <how env vars are injected in production>
- Health: /health and /health/ready endpoints

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

### Scaffold Generation

Generate actual source files appropriate to the chosen stack. Not empty dirs.

**BEFORE generating any config file, read the reference templates:**
- `references/gitignore-templates.md` — .gitignore assembled per stack
- `references/eslint-configs.md` — ESLint flat configs per framework
- `references/project-configs.md` — tsconfig, prettier, vitest, Docker, CI, Python configs
- `references/harness-scripts.md` — validate, stale-check, progress-sync, file-guard, changelog scripts
- `references/schemas-and-hooks.md` — progress.json JSON Schema, git hooks (pre-commit, commit-msg, pre-push)

Never write configs or scripts from memory. Always reference these files and adapt.
The templates use the strictest settings — never downgrade. If strict rules cause errors,
fix the code, not the config.

**Mandatory test & lint infrastructure (every project, no exceptions):**

For JS/TS projects, always generate:
- `eslint.config.js` (flat config) with strict rules appropriate to the framework
- `.prettierrc` + `.prettierignore`
- `tsconfig.json` with `strict: true` if TypeScript
- Test framework config (vitest.config.ts, jest.config.ts, etc.)
- NPM scripts in package.json for the full testing loop:
  ```json
  {
    "scripts": {
      "lint": "eslint . --report-unused-disable-directives --max-warnings 0",
      "lint:fix": "eslint . --fix",
      "type-check": "tsc --noEmit",
      "test": "vitest run",
      "test:integration": "vitest run --project integration",
      "test:e2e": "vitest run --project e2e",
      "test:watch": "vitest",
      "validate": "tsx scripts/validate.ts",
      "validate:full": "tsx scripts/validate-full.ts",
      "file-guard": "tsx scripts/file-guard.ts",
      "stale-check": "tsx scripts/stale-check.ts",
      "progress-sync": "tsx scripts/progress-sync.ts",
      "validate-schema": "tsx scripts/validate-schema.ts",
      "changelog": "tsx scripts/changelog.ts",
      "prepare": "husky"
    }
  }
  ```
  (Adapt command prefix to chosen package manager: `pnpm`, `bun`, or `npm run`)

**Harness scripts (every project — see `references/harness-scripts.md`):**

Add `tsx` as a dev dependency: `<pkg-mgr> add -D tsx`

Generate ALL scripts into `scripts/` as TypeScript files:
- `scripts/validate.ts` — the single gate (lint:fix → lint → type-check → test)
- `scripts/validate-full.ts` — extended gate (+ integration + e2e + file-guard + stale-check)
- `scripts/file-guard.ts` — 500-line enforcer (Iron Rule 1 as code, supports --staged)
- `scripts/stale-check.ts` — detects stale docs, env vars, plans, modules
- `scripts/progress-sync.ts` — detects new plan files, prompts sync to PLAN.md
- `scripts/validate-schema.ts` — validates progress.json against JSON Schema
- `scripts/check-commit-msg.ts` — commit message format enforcer for hooks
- `scripts/changelog.ts` — generates release notes from [Mn-id] commit messages

All scripts use only `node:` built-in modules — zero external dependencies beyond `tsx`.
Works identically on Windows, macOS, and Linux.

**Schemas (every project — see `references/schemas-and-hooks.md`):**

Generate `schemas/progress.schema.json` — the JSON Schema for progress.json.
This is validated automatically by:
- The pre-commit hook (when progress.json is staged)
- The validate-schema.ts script (callable anytime)

Agents don't need to "remember" the progress.json format — the schema rejects invalid writes.

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

Generate husky with THREE hooks (see `references/schemas-and-hooks.md` for full content):

- `.husky/pre-commit` — runs lint-staged + 500-line file guard + progress.json schema validation
- `.husky/commit-msg` — enforces `[Mn-id] description` format (rejects non-conforming commits)
- `.husky/pre-push` — runs full `scripts/validate.ts` before push

`lint-staged` config in package.json:
  ```json
  {
    "lint-staged": {
      "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
      "*.{json,md,yml,yaml}": ["prettier --write"],
      "docs/progress.json": ["npx tsx scripts/validate-schema.ts"]
    }
  }
  ```
- Setup script in package.json: `"prepare": "husky"`
- This creates a **4-layer enforcement chain**: pre-commit → commit-msg → pre-push → CI
  If something slips past one layer, the next catches it.

For Python: use `pre-commit` framework with ruff + mypy hooks.

**Claude Code + Codex configuration (every project):**

Generate BOTH config files to integrate plan mode with the harness:

**Claude Code — `.claude/settings.json`:**
```json
{
  "plansDirectory": "./docs/exec-plans/active",
  "permissions": {
    "allowedTools": ["Read", "Write", "Bash(git *)", "Bash(<package-manager> *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

**Codex — `.codex/config.toml`:**
```toml
# Codex reads AGENTS.md automatically from project root.
# Plans directory is not natively configurable in Codex — handled via AGENTS.md instructions.

approval_policy = "on-request"

[project_doc]
project_doc_max_bytes = 65536
```

**Why two configs:**
- Claude Code has native `plansDirectory` → plan mode output automatically lands in
  `docs/exec-plans/active/`. No extra instructions needed.
- Codex does NOT have a `plansDirectory` equivalent. Instead, the AGENTS.md includes
  an explicit instruction: "When creating a plan, write it to `docs/exec-plans/active/<name>.md`."
  Codex follows AGENTS.md instructions, so this achieves the same result via convention.

Both agents end up with plan files in the same location → Session Init detects and
syncs them identically, regardless of which agent created the plan.

**Environment management (every project):**

- `.env.example` with every required env var as `KEY_NAME=placeholder`:
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/dbname
  JWT_SECRET=your-secret-here
  SENTRY_DSN=https://your-dsn@sentry.io/project-id
  GA_MEASUREMENT_ID=G-XXXXXXXXXX
  FEATURE_FLAG_KEY=your-key-here
  ```
- `.gitignore` MUST include `.env`, `.env.local`, `.env.*.local` from line one
- `src/lib/env.ts` (or equivalent) — a typed env loader that validates all required
  vars exist at startup and throws a clear error if any are missing. Never use
  `process.env.X` directly in application code — always go through the typed loader.

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

## Phase 4: Execution Runtime (Long-Task Loop)

This phase covers everything from "artifacts generated" to "project complete."
It runs continuously across multiple sessions, potentially with multiple agents.

**BEFORE executing any task, read `references/execution-runtime.md`.**
It contains the full protocol for session init, progress tracking, task loop,
parallel coordination, quality gates, and feedback mechanisms.

### Key concepts (summary — details in reference file)

**Session Init Protocol:**
Every agent session starts with the same boot sequence:
1. Read AGENTS.md / CLAUDE.md (the map)
2. Read `docs/progress.json` (where are we?)
3. Read current milestone section of PLAN.md (what's next?)
4. Load ONLY the source files relevant to the current task
5. Begin task execution

Steps 1-3 must consume ≤ 30% of context window. Remaining 70% is for code and reasoning.

**Progress File (docs/progress.json):**
Machine-readable JSON tracking: current milestone, current task, completed milestones,
blockers, learnings, dependency graph, and active agents. Updated after every
significant action. This is the cross-session memory — if progress.json doesn't
know about it, it didn't happen.

Generate an initial `progress.json` in Phase 3 with:
- All milestones from PLAN.md
- Dependency graph for all tasks
- Empty learnings, blockers, and agents arrays

**Task Execution Loop (autonomous):**
```
PICK next unblocked task (⬜ + all deps ✅)
  → UPDATE progress.json + PLAN.md (mark 🟡)
  → LOAD relevant source files (context budget)
  → EXECUTE task
  → VALIDATE (lint:fix → lint → type-check → test)
     ├── ALL GREEN → COMMIT [Mn-id] + mark ✅ + update progress
     └── FAILED 3x → STASH, add blocker, log learning, pick next task
  → CHECK: milestone complete? → Merge Gate
  → CHECK: all remaining blocked? → Request human review
  → LOOP
```

**3-Strike Rule:**
If validate fails 3 times on the same task → `git stash`, add to blockers in
progress.json, log what went wrong in learnings, move on. Don't get stuck.

### Parallel Worktree Protocol

Multiple agents can work on independent milestones simultaneously:
- **One agent, one worktree** — never share
- **Milestones with no dependency can run in parallel** (check PLAN.md `Depends on`)
- **progress.json is the coordination point** — agents claim milestones via the `agents` array
- **Stale heartbeat (>1 hour) = reclaimable** — another agent can take over
- **Merge order follows dependency order** — even if M3 finishes before M1

### Context Budget

Performance degrades sharply beyond ~40% context utilization. Budget allocation:

| Zone | Budget |
|------|--------|
| System prompt + AGENTS.md | ≤ 15% |
| progress.json + current PLAN section | ≤ 10% |
| PRD section for current story | ≤ 5% |
| Source files for current task | ≤ 30% |
| Working memory (code + reasoning) | ≤ 40% |

**Progressive disclosure rules:**
- Never load entire codebase, entire PLAN, or entire PRD
- Load only files relevant to the current task
- If a file is >200 lines, load only the relevant section
- When context feels full → summarize, drop raw content, continue with summary
- Signs of overload: repeating itself, forgetting rules, conflicting patterns
  → Stop, commit what works, start fresh session

### Quality Checkpoints

| Event | Mode | Action |
|-------|------|--------|
| Task passes tests | **Auto** | Commit and continue |
| Task failed 3x | **Human** | Report blocker, wait |
| Milestone all done | **Auto** | Run merge gate |
| Merge gate fails | **Human** | Report, wait |
| Integration tests fail | **Human** | Report, suggest fix, wait |
| New module created | **Human** | Review ARCHITECTURE.md update |
| Security-sensitive change | **Human** | Always require review |
| Dependency conflict | **Auto** | Delete and rebuild (Iron Rule 3) |
| File approaching 500 lines | **Auto** | Split immediately (Iron Rule 1) |
| Stale doc detected | **Auto** | Update, commit, continue |

### Stale Detection

Run stale checks at: session init, every ~10 commits, and milestone completion.

| Artifact | Stale signal | Auto-fix? |
|----------|-------------|-----------|
| AGENTS.md / CLAUDE.md | Commands don't match scripts | Yes |
| ARCHITECTURE.md | New module not in doc | Yes |
| PLAN.md | Task done but status ⬜ | Yes |
| PRD.md | Implementation deviates from spec | No — flag for human |
| .env.example | New env var in code but not in example | Yes |
| docs/site/ | New feature but no doc | Yes |
| progress.json | Agent heartbeat >1h stale | Yes — mark reclaimable |

### Agent Learnings Log

When an agent hits an unexpected problem and solves it, log it in TWO places:
1. `progress.json → learnings[]` (machine-readable, searchable)
2. `docs/learnings.md` (human-readable, chronological)

```json
{
  "date": "2026-03-05",
  "context": "M1-003",
  "category": "dependency",
  "problem": "bcrypt native bindings fail on Alpine Docker",
  "solution": "Use bcryptjs (pure JS) instead",
  "affected_files": ["package.json", "src/lib/auth/hash.ts"],
  "prevention": "Prefer pure-JS packages for Docker compatibility"
}
```

During session init, scan learnings relevant to the current task (matching files or
category). Load those. Skip irrelevant history — don't waste context budget.

### Task Dependency Graph

Lives in `progress.json → dependency_graph`. Determines which tasks can run in
parallel and which are blocked.

```json
{
  "M1-001": { "depends_on": [], "blocks": ["M1-002", "M1-003"] },
  "M1-002": { "depends_on": ["M1-001"], "blocks": ["M1-004"] },
  "M1-003": { "depends_on": ["M1-001"], "blocks": ["M1-004"] }
}
```

A task is "ready" when: status is ⬜ AND all `depends_on` tasks are ✅.
Generate this graph in Phase 3 alongside PLAN.md.

### Integration Testing

Three test tiers, each with its own trigger:

| Tier | Scope | Runs when | Script |
|------|-------|-----------|--------|
| Unit | Per-module | Every task (validate loop) | `test` |
| Integration | Cross-module | Milestone merge gate | `test:integration` |
| E2E | Full user journey | Milestone merge gate | `test:e2e` |

```
tests/
├── unit/              ← run per-task
├── integration/       ← run at milestone merge
└── e2e/               ← run at milestone merge
```

Scripts:
- `validate` (per-task): lint + type-check + unit tests
- `validate:full` (milestone merge): lint + type-check + unit + integration + e2e

### Milestone Lifecycle (end-to-end)

```
1. CREATE worktree → 2. INIT session → 3. CLAIM milestone in progress.json
→ 4. TASK LOOP (pick → execute → validate → commit → update)
→ 5. MERGE GATE (validate:full + 500-line check + acceptance criteria)
→ 6. HUMAN REVIEW (if required by checkpoint matrix)
→ 7. MERGE to main + tag v<version>-M<n>
→ 8. POST-MERGE (integration tests on main + update progress + cleanup worktree)
→ 9. NEXT MILESTONE (check dependency graph → create new worktree → loop)
```

---

## Phase 5: Automated Testing Loop (runs within Phase 4)

The testing loop is embedded in every task execution. It is NOT a separate phase —
it runs inside the task loop defined in Phase 4.

### The Loop (runs on every task)

```
┌─────────────────────────────────┐
│  Write / modify code (1 task)   │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Run lint:fix (auto-fix)        │
│  e.g., eslint . --fix           │
└──────────────┬──────────────────┘
               ▼
┌─────────────────────────────────┐
│  Run lint check (strict)        │  ◄── zero errors, zero warnings
│  e.g., eslint . --max-warnings 0│
└──────────┬──────────┬───────────┘
           │ PASS     │ FAIL
           ▼          ▼
           │    Fix lint errors manually
           │    └── go back to lint:fix
           ▼
┌─────────────────────────────────┐
│  Run type-check                 │  ◄── zero errors
│  e.g., tsc --noEmit             │
└──────────┬──────────┬───────────┘
           │ PASS     │ FAIL
           ▼          ▼
           │    Fix type errors
           │    └── go back to lint:fix
           ▼
┌─────────────────────────────────┐
│  Run tests                      │  ◄── all pass
│  e.g., vitest run               │
└──────────┬──────────┬───────────┘
           │ PASS     │ FAIL
           ▼          ▼
           │    Fix failing tests
           │    └── go back to lint:fix (full restart)
           ▼
┌─────────────────────────────────┐
│  ALL GREEN → git add + commit   │
│  [M<n>-<task_id>] description   │
└─────────────────────────────────┘
```

**Key rules:**
- The loop restarts from lint:fix on ANY failure — never skip ahead
- lint:fix auto-corrects formatting, import order, unused vars
- Type-check after lint because auto-fix may change types
- Tests last because they're slowest
- NEVER commit with warnings or errors. Zero tolerance.
- Max 3 retries per task before stashing and moving on

### Milestone Merge Gate

```bash
<package-manager> run validate:full   # scripts/validate-full.ts — unit + integration + e2e + file-guard
<package-manager> run stale-check     # scripts/stale-check.ts — catch stale docs
<package-manager> run changelog > CHANGELOG.md  # generate release notes
```

If anything fails → fix, commit, re-run. Only merge when fully green.

### Product Acceptance Testing

After each milestone merge, verify PRD acceptance criteria:
1. For each completed story, pull acceptance criteria from PRD §9
2. Verify each criterion is covered by at least one test
3. Missing test → write it, run loop, commit
4. Update PLAN.md: mark stories verified

### CI Integration

Two workflows:

**ci.yml (every PR):**
- `validate` (lint + type-check + unit tests)
- `dependency-audit`

**deploy.yml (merge to main):**
- `validate:full` (lint + type-check + unit + integration + e2e)
- Build + deploy to target platform
- Sentry source map upload (if configured)

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

1. **Map, not encyclopedia** — AGENTS.md and CLAUDE.md stay concise. Deep info in linked docs.
2. **Dual-agent identical** — Always generate BOTH files with identical content.
3. **Iron rules templated, everything else dynamic** — Only the 6 coding iron rules are fixed. All other sections are written from the user's actual project.
4. **Everything in the repo** — If it matters, it's a versioned file. No tribal knowledge.
5. **Mechanically enforceable** — Rules are scripts and hooks, not prose. Pre-commit + commit-msg + pre-push + CI = 4-layer enforcement chain.
6. **Secrets never touch git** — .env in .gitignore from day zero. Typed env loader validates at startup. stale-check.ts detects missing .env.example entries.
7. **User value first** — Every requirement delivers clear user or business value.
8. **Testable & traceable** — Requirements → Epics → Stories → Tasks. Every task has "done when."
9. **Prioritized ruthlessly** — MoSCoW. Not everything is Must. Make hard choices.
10. **Granular decomposition** — Break milestones as fine as possible. ≤ 4h per task. If bigger, split.
11. **Code is cheap, clarity is priceless** — Delete and rewrite. Assume infinite tokens.
12. **First principles only** — Every abstraction justifies its existence. No cargo-cult.
13. **Worktree isolation** — Each milestone in its own worktree. Atomic commits. Merge only when green.
14. **Automated testing is continuous** — validate.ts on every task. validate-full.ts on every merge. Hooks + CI = no human gatekeeping needed for green code.
15. **Errors are structured** — Unified error classes, structured JSON logging, global error boundary.
16. **Schema-validated state** — progress.json has a JSON Schema. Commit hooks reject invalid writes. Format doesn't rot.
17. **Commit messages are parseable** — [Mn-id] format enforced by commit-msg hook. changelog.ts auto-generates release notes from them.
16. **Ship behind flags** — Every new user-facing feature goes behind a feature flag.
17. **Observe everything** — Analytics, error tracking, health checks, structured logs.
18. **Docs evolve with code** — Documentation site updates are milestone tasks, not afterthoughts.
19. **Progress is machine-readable** — progress.json is the single source of truth for cross-session state. Agents update it, agents read it, humans can inspect it.
20. **Context is finite** — Never load more than you need. Progressive disclosure. ≤40% context utilization.
21. **Learnings compound** — Every unexpected problem and its solution gets logged. Future sessions inherit past wisdom.
22. **Staleness is a bug** — Detect and fix stale docs, plans, and configs proactively. Don't wait for humans to notice.
23. **Parallel by default** — Independent milestones run in parallel. One agent, one worktree. Coordinate via progress.json.
24. **Human review at high-stakes moments** — Security changes, architecture decisions, merge gate failures get human eyes. Everything else is auto.
25. **Frontend = frontend-design skill** — All frontend output reads `docs/frontend-design.md` first. Bundled in the project so both agents can access it. No exceptions.
26. **The loop is perpetual** — Bootstrap, execute, idle, add work, execute again. The agent doesn't distinguish sprint 1 from sprint 10. Same rules, same flow, forever.

---

## Post-Generation

After creating all files:

1. Present the file tree overview
2. Highlight: PRD.md (review requirements), PLAN.md (review task granularity), AGENTS.md (review rules), progress.json (verify dependency graph)
3. Ask the user to review and confirm before execution begins
4. Suggest the first milestone and its first task as the entry point
5. If multiple milestones have no dependencies, suggest parallel execution

---

## Handoff to Claude Code / Codex

### What is the skill vs what is the project

```
harness-engineer/                ← THIS IS THE SKILL (stays in claude.ai)
├── SKILL.md                    ← Instructions for generating the project
└── references/                 ← Templates used DURING generation
    ├── eslint-configs.md       ← ESLint templates → becomes eslint.config.js
    ├── project-configs.md      ← tsconfig/prettier/vitest/Docker templates → becomes real files
    ├── gitignore-templates.md  ← .gitignore templates → becomes .gitignore
    ├── execution-runtime.md    ← Detailed protocol docs → summarized into AGENTS.md / CLAUDE.md
    └── harness-principles.md   ← Background context → informs generation

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
# Run the validate command from AGENTS.md / CLAUDE.md
<package-manager> run validate
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
