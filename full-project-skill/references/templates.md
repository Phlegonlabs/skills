# Phase 2: Document Templates

After confirmation, create the `docs/` directory, `tasks/` directory, and generate all documents (core docs + task tracking files + AI quick references at repo root).

## File: `docs/architecture.md`

The single source of truth for the entire project — project background, product spec, user journeys,
components, and technical architecture. This document should be comprehensive enough that someone reading
it for the first time fully understands what's being built and how.

This document is written once during init and only updated when architecture decisions are made during
implementation. It should NOT be rewritten from scratch.

Structure:
```markdown
# {Project Name}

## Project Background
- **What**: {1-2 sentence description of what this product is}
- **Why**: {The problem it solves}
- **Who**: {Target users and their context}
- **Scope**: {What's in scope for this build, and what's explicitly out of scope}

## Core Goals
- {High-level goals derived from the interview}

## User Roles
- **{Role 1}**: {description and permissions}
- **{Role 2}**: {description and permissions}

## User Journeys

### {Role 1} Journey
1. {Step-by-step flow from entry to goal completion}
2. {Each step references which page/screen the user is on}
3. {Include decision points and branches}

### {Role 2} Journey
1. {How their experience differs}

### Edge Cases & Error States
- {Empty states, loading states, error handling}
- {First-time vs. returning user differences}
- {Role transitions}

## Pages & Components

### Page: {Page Name}
- **Purpose**: {What this page is for}
- **Wireframe / Frame sketch (low-fidelity)**:
  ```text
  {Rough layout using labeled boxes; include key regions like header/sidebar/main and the major components inside each.}
  {Example:}
  [Top Bar: Logo | Nav | User Menu]
  [Sidebar: Project List]
  [Main: Filters | Table/List | Pagination]
  [Dialogs/Drawers: Create, Edit, Delete Confirm]
  ```
- **Component tree (exhaustive)**:
  - {PageFrame}
    - {HeaderFrame}: {components}
    - {SidebarFrame?}: {components}
    - {ContentFrame}: {components}
    - {FooterFrame?}: {components}
    - {Overlays}: {dialogs/drawers/popovers/toasts used by this page}
- **Key components (details)**:
  - {Component 1}: {what it displays, required data, states, interactions}
  - {Component 2}: {what it displays, required data, states, interactions}
- **User actions**: {what can the user do on this page}
- **Responsive behavior**: {how it adapts to mobile vs. desktop}

### Page: {Page Name 2}
...

## Product Spec
{For each core feature, write a detailed section:}

### A) {Feature Name}
- {Bullet points describing what it does}
- {Sub-features and behaviors}
- {Edge cases or constraints}
- {Which pages/components are involved}

### B) {Feature Name 2}
...

## Technical Architecture

### Tech Stack
- {Framework, language, runtime}
- {CSS approach}
- {Database, API layer}
- {Key libraries}

### Guiding Principles
- {2-3 architectural principles, e.g., "server components by default", "optimistic updates"}

### Directory Structure
{Proposed folder layout}

### Data Model
{Key entities and their relationships — can be text or a simple diagram}

### API Design
{Key endpoints or data fetching patterns — if applicable}

### Integrations
- {Third-party services and how they connect (e.g., payments, email, analytics like GA4/GTM)}
- {If analytics is required: key events, consent strategy, and a strict "no PII in analytics" rule}
- **API Documentation Rule**: When implementing any third-party integration, use the **Context7 MCP tool**
  to fetch the latest API docs for that service before writing integration code. Do NOT rely on
  training-data knowledge of SDKs/APIs — always fetch current docs via Context7.
  - If Context7 is unavailable, fall back to WebSearch + WebFetch for official docs.
  - If official docs still cannot be fetched, ask the user for documentation links.
  - If links are unavailable, proceed only with best-effort assumptions + explicit caveats, and mark
    API-doc validation as a required pre-implementation checkpoint.

### Key Technical Decisions
{Record important decisions made during the interview, e.g., "chose WebSocket over SSE because..."}
{For **Standard** and **Complex** tier projects: use `docs/decisions.md` (ADR format) to track
decisions made during implementation. See `references/decisions-template.md` for the template.}

## Hard Requirements
- {Any constraints the user mentioned}
- {Performance, security, accessibility requirements}
- {Privacy/compliance requirements (PII, consent/cookies, retention, audit logging)}

## Deliverable
A repo that contains:
- A working app implementing the features above
- Scripts: dev, build, test, lint, typecheck
- `docs/architecture.md` — Architecture + product spec
- `docs/plans.md` — Full implementation plan with milestone tracking
- `docs/implement.md` — Execution rules
- `docs/secrets.md` — Secrets & API keys guidance
- `docs/documentation.md` — User-facing docs
- `docs/design.md` — Design system + page-level design spec
- `CLAUDE.md` — AI quick reference for Claude Code
- `AGENTS.md` — AI quick reference for agent runners (different operating focus)
- `tasks/todo.md` — Execution sub-task tracker
- `tasks/lessons.md` — Correction-derived prevention rules
- `.env.example` — Environment variable template (API keys/IDs, no real secrets)
```

