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
   - Options: `Web App`, `Mobile (Expo / React Native)`, `Desktop App`, `CLI Tool`, `Agent Tool / MCP Server`

If **Mobile** is selected → read `references/skill-mobile.md` now before proceeding.

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

5. **Monorepo** (single_select): Do you want a monorepo structure?
   - Options: `Yes — monorepo (apps/ + packages/)`, `No — single package`
   - Recommend monorepo if: the project has multiple layers (e.g. web + API + mobile),
     the user mentioned wanting to add features / apps later, or the stack is Next.js +
     separate backend, or the product has a clear public package (SDK, shared UI lib, etc.)
   - If monorepo: recommend `pnpm` workspaces (best monorepo support); note that `bun`
     workspaces also work; `npm` workspaces are functional but slower
   - Ask a follow-up in prose: "What apps or packages do you expect to add first?
     (e.g. `apps/web`, `apps/api`, `packages/ui`, `packages/db`)"
     Use the answer to pre-populate the initial workspace structure
   - Store choice as `MONOREPO=true/false` — referenced throughout scaffold generation

**ask_user_input call 3 (deploy + ops — DO NOT SKIP):**

6. **Deploy target** (single_select): Where will this run?
   - Populate with 3–4 options relevant to the project type based on research.
     Always include `Other` as last option.
   - **Full reference list — pick the best fits for the project type:**
     - Managed platforms (zero infra): `Vercel`, `Cloudflare Pages/Workers`, `Netlify`, `Railway`, `Render`
     - Container platforms: `Fly.io`, `AWS ECS/Fargate`, `Google Cloud Run`, `Azure Container Apps`
     - VPS / self-hosted: `VPS (Hetzner/DigitalOcean/Linode)`, `Self-hosted (Coolify/Dokku/Kamal)`
     - Serverless: `AWS Lambda`, `Cloudflare Workers`, `Supabase Edge Functions`
     - Mobile: `EAS (Expo Application Services)` — standard for Expo
     - CLI / Package: `npm registry`, `PyPI`, `Homebrew`, `GitHub Releases`
   - **Example combos by project type:**
     - Next.js SaaS: `Vercel`, `Cloudflare Pages`, `VPS (Hetzner/DO)`, `Other`
     - API / Backend: `Railway`, `Fly.io`, `VPS (Hetzner/DO)`, `Other`
     - Full-stack (Docker): `Fly.io`, `VPS (Hetzner/DO)`, `AWS ECS`, `Other`
     - Static site / JAMstack: `Cloudflare Pages`, `Vercel`, `Netlify`, `Other`
     - Agent / MCP tool: `Docker self-hosted`, `Cloud Run`, `Fly.io`, `Other`

7. **Deployment method** (single_select): How should it be packaged and deployed?
   - Options depend on the deploy target chosen in #6:
   - **Vercel / Netlify**: `Git push auto-deploy (managed)`, `CLI deploy (vercel / netlify deploy)`
   - **Cloudflare Pages**: `Git push auto-deploy`, `Wrangler CLI deploy`
   - **Cloudflare Workers**: `Wrangler CLI`, `Git push via Pages Functions`
   - **Fly.io / Railway / Render**: `Docker container`, `Buildpack (auto-detect)`
   - **VPS (Hetzner/DO/Linode)**: `Docker Compose + SSH deploy`, `Kamal (zero-downtime Docker)`, `Coolify (self-hosted PaaS)`, `Dokku (self-hosted Heroku)`
   - **AWS ECS / Cloud Run**: `Docker container + CI push to registry`
   - **AWS Lambda**: `Serverless Framework`, `SST`, `SAM`
   - **Mobile (EAS)**: `EAS Build (managed)` — typically the only answer
   - **CLI / Package**: `npm publish`, `GitHub Release + binary`, `Docker image`
   - This determines: Dockerfile generation, platform config files (vercel.json / wrangler.toml /
     fly.toml / docker-compose.yml / kamal deploy.yml), build commands, CI deploy steps

8. **CI/CD pipeline** (single_select): Which CI/CD provider?
   - Options: `GitHub Actions`, `GitLab CI`, `None (manual deploy for now)`
   - Default: `GitHub Actions` if repo is on GitHub
   - Note: some targets have built-in CI (Vercel/Netlify/Cloudflare auto-deploy on git push).
     Even then, still generate a CI workflow for `harness validate` on PR — deploy can be
     handled by the platform's built-in integration
   - This determines: which workflow files to generate (.github/workflows/ vs .gitlab-ci.yml),
     how deploy triggers are configured, and how secrets/env vars are referenced

