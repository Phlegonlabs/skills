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
- **Task/action tracking is mandatory**:
  - Before writing implementation code for a sub-task, add that sub-task to `tasks/todo.md` under Current Sprint (or mark it as in-progress if already listed)
  - After finishing the sub-task, move it to Completed and keep Blocked/Review updated as needed
  - Record key implementation actions/decisions in `docs/plans.md` under "Implementation Notes" as work progresses (not only at milestone end)
  - If a mistake, blocker, or correction occurs, record a prevention rule in `tasks/lessons.md` immediately
- **Immutable / Mutable Layers**:
  - **Immutable** (do NOT modify without informing the user first): `docs/architecture.md` (spec & contracts),
    `docs/implement.md` (execution rules), test files that encode accepted behavior
  - **Mutable** (free to modify during implementation): `src/`, config files, `docs/plans.md` (progress tracking),
    `docs/documentation.md` (kept in sync with reality)
  - If you need to change an immutable-layer file, **stop and tell the user** what you want to change and why.
    Only proceed after acknowledgement.
- If anything is ambiguous, make a reasonable decision and record it in plans.md
- Follow `docs/secrets.md` for any secrets/API key handling (storage, redaction, output/display)
- **Hook compatibility (Claude + Codex)**:
  - This workflow supports both `.claude/settings.json` and `.codex/settings.json`
  - Install hooks for both platforms by default (`setup-hooks.sh --platform both`) so the same guardrails apply regardless of runtime
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
- **First-Principles Execution**: before implementing or fixing any task, derive the root cause from product intent and architecture.
  - Avoid symptom-level fixes that do not resolve the underlying design or contract issue.
  - If root cause analysis proves the current module direction is wrong, rewrite the module instead of patch layering.
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