## File: `docs/plans.md`

The execution plan — a living document updated as milestones are completed.

Structure:
```markdown
# {Project Name} Implementation Plan

## Project Metadata
- **Project**: {Project Name}
- **Platform**: {Web app / Desktop app / Mobile app / CLI / Hybrid}
- **Tech stack**: {runtime, framework, styling, database}
- **UI framework**: {e.g., shadcn/ui, Radix, Ant Design} (GUI projects only)
- **Deployment**: {e.g., Vercel, Cloudflare Pages, Electron installer}
- **Analytics**: {none / GA4 / GTM / other} (Web projects only)
- **Created**: {date}
- **Status**: In Progress

## Guiding Principles
- {2-3 principles derived from the project's nature}

## Verification Checklist (kept current)
- [ ] `{pm} run lint`
- [ ] `{pm} run typecheck`
- [ ] `{pm} run test`
- Last verified: not started

## Milestones

### Milestone 01 - Repo scaffold + tooling [ ]
Scope:
- Initialize {tech stack}
- Add testing, linting, type checking tooling
- Establish folder structure

Sub-tasks:
- 1.1 — {Atomic action, e.g., "Initialize project with {pm} init"}
- 1.2 — {e.g., "Install and configure linter (ESLint)"}
- 1.3 — {e.g., "Install and configure formatter (Prettier)"}
- 1.4 — {e.g., "Set up TypeScript config (tsconfig.json)"}
- 1.5 — {e.g., "Create folder structure per architecture.md"}
- 1.6 — {e.g., "Add test framework and verify with a smoke test"}
- 1.7 — {e.g., "Add dev/build/test/lint/typecheck scripts to package.json"}

Key files/modules:
- {list key files}

Acceptance criteria:
- {list criteria}

Trade-offs considered:
- {Alternative approach vs chosen approach: why chosen approach wins}
- {Constraint that ruled out a simpler path}
{Omit if no meaningful trade-offs for this milestone.}

Verification:
- {commands to run}

### Milestone 02 - {Next logical step} [ ]
...

{Generate milestone count based on the complexity tier assigned during Phase 1:
- Standard tier: 7-10 milestones
- Complex tier: 10-14 milestones
Each feature should map to 1-3 milestones depending on complexity.
Always start with scaffold and end with the **Production Readiness Gate** (Milestone PR, see below).
For web apps: if analytics/tracking is in scope (GA4/GTM), include an Analytics milestone (after core navigation/auth is stable, before Production Readiness Gate).
For CLI tools: place CLI Foundation (CC) as Milestone 02, right after repo scaffold.
The second-to-last milestone should be polish/verification. The LAST milestone is ALWAYS the Production Readiness Gate.}

{Sub-task generation rules:
- Every milestone MUST have a "Sub-tasks" section with numbered items (no checkboxes)
- Each sub-task is ONE atomic action that can be completed and verified independently
- Use format: "- N.M — {verb phrase describing a single action}"
- Target 3-8 sub-tasks per milestone depending on milestone scope
- Sub-tasks should follow a logical implementation order within the milestone
- Each sub-task should be small enough to complete in a single focused session
- For milestones with non-obvious implementation choices, document trade-offs considered.
- Common sub-task patterns per milestone type:
  - UI feature: create component → add styling → wire up state → handle edge states → add tests
  - API/data: define schema/types → implement data layer → add validation → add error handling → add tests
  - Integration: set up client/SDK → implement core integration → add error handling → add tests
  - Polish: audit UX flows → fix edge cases → optimize performance → final verification
 - Track sub-task execution progress in `tasks/todo.md` (Current Sprint / Completed)
 - After all sub-tasks for a milestone are complete in `tasks/todo.md`, mark the milestone itself as complete in `docs/plans.md`}

### Milestone CC - CLI Foundation [ ] (CLI projects only)
Set up the CLI entry point, argument parsing, help system, and output formatting infrastructure.

Scope:
- Set up CLI entry point with argument parser (e.g., `commander`, `yargs`, `citty`)
- Implement all subcommands as stubs with `--help` text and usage examples
- Implement global flags: `--help`, `--version`, `--verbose`, `--quiet`, `--json`, `--no-color`
- Set up output formatting layer (human-readable default, JSON with `--json`)
- Set up error handling: stderr for errors, correct exit codes (0/1/2)
- Respect `NO_COLOR` env var
- Detect piped stdin for non-interactive mode
- Set up config file loading if applicable (discovery, parsing, validation)
- Add graceful shutdown handler (SIGINT/SIGTERM)

Key files/modules:
- CLI entry point (e.g., `src/cli.ts` or `src/index.ts`)
- Command definitions (e.g., `src/commands/`)
- Output formatter (e.g., `src/utils/output.ts`)
- Config loader (e.g., `src/config.ts`)
- `bin` field in package.json

Acceptance criteria:
- `mytool --help` shows all commands with descriptions
- `mytool <cmd> --help` shows command-specific usage with examples
- `mytool --version` outputs version from package.json
- `mytool --json <cmd>` outputs valid JSON
- `NO_COLOR=1 mytool <cmd>` produces uncolored output
- Invalid command/args exits with code 2 and helpful error message to stderr
- Config file is loaded from expected location (if applicable)

Verification:
- `{pm} run build && ./dist/mytool --help` — verify help output
- `{pm} run build && ./dist/mytool --version` — verify version
- `{pm} run build && ./dist/mytool invalid-cmd 2>&1; echo $?` — verify exit code 2
- `NO_COLOR=1 {pm} run build && ./dist/mytool --help` — verify no ANSI codes

### Milestone WA - Web Analytics / Tracking [ ] (Web projects only, if analytics is in scope)
Instrument analytics (e.g., GA4/GTM) with consent and a typed event layer.

Scope:
- Decide analytics provider (GA4 via gtag, GTM, or other) and consent requirements
- Create a single analytics adapter module (avoid scattered direct SDK calls)
- Instrument page views + 3-10 key events derived from the user journeys
- Ensure analytics is disabled in dev/test by default (env-gated)
- Add tests for event payload building (and enforce "no PII" in analytics payloads)

Key files/modules:
- Analytics adapter (e.g., `src/analytics/`)
- Event schema/types (e.g., `src/analytics/events.ts`)
- Consent handling (if applicable)

Acceptance criteria:
- Analytics can be toggled via env/config (off in dev/test by default)
- Page view + key events are emitted through the adapter
- Consent requirements are respected (if applicable)
- No PII is sent in analytics payloads (explicitly documented)

Verification:
- `{pm} run test` — tests cover event payload builder
- `{pm} run build` — production build includes analytics only when enabled

### Milestone PR - Production Readiness Gate [ ] (MANDATORY — always the final milestone)
Verify the entire project is production-ready, not just functional. This milestone is the final
quality gate before the project can be considered complete.

Scope:
- Full audit of all code for production quality
- Verify no demo/prototype artifacts remain
- Confirm all features work end-to-end with real (non-mock) data paths
- Security, performance, and error handling review

Sub-tasks:
- PR.1 — Run full verification suite (`{pm} run lint`, `{pm} run typecheck`, `{pm} run test`) — zero failures
- PR.2 — Audit for hardcoded values: no hardcoded URLs, ports, API keys, user IDs, or env-specific values in source code
- PR.3 — Audit for prototype leftovers: no `// TODO`, no `console.log` debugging, no commented-out code blocks, no `any` types, no `@ts-ignore` without justification
- PR.4 — Audit for mock/placeholder data: no mock data in production code paths (only allowed in test files and dev seed scripts)
- PR.5 — Verify error handling: every async operation has error handling, every user-facing error has a meaningful message, no empty catch blocks
- PR.6 — Verify `{pm} run build` produces a clean production build with no warnings
- PR.7 — Verify `{pm} run dev` starts cleanly and all features work end-to-end
- PR.8 — Verify all environment variables are documented in `.env.example` and validated at startup
- PR.9 — Review file sizes: flag any source file over 500 lines and verify it's justified
- PR.10 — Final documentation sync: ensure `docs/documentation.md` accurately reflects the implemented state (setup, commands, structure, troubleshooting)
- PR.11 — Dependency security audit: run `{pm} audit` (or equivalent) and remediate high/critical vulnerabilities
- PR.12 — (Web/GUI projects) Accessibility check: verify keyboard navigation, ARIA labels on interactive elements, sufficient color contrast
- PR.13 — License audit: verify all production dependencies use permissive licenses (MIT/Apache/BSD) compatible with this project's distribution model