**ask_user_input call 4 (monitoring + environments):**

9. **Monitoring & analytics** (multi_select): Which operational layers do you want?
   - Options: `Error tracking (Sentry)`, `Analytics (Google Analytics / Posthog)`, `Health checks + uptime`, `Structured logging`

10. **Environments** (multi_select): Which deployment environments do you need?
   - Options: `development (local)`, `staging / preview`, `production`
   - Default: all three. Deselect staging if project is very early/solo
   - This determines: how many env files to generate (.env.development, .env.staging, .env.production),
     what CI/CD pipelines to set up, and how EAS build profiles are named (for mobile)

---

### Handling "Other" Selections

**If the user selects `Other` for framework/stack**, ask in prose:
> "What stack did you have in mind? Describe the framework, runtime, or any tools you already
> know you want to use."

Then do a **targeted web search** for that stack:
1. Search: `<user's stack> production best practices 2024`
2. Search: `<user's stack> project structure`
3. Check if the stack suits the project type. If it's a mismatch (e.g., user says
   "Django" for a real-time mobile app), say so directly:
   > "Django is a strong choice for server-side web apps, but for a real-time mobile
   > experience you'd typically want a dedicated API layer (FastAPI, Node, etc.) plus
   > a mobile client. Here's what I'd suggest instead: [researched alternatives]."
4. Only proceed with the user's choice if it's genuinely suitable, or if the user
   explicitly confirms they want it anyway. Document any tradeoffs in the PRD tech stack
   section.

**If the user selects `Other` for deploy target**, ask in prose:
> "Where do you want to deploy? Describe the platform, hosting provider, or infrastructure
> you already have or prefer."

