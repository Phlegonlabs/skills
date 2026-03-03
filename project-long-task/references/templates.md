# Phase 2: Document Templates

After confirmation, create the `docs/` directory and generate all documents (4 documents total).

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
- **Components**:
  - {Component 1}: {what it displays, states, interactions}
  - {Component 2}: {what it displays, states, interactions}
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
- {Third-party services and how they connect}

### Key Technical Decisions
{Record important decisions made during the interview, e.g., "chose WebSocket over SSE because..."}

## Hard Requirements
- {Any constraints the user mentioned}
- {Performance, security, accessibility requirements}

## Deliverable
A repo that contains:
- A working app implementing the features above
- Scripts: dev, build, test, lint, typecheck
- `docs/plans.md` — Full implementation plan with milestone tracking
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
- **Created**: {date}
- **Status**: In Progress

## Guiding Principles
- {2-3 principles derived from the project's nature}

## Verification Checklist (kept current)
- [ ] `{package-manager} run lint`
- [ ] `{package-manager} run typecheck`
- [ ] `{package-manager} run test`
- Last verified: not started

## Milestones

### Milestone 01 - Repo scaffold + tooling [ ]
Scope:
- Initialize {tech stack}
- Add testing, linting, type checking tooling
- Establish folder structure

Sub-tasks:
- [ ] 1.1 — {Atomic action, e.g., "Initialize project with {pm} init"}
- [ ] 1.2 — {e.g., "Install and configure linter (ESLint)"}
- [ ] 1.3 — {e.g., "Install and configure formatter (Prettier)"}
- [ ] 1.4 — {e.g., "Set up TypeScript config (tsconfig.json)"}
- [ ] 1.5 — {e.g., "Create folder structure per architecture.md"}
- [ ] 1.6 — {e.g., "Add test framework and verify with a smoke test"}
- [ ] 1.7 — {e.g., "Add dev/build/test/lint/typecheck scripts to package.json"}

Key files/modules:
- {list key files}

Acceptance criteria:
- {list criteria}

Verification:
- {commands to run}

### Milestone 02 - {Next logical step} [ ]
...

{Generate milestone count based on project complexity:
- Simple projects: 4-6 milestones
- Standard projects: 7-10 milestones
- Complex projects: 10-14 milestones
Each feature should map to 1-3 milestones depending on complexity.
Always start with scaffold and end with polish/verification.
For CLI tools: place CLI Foundation (CC) as Milestone 02, right after repo scaffold.}

{Sub-task generation rules:
- Every milestone MUST have a "Sub-tasks" section with numbered, checkboxed items
- Each sub-task is ONE atomic action that can be completed and verified independently
- Use format: "- [ ] N.M — {verb phrase describing a single action}"
- Target 3-8 sub-tasks per milestone depending on milestone scope
- Sub-tasks should follow a logical implementation order within the milestone
- Each sub-task should be small enough to complete in a single focused session
- Common sub-task patterns per milestone type:
  - UI feature: create component → add styling → wire up state → handle edge states → add tests
  - API/data: define schema/types → implement data layer → add validation → add error handling → add tests
  - Integration: set up client/SDK → implement core integration → add error handling → add tests
  - Polish: audit UX flows → fix edge cases → optimize performance → final verification
- When a milestone is in progress, check off sub-tasks as they are completed
- After ALL sub-tasks are checked, mark the milestone itself as complete}

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

## Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| {risk} | {impact} | {mitigation} |

## Implementation Notes
{Empty section — will be filled during implementation}
```

## File: `docs/implement.md`

Execution rules that enforce disciplined autonomous work.

Structure:
```markdown
# Execution Rules

## Non-negotiable Constraints
- Do not stop after a milestone to ask questions or wait for confirmation
- Proceed through every milestone in plans.md until complete
- **Production-ready only** — every line of code must be production-quality. Specifically:
  - **No hardcoded values**: No hardcoded URLs, API keys, port numbers, user IDs, or environment-specific
    values. All configuration must come from environment variables, config files, or constants with clear naming.
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
  - **File size guideline**: Target under **300 lines** for most source files.
    If a file needs to exceed this for valid reasons (e.g., framework conventions, strongly related logic),
    keep it well-structured and document why splitting would hurt cohesion.

## Execution Rules (follow strictly)
- Treat plans.md as the source of truth
- If anything is ambiguous, make a reasonable decision and record it in plans.md
- **Git strategy**: Initial implementation works directly on `main` — do NOT create feature branches.
  Branch rules (`feature/`, `fix/`, `refactor/`) apply only to post-init development after the project is fully set up.
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
- Work through milestones at the **sub-task** level:
  - Start each milestone by reading its sub-task list
  - Complete sub-tasks in order — check off each one in plans.md as you finish it
  - **Every sub-task MUST have its own commit** — no batching, no skipping. One sub-task = one commit.
    Commit message format: `milestone-{NN}.{M}: {sub-task description}`
    (e.g., `milestone-03.2: implement user login API endpoint`)
  - If a sub-task turns out to need a fix after committing, create a separate fix commit — do NOT amend
- After every milestone (all sub-tasks checked off):
  - Run verification commands (lint, typecheck, tests)
  - Fix all failures immediately
  - Add or update tests for the milestone's core behavior
  - Mark the milestone itself as complete in plans.md
  - Create a milestone-level commit: `milestone-{NN}: complete — {milestone title}`
- If a bug is discovered:
  - Write a failing test
  - Fix the bug
  - Confirm the test passes
  - Record a note in plans.md under "Implementation Notes"

## Validation Requirements
- Maintain the verification checklist in plans.md
- Enforce determinism where applicable with snapshot tests

## Completion Criteria (do not stop until all are true)
- All milestones in plans.md are implemented and checked off
- `{pm} run dev` works
- `{pm} run test`, `{pm} run lint`, `{pm} run typecheck` all pass
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

## Files: `CLAUDE.md` + `AGENT.md` (both at project root)

Generate both files at the repository root with **identical content**:
- `CLAUDE.md` — For Claude Code (auto-loaded when working in this project)
- `AGENT.md` — For any other AI coding tool

Both files must always stay in sync — when one is updated, the other should be updated too.

This file should be concise and actionable — it's a quick-reference for the AI, not a full spec.
The full details live in `docs/architecture.md`.

Structure:
```markdown
# {Project Name}

{One-sentence description.}

## !! Execution Protocol — READ FIRST !!

**Every time you read this file, start your response with: "Hey Jacky Bro"**
This confirms you have loaded the project context. No exceptions.

**Before starting ANY implementation work, you MUST read all docs below — no skipping:**

1. Read `docs/implement.md` — contains non-negotiable execution rules
2. Read `docs/plans.md` — find the current milestone to work on
3. Read `docs/architecture.md` — understand the full project context

**After reading all docs, confirm by listing which docs you read.** Do NOT proceed to implementation
until all relevant docs are loaded into context.

**Workflow for every task:**
1. Check `docs/plans.md` for the next unchecked milestone
2. Follow `docs/implement.md` rules strictly while implementing
3. After completing a milestone:
   - Run verification (lint, typecheck, test), fix all failures
   - Update `docs/plans.md` — check off the milestone, add implementation notes
   - Update `docs/documentation.md` — keep status, setup instructions, and repo structure in sync with reality
   - Commit with a clear message referencing the milestone
4. Move to the next milestone — do NOT stop to ask unless truly blocked

**NEVER skip reading `docs/implement.md` before executing. It contains critical rules about
verification, testing, commit discipline, and bug handling that must be followed at all times.**

## Key Docs
- `docs/implement.md` — **Execution rules (MUST read before any implementation)**
- `docs/plans.md` — Milestones and execution progress (update after each milestone)
- `docs/architecture.md` — Project background, user journeys, components, product spec, technical architecture
- `docs/documentation.md` — User-facing docs (keep in sync with reality)

## Tech Stack
- {Runtime}: {e.g., Bun}
- {Framework}: {e.g., React + Vite}
- {Styling}: {e.g., Tailwind CSS}
- {Database}: {e.g., PostgreSQL + Drizzle} (if applicable)
- {Testing}: {e.g., bun test + Vitest}

## Commands
- `{pm} run dev` — Start dev server
- `{pm} run build` — Production build
- `{pm} run test` — Run tests
- `{pm} run lint` — Lint
- `{pm} run typecheck` — Type check

## Project Structure
{Brief directory layout, e.g.:}
- `src/` — Application source
- `src/components/` — Reusable UI components
- `src/pages/` — Page-level components / routes
- `docs/` — Project documentation

## Coding Conventions
- {Key conventions derived from the interview and tech stack choices}
- {e.g., "Use server components by default, client components only when needed"}
- {e.g., "All API routes return typed responses using shared types from src/types/"}
- {e.g., "Components are colocated with their tests: Button.tsx + Button.test.tsx"}

## Current Status
See `docs/plans.md` for milestone progress.
```

Important rules for CLAUDE.md / AGENT.md:
- Keep it under 80 lines — it's loaded into context every conversation, so brevity matters
- Focus on what the agent needs to KNOW to work correctly, not on explaining the project to humans
- Commands and structure should be accurate and runnable
- Update both files together as the project evolves (e.g., new commands, changed structure)