Key files/modules:
- All source files
- `.env.example`
- `docs/documentation.md`
- `package.json` (scripts section)

Acceptance criteria:
- All verification commands pass with zero errors and zero warnings
- No hardcoded secrets, URLs, ports, or environment-specific values in source code
- No TODO comments, console.log debugging, or commented-out code blocks
- No mock/placeholder data in production code paths
- Every async operation has proper error handling
- Production build succeeds cleanly
- Dev server starts and all features are functional end-to-end
- `.env.example` is complete and all env vars are validated at startup
- `docs/documentation.md` is accurate and up-to-date
- The project is ready to deploy — not a demo, not a prototype

Verification:
- `{pm} run lint` — zero errors
- `{pm} run typecheck` — zero errors
- `{pm} run test` — all tests pass
- `{pm} run build` — clean build, no warnings
- `{pm} run dev` — starts cleanly, manual smoke test of all features

## Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| {risk} | {impact} | {mitigation} |

## Implementation Notes & Lessons Learned
{Empty section — dual purpose:}
{1. Record bug fixes, workarounds, and unexpected discoveries during implementation}
{2. Capture lessons learned that should inform future work (also add to CLAUDE.md "Lessons & Prevention Rules")}
```

## File: `docs/implement.md`

Execution rules that enforce disciplined autonomous work.

Structure:
```markdown
# Execution Rules