Then do a **targeted web search**:
1. Search: `<user's platform> deploy <framework> 2024`
2. Search: `<user's platform> CI CD setup`
3. Generate the appropriate platform config file (or note if one isn't needed).
   If the platform is unusual or undocumented, document the deploy steps in
   `docs/site/deployment.md` as prose rather than generating a config file.
4. Make sure the CI workflow's deploy step matches the chosen platform.

---

### Auth Stack Decision

After the user's tech stack is confirmed, ask:

**ask_user_input:**
1. **Authentication** (single_select): How will users authenticate?
   - Options: `Better Auth (self-hosted, TypeScript)`, `Clerk (managed)`, `Supabase Auth`, `Firebase Auth`, `None / custom`

If **Better Auth** is selected → read `references/skill-auth.md` now before generating
any auth code, env files, or scaffold. Better Auth requires specific env variables,
platform setup (Google Console, GitHub OAuth app, Apple Developer), and mobile-specific
configuration that must be generated correctly from the start.

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

Populate actual NFRs based on project discovery. The above are COMMON defaults for
**Web App / API** projects. For other project types, use these defaults instead:

**CLI Tool defaults:**
| ID | Category | Requirement | Metric | Priority |
|----|----------|-------------|--------|----------|
| NFR-001 | Performance | Startup time | < 500ms to first output | Must |
| NFR-002 | UX | Error messages | Human-readable errors to stderr, exit code 1 | Must |
| NFR-003 | UX | Help text | `--help` for every command, contextual examples | Must |
| NFR-004 | Compatibility | Exit codes | 0 = success, 1 = error, 2 = usage error | Must |
| NFR-005 | Output | Machine-readable output | `--format json` option on all data commands | Should |
| NFR-006 | Monitoring | Error tracking | Sentry (opt-in with `--telemetry` flag) | Could |

**Agent / MCP Server defaults:**
| ID | Category | Requirement | Metric | Priority |
|----|----------|-------------|--------|----------|
| NFR-001 | Reliability | Tool error handling | All tools return structured MCP errors, never raw exceptions | Must |
| NFR-002 | Performance | Tool response time | < 5s for most tools, timeout after 30s | Must |
| NFR-003 | Security | Input validation | All tool inputs validated against JSON Schema | Must |
| NFR-004 | Observability | Structured logging | JSON logs with tool name, duration, success/failure | Must |
| NFR-005 | Monitoring | Error tracking | Sentry integrated | Should |

**Desktop App defaults:**
| ID | Category | Requirement | Metric | Priority |
|----|----------|-------------|--------|----------|
| NFR-001 | Performance | Startup time | < 2s to interactive | Must |
| NFR-002 | Performance | Memory usage | < 200MB idle | Should |
| NFR-003 | UX | Offline support | Core features work without network | Must |
| NFR-004 | Security | Auto-update | Signed updates via electron-updater or Tauri updater | Must |
| NFR-005 | Accessibility | Keyboard navigation | All features keyboard-accessible | Should |

Always ask during Step 2 if unclear which NFRs apply.

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

**PRD story examples for other project types (use instead of the web app example above):**

CLI Tool:
```markdown
### Epic E1: Core Commands (covers FR-001, FR-002)
| Story ID | As a... | I want to... | So that... | Acceptance Criteria | Estimate |
|----------|---------|-------------|-----------|-------------------|----------|
| E1-S01 | developer | run `mycli init` | my project is configured | - Creates config file - Validates dir - Prints next steps | S |
| E1-S02 | developer | run `mycli deploy --env staging` | my app deploys | - Reads config - Shows progress - Exit 0/1 - Prints URL on success | M |
| E1-S03 | developer | get output as JSON | I can pipe/parse it | - `--format json` returns valid JSON - Default: table | S |
```

Agent / MCP Server:
```markdown
### Epic E1: Core Tools (covers FR-001, FR-002)
| Story ID | As a... | I want to... | So that... | Acceptance Criteria | Estimate |
|----------|---------|-------------|-----------|-------------------|----------|
| E1-S01 | LLM agent | call `search` tool | I get relevant results | - Schema validates input - Returns structured array - Handles empty | M |
| E1-S02 | LLM agent | call `create` tool | a record is created | - Validates required fields - Returns ID - Duplicate → error | M |
```

Desktop App:
```markdown
### Epic E1: App Shell + Core Screen (covers FR-001)
| Story ID | As a... | I want to... | So that... | Acceptance Criteria | Estimate |
|----------|---------|-------------|-----------|-------------------|----------|
| E1-S01 | user | launch the app | I see the main window | - App opens in <2s - Window sized correctly - Menu bar works | S |
| E1-S02 | user | use the core feature | I get value from the app | - Feature works offline - State persists between sessions | M |
```

### Resolving Open Questions — Mandatory Gate

**DO NOT proceed to Phase 3 until ALL Open Questions are resolved.**

After generating the PRD, present the Open Questions section explicitly and work
through each one with the user in conversation. Common categories:

**Technical decisions:** auth provider, database, API style (REST / tRPC / GraphQL),
state management, offline support, push notification triggers

**Product scope:** free vs paid tiers, permission model (who can edit/delete what),
legal/compliance (GDPR, HIPAA, age restrictions), multi-language from day one

**UX decisions:** what happens when a user hits a limit, error states for critical flows

For each open question, ask the user to decide. If the user defers ("figure it out"),
make a **concrete recommendation** and document it as a decided choice:
> "I'll default to tRPC since you're using Next.js + React Native — end-to-end type
> safety without a schema layer. Noted in PRD §6 Tech Stack."

Only mark a question resolved when there is an actual answer — not "TBD" or "decide later."
Update the PRD with resolved decisions before proceeding.

### After generating PRD — Approval Gate

Present the PRD to the user and ask them to review:
- Are the Must-have FRs correct? Anything missing or over-scoped?
- Do the user journeys match what you had in mind?
- Any acceptance criteria that need adjusting?
- Are all Open Questions resolved?

Incorporate all feedback. Then ask explicitly:

> **"All open questions are resolved and the PRD is finalized. Here's a summary of
> the key decisions: [list: stack, auth, DB, deploy target, environments, monorepo y/n].
> Every milestone will be built to production standards (Iron Rule 7): error handling,
> input validation, structured logging, zero build warnings, no TODO/FIXME in code.
> Shall I proceed to Phase 3 and generate the full project scaffold?"**

**Wait for the user to say yes before generating any files.**
Do not auto-proceed. Phase 3 generates a lot of files — the user must consciously
sign off on the plan before the agent starts building.

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
│   ├── harness.ts               ← entry point router (~50 lines)
│   ├── check-commit-msg.ts      ← commit message format enforcer (for hooks)
│   └── harness/                 ← CLI modules (each <350 lines)
│       ├── config.ts            ← constants, colors, output helpers
│       ├── types.ts             ← all interfaces
│       ├── state.ts             ← load/save progress + plan
│       ├── worktree.ts          ← worktree detection, enforcement, agent lifecycle
│       ├── tasks.ts             ← init, status, next, start, done, block, reset
│       ├── validate.ts          ← validate, file-guard
│       └── quality.ts           ← merge-gate, stale-check, schema, changelog, learn
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

**If MONOREPO=true**, replace the single-package structure above with:

```
<project-name>/
├── AGENTS.md
├── CLAUDE.md
├── ARCHITECTURE.md
├── docs/                        ← same as single-package (PRD, PLAN, progress.json, etc.)
├── apps/
│   ├── web/                     ← e.g. Next.js frontend (populate from user's answer)
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                     ← e.g. Express / Fastify backend
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── ui/                      ← shared component library
│   │   ├── src/
│   │   └── package.json
│   ├── db/                      ← shared DB client / schema (e.g. Prisma)
│   │   ├── prisma/
│   │   └── package.json
│   └── config/                  ← shared tsconfig, eslint, prettier configs
│       ├── tsconfig.base.json
│       ├── eslint.config.js
│       └── package.json
├── scripts/
│   ├── harness.ts               ← root-level entry point (validates all workspaces)
│   ├── check-commit-msg.ts
│   └── harness/                 ← CLI modules
├── schemas/
│   └── progress.schema.json
├── .github/
│   └── workflows/
│       ├── ci.yml               ← runs validate across all workspaces
│       └── deploy.yml
├── pnpm-workspace.yaml          ← declares apps/* and packages/* as workspaces
├── turbo.json                   ← optional: Turborepo pipeline for build/test/lint
├── package.json                 ← root package (private: true, scripts call turbo or pnpm -r)
├── tsconfig.json                ← root tsconfig (references all workspace tsconfigs)
├── .env.example
├── .gitignore
├── .claude/settings.json
├── .codex/config.toml
├── .husky/
│   ├── pre-commit
│   ├── commit-msg
│   └── pre-push
└── README.md
```

**Monorepo generation rules:**
- Pre-populate `apps/` and `packages/` based on the user's answer to the follow-up question.
  Only generate the packages they mentioned — don't invent extra ones.
- Each workspace package gets its own `package.json` with a scoped name:
  `@<project-name>/web`, `@<project-name>/api`, `@<project-name>/ui`, etc.
- Root `package.json` must have `"private": true` and workspace scripts
  (e.g. `"build": "pnpm -r build"` or `"build": "turbo build"`).
- `pnpm-workspace.yaml` always includes both `apps/*` and `packages/*`.
- Add `turbo.json` only if the user's project has 3+ workspaces or mentions CI performance.
  Otherwise keep it simple with `pnpm -r` scripts.
- `harness.ts` at the root runs validate across ALL workspaces in sequence.
  Add a `--workspace` flag so agents can validate a single package: `harness validate --workspace apps/web`.
- ARCHITECTURE.md must document the workspace dependency graph:
  which `apps/` depend on which `packages/`.
- In AGENTS.md / CLAUDE.md, add a **Monorepo Rules** section:
  - Shared code lives in `packages/` — never import across `apps/`
  - Each package is independently buildable and testable
  - Breaking changes to a `packages/` entry require updating all consumers in the same PR
  - New feature area → new workspace under `apps/` or `packages/` (don't bloat existing ones)

---

### Project-Type-Specific Scaffolds

The file structure above is the **Web App default**. For other project types, replace
the `src/` layout and adjust which files are generated. The harness layer (docs/, scripts/,
schemas/, .husky/, .claude/, .codex/) stays identical for every project type.

**If CLI Tool:**

```
src/
├── commands/              ← one file per command (e.g. init.ts, deploy.ts, config.ts)
│   └── index.ts           ← command registry + top-level parser
├── lib/                   ← shared utilities (errors, logger, config loader, output formatters)
│   ├── errors.ts
│   ├── logger.ts
│   ├── config.ts          ← read/write config files (~/.myapp/config.json)
│   └── output.ts          ← table / JSON / plain text formatters
├── prompts/               ← interactive prompts (if needed — inquirer / @clack/prompts)
└── index.ts               ← entry point: parse args → dispatch to command
```

Additional files for CLI projects:
- `package.json` must include `"bin": { "<cli-name>": "./dist/index.js" }` and `"type": "module"`
- `tsup.config.ts` or `esbuild` config for bundling to single distributable file
- If publishing to npm: `"files": ["dist"]`, `"main": "./dist/index.js"`, `.npmignore`
- If distributing as binary: `pkg` config or `bun build --compile` in CI
- **No Docker, no docker-compose** — skip unless user explicitly requests
- **No frontend-design.md** — skip for non-interactive CLIs
- **No middleware/** — CLIs don't have HTTP middleware
- **No health endpoints** — CLI NFRs focus on: startup time, error messages, exit codes

```
# CLI-specific package.json additions:
{
  "name": "<cli-name>",
  "version": "0.0.1",
  "type": "module",
  "bin": { "<cli-name>": "./dist/index.js" },
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format esm --dts",
    "dev": "tsx src/index.ts",
    "harness": "tsx scripts/harness.ts",
    "lint": "eslint . --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "prepare": "husky"
  }
}
```

**If Agent Tool / MCP Server:**

```
src/
├── server.ts              ← MCP server entry point (stdio or SSE transport)
├── tools/                 ← one file per tool
│   ├── index.ts           ← tool registry
│   ├── search.ts          ← example: search tool
│   └── create.ts          ← example: create tool
├── resources/             ← MCP resources (if applicable)
│   └── index.ts
├── prompts/               ← MCP prompt templates (if applicable)
│   └── index.ts
├── lib/                   ← shared utilities
│   ├── errors.ts
│   ├── logger.ts
│   ├── config.ts
│   └── api-client.ts      ← external API client (if tool calls external services)
└── index.ts               ← entry point: start server
```

Additional files for MCP/Agent projects:
- `package.json`: `"type": "module"`, `"bin": { "<server-name>": "./dist/index.js" }`
- Transport config: stdio (default for Claude Desktop) or SSE (for web integrations)
- **No frontend-design.md** — no UI
- **No middleware/** — MCP servers don't use HTTP middleware
- If deploying as Docker: include Dockerfile + compose for self-hosting
- If publishing to npm: include `bin` field for `npx <server-name>` usage

```json
// Example MCP server package.json:
{
  "name": "<server-name>",
  "version": "0.0.1",
  "type": "module",
  "bin": { "<server-name>": "./dist/index.js" },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm",
    "dev": "tsx src/index.ts",
    "harness": "tsx scripts/harness.ts"
  }
}
```

**If Desktop App (Electron):**

```
src/
├── main/                  ← main process (Node.js)
│   ├── index.ts           ← app lifecycle, window management
│   ├── ipc.ts             ← IPC handlers (main ↔ renderer)
│   └── menu.ts            ← native menus
├── renderer/              ← renderer process (React/Vue/etc.)
│   ├── App.tsx
│   ├── pages/
│   ├── components/
│   └── lib/
├── preload/               ← preload scripts (context bridge)
│   └── index.ts
├── shared/                ← types/utils shared between main and renderer
│   └── types.ts
└── lib/                   ← shared utilities
    ├── errors.ts
    └── logger.ts
```

**If Desktop App (Tauri):**

```
src/                       ← frontend (React/Vue/Svelte)
├── App.tsx
├── pages/
├── components/
└── lib/
src-tauri/                 ← Rust backend (auto-generated by Tauri)
├── src/
│   ├── main.rs
│   └── commands.rs        ← Tauri command handlers
├── Cargo.toml
└── tauri.conf.json
```

Desktop notes:
- **Include frontend-design.md** — desktops have UI
- Electron: `electron-builder` or `electron-forge` for packaging
- Tauri: `tauri build` for packaging
- Run web search for latest `<Electron|Tauri> project structure best practices`
  before generating scaffold — these frameworks evolve quickly

**If Python project (CLI or API):**

```
src/
├── <package_name>/
│   ├── __init__.py
│   ├── cli.py             ← entry point (click/typer)
│   ├── commands/           ← one file per command group
│   ├── lib/                ← shared utilities
│   └── config.py
tests/
├── unit/
├── integration/
└── conftest.py
```

Python notes:
- Use `pyproject.toml` for all config (ruff, mypy, pytest, build — see project-configs.md)
- **Harness CLI**: the harness scripts are still TypeScript — add `tsx` + `node` as dev
  dependency via `pip install nodeenv` or require Node.js installed. Alternative: generate
  a `scripts/harness.py` equivalent (simplified — init, validate, status only) and use
  `Makefile` targets as the primary interface: `make validate`, `make test`, `make harness-next`
- `Makefile` replaces `package.json scripts` as the command interface

**If Go project:**

```
cmd/
├── <app-name>/
│   └── main.go            ← entry point
internal/                  ← private packages
├── commands/              ← CLI commands (cobra)
├── config/
├── service/
└── lib/
pkg/                       ← public packages (if any)
tests/
└── ...
```

Go notes:
- Use `golangci-lint` for linting (see project-configs.md)
- Use `go test ./...` for testing
- **Harness CLI**: same as Python — either require Node.js for tsx, or generate a
  simplified `scripts/harness.sh` bash wrapper, or use Makefile targets
- Dockerfile: `FROM golang:1.22-alpine AS build` → `FROM alpine:3.19` (multi-stage)

---