## Non-negotiable Constraints
- Do not stall after a milestone — continue unless blocked or a user decision is required
- Proceed through milestones in plans.md until complete (or until scope is explicitly revised and recorded)
- **Production-ready only** — every line of code must be production-quality. Specifically:
  - **No hardcoded values**: No hardcoded URLs, API keys, port numbers, user IDs, or environment-specific
    values. All configuration must come from environment variables, config files, or constants with clear naming.
  - **No committed secrets**: Never commit real secrets. Use `.env` for local secrets and provide `.env.example` when applicable.
  - **Gitignore discipline**: Ensure `.gitignore` covers at minimum: `.env`, `node_modules/`,
    `dist/`, `.DS_Store`. Never commit build artifacts or dependency directories.
  - **No prototype-quality code**: No `// TODO`, no `any` types, no `console.log` debugging leftovers,
    no commented-out code blocks, no placeholder implementations that "work for now."
  - **No mock data in production paths**: Mock/seed data is only acceptable in test files and dev seed scripts,
    never in application code that runs in production.
  - **Proper error handling**: Every async operation has error handling. Every user-facing error has a
    meaningful message. No swallowed errors, no empty catch blocks.
  - **Proper typing**: Full TypeScript types for all function signatures, API responses, and data structures.
    No `as any` casts, no `@ts-ignore` unless truly unavoidable (with a comment explaining why).
  - **Proper validation**: All external input (user input, API responses, URL params) is validated at
    the boundary. Use schema validation (e.g., Zod) for complex structures.
  - **Proper separation of concerns**: Business logic, data access, and UI rendering are clearly separated.
    No god functions that do everything.
  - **Frontend-backend contract**: API contracts between frontend and backend must be explicitly defined
    and kept in sync at all times. Specifically:
    - Define **shared types** for all API request/response payloads in a common location (e.g., `src/types/api.ts`
      or a shared package). Both frontend and backend MUST import from this single source of truth — no duplicated
      type definitions.
    - Every API endpoint must have a **typed client function** on the frontend that mirrors the backend handler's
      input/output types. No raw `fetch` calls scattered across components.
    - Use **schema validation** (e.g., Zod) at the API boundary: backend validates incoming requests,
      frontend validates API responses in development. Schemas should derive from or align with the shared types.
    - When changing an API endpoint's contract (URL, method, params, response shape), update ALL layers
      in the same commit: backend handler → shared types → frontend client → calling components.
      Never leave the contract out of sync across commits.
    - **Error response format** must be standardized: agree on a single error shape
      (e.g., `{ error: string; code: string; details?: unknown }`) used by all endpoints.
      Frontend error handling must expect and parse this shape.
  - **Code Quality Red Lines**:

    | Metric | Target | Ceiling (hard limit) | Action when exceeded |
    |--------|--------|---------------------|----------------------|
    | File length | ≤ 500 lines | ≤ 800 lines | Must split or justify in plans.md |
    | Function length | ≤ 25 lines | ≤ 40 lines | Extract helper or refactor |
    | Nesting depth | ≤ 2 levels | ≤ 3 levels | Use early returns or extract |
    | Conditional branches per function | ≤ 3 | ≤ 3 | Extract strategy or use lookup |

    - **Target** = the norm you should design for. **Ceiling** = the absolute maximum before the code must be restructured.
    - If a file legitimately needs to exceed the target (e.g., framework conventions, strongly related logic),
      keep it well-structured, stay under the ceiling, and document the reason in plans.md.

## Execution Rules (follow strictly)
- **Production mindset from Day 1** — every line of code you write should be production-quality from the start.
  Do NOT write "get it working first, clean up later" code. There is no cleanup phase — each milestone's output
  must be deployable as-is. If you catch yourself writing a shortcut, fix it immediately.
- Treat plans.md as the source of truth
- **Immutable / Mutable Layers**:
  - **Immutable** (do NOT modify without informing the user first): `docs/architecture.md` (spec & contracts),
    `docs/implement.md` (execution rules), test files that encode accepted behavior
  - **Mutable** (free to modify during implementation): `src/`, config files, `docs/plans.md` (progress tracking),
    `docs/documentation.md` (kept in sync with reality)
  - If you need to change an immutable-layer file, **stop and tell the user** what you want to change and why.
    Only proceed after acknowledgement.
- If anything is ambiguous, make a reasonable decision and record it in plans.md
- Follow `docs/secrets.md` for any secrets/API key handling (storage, redaction, output/display)
- **Claude Code hooks compatibility**: Hook configuration in `.claude/settings.json` relies on Claude Code's
  hook event system and JSON protocol. It is not compatible with Codex CLI hooks.
- **Third-party API documentation**: When implementing any third-party integration (payment gateway,
  email provider, OAuth, analytics SDK, etc.), use the **Context7 MCP tool** to fetch the latest API
  docs for that service before writing any code. Do NOT rely on training-data knowledge of third-party
  SDKs — APIs change frequently and outdated implementations are a production risk.
  - If Context7 is unavailable, fall back to WebSearch + WebFetch for official docs.
  - If official docs still cannot be fetched, ask the user to provide API documentation links.
  - If links are still unavailable, proceed with best-effort assumptions + explicit caveats, and
    require API-doc validation before implementation starts.
- **Git strategy**: Follow the git workflow chosen in the interview. If unspecified, default to trunk-based development on `main`.
  If branches are used, follow the project's naming convention (commonly: `feature/`, `fix/`, `refactor/`).
- Implement with small, reviewable commits
- **CLI implementation** (CLI projects only): Every CLI tool must meet these standards:
  - `--help` for every command and subcommand, with usage examples and argument descriptions
  - `--version` outputs the version from package.json
  - Exit codes: `0` = success, `1` = runtime error, `2` = usage/validation error
  - All normal output to `stdout`, all errors and diagnostics to `stderr`
  - Support `--json` flag for machine-readable output where applicable
  - Respect `NO_COLOR` env var and `--no-color` flag — never force colors
  - If interactive prompts exist, detect piped stdin and skip prompts in non-interactive mode
  - Graceful shutdown on SIGINT/SIGTERM — clean up temp files, release locks
- **Frontend-backend integration** (full-stack projects only):
  - Implement API endpoints **before** the frontend that consumes them — backend-first, then wire up frontend
  - After implementing a backend endpoint, immediately verify it works (e.g., test or curl) before building the frontend caller
  - When building a frontend feature that calls an API, implement in this order:
    1. Shared types (request/response)
    2. Backend handler + validation
    3. Frontend API client function
    4. UI component that uses the client
    5. Integration test covering the full round-trip
  - Never use hardcoded mock data as a stand-in for a real API call in production code.
    If a backend endpoint isn't ready yet, create the typed client function that points to the real endpoint
    and gate the feature — do NOT fake the response shape inline.
- **Analytics / tracking** (Web projects only, if analytics is in scope):
  - Use a single adapter module (avoid scattered direct GA/gtag/GTM calls across UI components)
  - Gate analytics behind env/config (disabled in dev/test by default)
  - Never send PII in analytics payloads (document what counts as PII for this project)
  - Respect consent requirements and opt-out signals if applicable
  - Add tests for event payload building / adapter behavior
- **Code is cheap — rewrite over patch**: When implementation hits a dead end (wrong library,
  bad architecture, accumulating workarounds), do NOT keep patching. Instead:
  - **Rewrite trigger**: If a module needs repeated workaround patches or no longer matches the agreed architecture,
    delete/recreate the module and rewrite it cleanly instead of layering more fixes.
  1. Revert the failed changes (`git stash` or `git checkout -- .`)
  2. Record what failed and why in plans.md "Implementation Notes"
  3. Re-plan the milestone with an alternative approach
  4. Rewrite the affected module from scratch
  Patching a fundamentally wrong approach always costs more than a clean rewrite.
  When fixing bugs: write a failing test first, then delete the broken module and rewrite it —
  never patch buggy code to make it "work."
- Work through milestones at the **sub-task** level:
  - Start each milestone by reading its sub-task list
  - Complete sub-tasks in order — track each sub-task status in `tasks/todo.md` as you finish it
  - **1 sub-task = 1 atomic commit** (mandatory; no bundling multiple sub-tasks into one commit)
  - Commit messages: use Conventional Commits; optionally include the milestone in the scope
    (e.g., `feat(milestone-03.2): implement user login API endpoint`)
  - If a sub-task turns out to need a fix after committing, create a separate fix commit — do NOT amend
- After every milestone (all sub-tasks marked complete in `tasks/todo.md`):
  - Run verification commands (lint, typecheck, tests)
  - Fix all failures immediately
  - Add or update tests for the milestone's core behavior
  - **Production spot-check**: scan the milestone's code for hardcoded values, TODO comments, console.log,
    `any` types, mock data in production paths, or missing error handling. Fix any issues before proceeding.
  - Mark the milestone itself as complete in plans.md
  - Create a milestone-level docs/status commit (e.g., `docs(milestone-{NN}): mark complete — {milestone title}`)
- **Session Handoff Protocol** (when a session is ending or a new session begins):
  - **Before ending a session**:
    1. Check off all completed sub-tasks in `tasks/todo.md`
    2. For any in-progress sub-task, add a brief status note (what's done, what remains)
    3. Run verification commands (lint, typecheck, test) and record results
    4. Note any open questions or decisions needed in plans.md "Implementation Notes"
    5. Create a WIP commit with a clear message (e.g., `wip(milestone-{NN}): {sub-task} in progress — {status}`)
  - **Starting a new session**:
    1. Read `docs/implement.md` — reload execution rules
    2. Read `docs/plans.md` — identify the current milestone
    3. Read `tasks/todo.md` — find the active/in-progress sub-task
    4. Read `docs/architecture.md` sections relevant to the current milestone
    5. Confirm your understanding of the current state before writing any code
    6. Do NOT start implementing until you've confirmed where you left off
- If a bug is discovered:
  - Write a failing test
  - Fix the bug
  - Confirm the test passes
  - Record a note in plans.md under "Implementation Notes"
- **TDD/BDD Workflow**:
  - **New feature**: Write a failing test first → implement the minimum code to pass → refactor while green.
    Not every line needs TDD, but every user-facing behavior should have a test before the sub-task is marked done.
  - **Bug fix**: TDD is **mandatory** — write a failing test that reproduces the bug before writing the fix.
    The fix is not complete until the test passes.
  - **Integration tests**: Each milestone that adds a user-facing flow should include at least one integration
    test covering the happy path end-to-end. Add edge-case integration tests for critical flows.

## Validation Requirements
- Maintain the verification checklist in plans.md
- Enforce determinism where applicable with snapshot tests

## Completion Criteria (do not stop until all are true)

**The project is NOT complete until it is production-ready. "It works" is not enough — it must be
deployment-grade. The final milestone (Production Readiness Gate) enforces this explicitly.**

- All milestones in plans.md are implemented and checked off, **including the Production Readiness Gate**
- `{pm} run dev` works
- `{pm} run test`, `{pm} run lint`, `{pm} run typecheck` all pass with **zero errors and zero warnings**
- `{pm} run build` produces a clean production build
- **No prototype artifacts remain**: no `// TODO`, no `console.log` debugging, no `any` types,
  no `@ts-ignore` without justification, no commented-out code, no placeholder/mock data in production paths
- **No hardcoded values**: no hardcoded URLs, ports, API keys, user IDs, or environment-specific values
- **All environment variables** documented in `.env.example` and validated at startup
- Secrets/API keys handled safely per `docs/secrets.md` (if applicable): no secrets committed/logged; any user-issued API keys are show-once + hashed storage
- Analytics/tracking standards met (Web projects only, if analytics is in scope):
  - Page views + key events are instrumented through the adapter
  - Consent requirements are respected (if applicable)
  - No PII is sent in analytics payloads
  - Analytics is disabled in dev/test by default
- CLI standards met (CLI projects only):
  - Every command has `--help` with usage examples
  - `--version` works
  - Exit codes are correct (0/1/2)
  - `--json` output is valid JSON
  - `NO_COLOR` and `--no-color` are respected
  - Piped/non-interactive mode works without prompts
- Frontend-backend contract integrity (full-stack projects only):
  - All API types are defined in a shared location and imported by both sides
  - No raw `fetch` calls in components — all API access goes through typed client functions
  - API error responses follow the standardized error shape
  - Changing any API endpoint's contract updates all layers in the same commit
- documentation.md is accurate and complete
- **Production Readiness Gate passed** — the final milestone (Milestone PR) is complete, confirming:
  - Zero prototype artifacts (TODOs, console.log, any types, mock data in prod paths)
  - Zero hardcoded environment-specific values
  - All env vars documented and validated
  - Clean production build with no warnings
  - All features work end-to-end
  - The deliverable is ready to deploy to production — not a demo, not a proof-of-concept
```

## File: `docs/secrets.md`

Guidance for handling secrets and API keys (both integration keys and user-issued keys).

Structure:
```markdown
# Secrets & API Keys

## Principles
- Never commit secrets (API keys, tokens, private keys) to git
- Prefer environment variables for local dev and a secrets manager in production
- Redact secrets from logs, errors, and any user-facing output by default

## Local Development Setup
- Copy `.env.example` → `.env`
- Fill in required keys/IDs (never paste real secrets into docs)
- Never commit `.env`

## Integration Keys (3rd-party services)
- Store secrets in server-side env vars only (never ship secrets in client bundles)
- Validate required env vars at startup and fail fast with an actionable error (do not print secret values)
- Decide rotation strategy (how to rotate without downtime) and document it

## If This Product Issues API Keys to Users (optional)
- Generate high-entropy keys with a prefix (e.g., `sk_live_...`)
- Store only a hash (plus metadata); never store plaintext keys
- Show the full key only once at creation; afterwards show masked + last 4
- Support revoke/rotate; add audit logging, scopes/permissions, and rate limits

## Secret Scanning (recommended)
- Consider adding a pre-commit hook (e.g., `detect-secrets`, `git-secrets`, or GitHub secret scanning)
  to catch accidental secret commits before they reach the remote

## Output/Display Guidance
- Never print full keys by default (CLI/UI)
- If showing a key is required, make it explicit (e.g., "Reveal" / `--show-key`) and warn the user
- Ensure keys never appear in URLs, crash reports, or analytics events
```

## File: `docs/documentation.md`

User-facing documentation — a living document kept in sync with reality.

Structure:
```markdown
# {Project Name} Documentation

## What {Project Name} Is
- {1-2 sentence description}

## Status
- Milestone 01: pending
- Milestone 02: pending
...

## Local Setup
- Prerequisites: {runtime version}
- Install: `{pm} install`
- Start: `{pm} run dev`

## Environment Variables / API Keys
- Use `.env.example` as the template for required env vars (API keys/IDs)
- Create `.env` locally and fill values; never commit `.env`
- Production: set env vars in your hosting provider / secrets manager

## Verification Commands
- Lint: `{pm} run lint`
- Typecheck: `{pm} run typecheck`
- Tests: `{pm} run test`
- Build: `{pm} run build`

## Repo Structure Overview
_To be updated as implementation progresses._

## Troubleshooting
_To be updated as issues are discovered._
```

## File: `docs/design.md`

Design specification covering design system tokens, component inventory, composition patterns, interactive patterns, layout system, and page-level composition/behavior.

Structure:
````markdown
# {Project Name} Design Spec

## Part 1: Design System

### Design Principles
- 3-5 project-specific design principles that guide every UI decision
- Examples: "Dense information display", "Keyboard-first interaction", "Dark mode default",
  "Progressive disclosure", "Minimal chrome — content is the UI"
- These are captured during the Step 2.8 Design Direction interview

### Color System
- Brand / primary palette
- Neutral palette
- Semantic colors (success / warning / error / info)
- State tokens (hover / active / disabled / focus)
- Status color mapping (if applicable — e.g., statuses like "active", "archived", "blocked"
  each map to a specific semantic color)
- CSS variable naming convention — use semantic token names (e.g., `--color-primary`,
  `--color-surface-raised`), never raw color values in component code
- Color space convention (e.g., OKLCH for perceptual uniformity, HSL, hex)

### Typography
- Font families (primary, secondary, monospace if needed)
- Type scale with exact class patterns — define ALL allowed text styles as a table:

| Role          | Class / Token          | Size   | Weight   | Use Case                  |
|---------------|------------------------|--------|----------|---------------------------|
| Page title    | `text-page-title`      | 1.5rem | 600      | Top-level page headings   |
| Section title | `text-section-title`   | 1.125rem | 600    | Card/panel headings       |
| Body          | `text-body`            | 0.875rem | 400    | Default paragraph text    |
| Muted         | `text-muted`           | 0.8125rem | 400   | Secondary/helper text     |
| Tiny label    | `text-tiny`            | 0.6875rem | 500   | Badges, metadata          |
| Mono          | `font-mono`            | 0.8125rem | 400   | Code, IDs, timestamps     |
| Large stat    | `text-stat`            | 1.75rem  | 700    | Dashboard KPI numbers     |

- Rule: use the established scale only — no ad-hoc font sizes or weights in component code

### Spacing System
- Base spacing unit
- Spacing scale tokens
- Layout spacing conventions (section gap, card padding, grid gutters)

### Radius & Shadows
- Border radius scale (e.g., `rounded-sm` = 4px, `rounded-md` = 6px, `rounded-lg` = 8px)
- Usage guidelines (e.g., buttons use `rounded-md`, cards use `rounded-lg`, avatars use `rounded-full`)
- Shadow constraints (e.g., max `shadow-sm` — heavy shadows look dated and break flat aesthetics)

### Component Hierarchy
- **Tier 1 — UI library primitives**: Components from the chosen UI library (e.g., shadcn/ui Button,
  Dialog, Select). Rules: do NOT modify source code of primitives; extend behavior through composition
  and wrapper components.
- **Tier 2 — Custom composites**: Project-specific components that compose Tier 1 primitives into
  domain-specific building blocks (e.g., `{Entity}Row`, `StatusBadge`, `FilterBar`).
  These define the project's unique design language.
- **Tier 3 — Page components**: Full page layouts that compose Tier 1 + Tier 2 components.
  Pages should contain layout logic and data orchestration, not raw styling.
- **When to create a component vs use utility classes directly**:
  - Create a component when: a pattern appears 3+ times, has internal state, or needs consistent
    props/API across usages
  - Use utility classes directly when: the pattern is one-off, purely visual, and unlikely to be reused

## Part 2: Component Inventory

A living registry of all UI components in the project. Update this section whenever components
are added, removed, or have their API changed.

### UI Library Primitives
List all primitives used from the chosen UI library:

| Component  | Source          | Key Props / Variants   | Notes                      |
|------------|-----------------|------------------------|----------------------------|
| Button     | {ui-lib}/button | variant, size, disabled | Primary action component   |
| Dialog     | {ui-lib}/dialog | open, onOpenChange      | All modals use this        |
| ...        | ...             | ...                    | ...                        |

### Custom Components
For each custom composite component:
- **File**: `components/{component-name}.tsx`
- **Props**: key props and their types
- **Usage**: when and where to use this component
- **Code example**: minimal usage snippet

### Layout Components
Components that define page structure (e.g., `AppShell`, `Sidebar`, `PageHeader`, `ContentPanel`).

### Dialog & Form Components
Components for data entry and confirmation flows (e.g., `ConfirmDialog`, `EntityForm`, `FilterPanel`).

### Utilities & Hooks
Shared hooks and utility functions related to UI behavior (e.g., `useMediaQuery`, `useDebounce`,
`useClickOutside`, `formatDate`).

## Part 3: Composition Patterns

Recurring multi-component patterns that must be implemented consistently across the app.

### Pattern: {Pattern Name}
- **Where used**: list pages/contexts where this pattern appears
- **Structure**: describe the component arrangement
- **Rules**: consistency constraints (e.g., "leading slot always: StatusIcon first, then PriorityIcon",
  "action buttons right-aligned in footer")
- **Code example**: show how components compose together

{Repeat for each recurring pattern}

## Part 4: Interactive Patterns

Standard conventions for interactive states across all components.

### Hover States
- Convention for hover feedback (e.g., "subtle background change `bg-muted/50`, never change text color")
- Row hover behavior for lists/tables
- Button hover behavior per variant

### Focus States
- Focus ring convention (e.g., "2px ring, `ring-ring` color, `ring-offset-2`")
- Tab order expectations for key pages
- Focus trap behavior for modals/dialogs

### Disabled States
- Visual convention (e.g., "50% opacity, `pointer-events-none`, no hover effect")
- When to disable vs hide elements

### Inline Editing
- If applicable: how inline editing works (click-to-edit, save/cancel behavior, escape key handling)

### Popover / Selector Patterns
- If applicable: how popover-based selectors work (trigger element, popover content, selection behavior,
  keyboard navigation within popovers)

## Part 5: Layout System

### Overall App Layout
```
+--------------------------------------------------+
| Header / Toolbar                                  |
+--------------------------------------------------+
| Sidebar       | Main Content Area                 |
| (if present)  | +-------------------------------+ |
|               | | Page Header                   | |
|               | +-------------------------------+ |
|               | | Content                       | |
|               | |                               | |
|               | +-------------------------------+ |
+---------------+-----------------------------------+
```
- Named zones with dimensions (e.g., sidebar: 240px fixed, main: fluid)
- Responsive behavior (e.g., sidebar collapses to icon-only at <1024px, hidden at <768px)

### Content Area Layout
- Max content width constraints (if any)
- Standard page padding / margins
- Grid system used within content area (if applicable)

## Part 6: Living Design Guide

For GUI projects, maintain a living design guide page within the application.

### Route
- `/design-guide` (or `/storybook`, or project-appropriate route)
- This page is for development reference, not end-user facing

### Rules
- When a new Tier 2 component is created → add it to the design guide page
- When a component's API changes → update its design guide entry
- The design guide page must show:
  - All Tier 2 (custom composite) components with variants and states
  - Interactive examples (not just static renders)
  - Color palette and typography scale preview

### Section Structure
Each component section in the design guide should show:
1. Component name and description
2. All variants / sizes
3. Key states (default, hover, active, disabled, loading)
4. Usage code snippet
5. Props table

## Part 7: File Conventions

### Directory Structure
- `components/ui/` — Tier 1 UI library primitives
- `components/` — Tier 2 custom composites
- `app/` or `pages/` — Tier 3 page components
- `hooks/` — shared React hooks / composables
- `lib/` or `utils/` — utility functions, API clients, formatters
- `contexts/` or `stores/` — state management (contexts, stores, atoms)
- `types/` — shared TypeScript types

### Naming Conventions
- Components: `PascalCase.tsx` (e.g., `StatusBadge.tsx`, `FilterBar.tsx`)
- Hooks: `camelCase.ts` starting with `use` (e.g., `useMediaQuery.ts`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`, `apiClient.ts`)
- Pages/routes: follow framework convention (e.g., `kebab-case` for file-based routing)

### Import Conventions
- Use path aliases (e.g., `@/components/...`, `@/lib/...`) — no deep relative imports (`../../..`)
- Group imports: external deps → internal aliases → relative imports → styles

## Part 8: Common Mistakes

Project-specific anti-patterns to avoid. Update this section as the team discovers new pitfalls.

- **Raw colors**: Never use raw color values (`#3b82f6`, `blue-500`) — always use semantic tokens
  (`--color-primary`, `text-primary`)
- **Ad-hoc typography**: Never invent font sizes or weights outside the type scale — if a new
  text style is needed, add it to the scale first
- **Heavy shadows**: Avoid `shadow-md` or larger — they look dated and break flat/modern aesthetics.
  Use `shadow-sm` max or rely on border/background contrast
- **Forgetting dark mode**: If dark mode is supported, every color choice must work in both themes —
  test both during development
- **Inline styles**: Avoid inline style objects when utility classes or tokens cover the case
- **Prop drilling for theme**: Use CSS variables or context for theming — don't pass color/spacing
  props through component trees
- **Ignoring the component hierarchy**: Don't build Tier 3 (page) logic inside Tier 2 (composite)
  components — keep composition clean

{Add project-specific anti-patterns as they are discovered}

## Part 9: Page-Level Design

### Page: {Page Name}
- Purpose
- Layout description (regions, hierarchy, responsive behavior)
- Component arrangement (major sections and key component relationships)
- Interaction behavior (primary actions, transitions, loading/empty/error handling)
- State changes (default, hover/focus, loading, success, failure)
- ASCII wireframe:
  +--------------------------------------------------+
  | Header                                           |
  +----------------------+---------------------------+
  | Sidebar              | Main content              |
  | - nav item           | - section A               |
  | - nav item           | - section B               |
  +----------------------+---------------------------+

{Repeat for each page/screen in scope}
````

## File: `CLAUDE.md` (project root)

Assemble from `references/partials/`.
See ordering and conditional rules in `references/partials/_assembly-order.md`.

## File: `AGENTS.md` (project root)

Assemble from `references/partials-agents/`.
See ordering and conditional rules in `references/partials-agents/_assembly-order.md`.

Implementation notes:
- `CLAUDE.md` and `AGENTS.md` are intentionally different.
- Keep both concise and operational.
- Reflect command and structure changes in both templates when the project evolves.
