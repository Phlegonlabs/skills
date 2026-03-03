---
name: project-init
description: >
  Initialize a long-running project with a structured docs workflow. Use this skill whenever the user wants to
  start a new project, kick off a long-running build task, set up project documentation structure, or says things
  like "new project", "start a project", "init project", "project setup", or "I want to build something from scratch".
  Also use when the user mentions wanting a milestone-based plan, structured execution workflow, or asks to
  scaffold documentation for a complex multi-step build.
---

# Project Init

A structured project initialization workflow for long-running, milestone-based builds. This skill collects project
requirements through an interactive interview, then generates a complete documentation scaffold that guides
autonomous execution from planning through implementation.

## Why this structure works

Long-running tasks fail when context drifts or the executor loses track of what's done and what's next. This
workflow prevents that by separating concerns into distinct documents that each serve a clear purpose:

- A **spec** that never changes (what to build)
- A **plan** that tracks progress (what's done, what's next)
- **Execution rules** that enforce discipline (how to work)
- **Living docs** that stay accurate (architecture + user docs)

The interview phase is critical — it forces clarity before any code is written, which saves hours of rework later.

## Workflow

### Phase 1: Interactive Interview

Collect project information through conversation. Use `AskUserQuestion` for each step.

#### Step 1 — Project Name

Ask the user for the project name. This becomes the directory context and document titles.

Example question: "What's the project name?"

#### Step 2 — Project Goals (Free-form)

This is the most important step. Before diving into tech stack or feature lists, ask the user to describe
their project goals in their own words — what problem they're solving, who it's for, what the end result
should look like. This can be as brief or detailed as they want. The point is to capture intent and context
before any structured breakdown.

Example question: "Tell me about your project — what are you building, what problem does it solve, and who is it for? Just describe it in your own words, no need to be structured."

Let the user write freely. Do NOT interrupt with follow-up questions mid-description.

#### Step 3 — Clarifying Questions (AI-driven discovery)

This step is critical. Based on what the user described in Step 2, **analyze their goals and identify gaps
or ambiguities**, then ask targeted clarifying questions to flesh out the project scope.

Do NOT skip this step. Do NOT jump straight to feature lists or tech stack. The goal is to deeply understand
the project before generating anything.

The two primary goals of this step are:
1. **Map out every user journey** — understand all the different paths users take through the product
2. **Identify every component** — understand what UI/functional building blocks are needed and how they behave

Process:
1. Read the user's goals description carefully
2. Plan out a discovery interview of **9-12 base rounds**. The first section covers user journeys, the second
   drills into components and details, then a required tech baseline checkpoint, then UI preferences (GUI) or
   CLI interface design (CLI), and finally deployment. Cover these areas progressively (skip any already answered in Step 2):

   **--- User Journeys (Rounds 1-5) ---**

   **Round 1 — User roles & personas**: Who are the different types of users? (e.g., admin, regular user, guest,
   viewer). What are their goals and context? Ask the user to list every distinct role.

   **Round 2 — Primary user journey**: For the most important user role, walk through their complete journey
   step by step. From first landing / sign-up, through the core action, to the end goal. Ask: "Walk me through
   what [primary user] does from the moment they open the app to completing their main goal."

   **Round 3 — Secondary user journeys**: For each additional role identified in Round 1, ask about their
   distinct journey. How does their experience differ? What can they do that others can't? Focus on the
   differences from the primary journey.

   **Round 4 — Journey edge cases & transitions**: What happens when things go wrong? Error states, empty
   states, loading states. How do users transition between journeys? (e.g., a viewer gets upgraded to editor).
   What about first-time vs. returning user experience?

   **Round 5 — Journey validation & gaps**: Revisit the complete set of journeys mapped so far. Are there
   any missing flows? (e.g., onboarding, password reset, settings changes, data export). Ask the user to
   confirm the journey map is complete or identify gaps.

   **--- Components & Details (Rounds 6-10) ---**

   **Round 6 — Page/screen inventory**: Based on the journeys above, list out every page or screen the app
   needs. Ask the user to confirm and add any missing ones. For each page, ask: "What are the key elements
   on this page? What actions can the user take here?"

   **Round 7 — Component deep-dive**: For each page identified, drill into the specific components:
   - What data does each component display?
   - What states does it have? (loading, empty, error, success, disabled)
   - What interactions does it support? (click, hover, drag, swipe)
   - How does it behave on mobile vs. desktop?

   **Round 8 — Data flow & relationships**: How do components connect to each other?
   - What happens when you click a button — what changes on screen?
   - Which components share data?
   - What needs real-time updates vs. static content?
   - Any complex forms or multi-step workflows?

   **Round 9 — State management & persistence**: How is application state managed?
   - What data needs to persist across sessions?
   - What's stored locally vs. server-side?
   - Caching strategy? Optimistic updates?
   - How is authentication state handled?

   **Round 10 — Integrations, constraints & non-functional requirements**:
   - Third-party services or APIs to connect with?
   - Scale expectation (personal tool vs. SaaS vs. enterprise)?
   - Performance requirements? Offline support?
   - Any hard business rules or constraints?

   **Round 10.5 — Tech stack baseline checkpoint (required before UI/deployment)**:
   - Confirm runtime/package manager/framework baseline before entering UI and deployment rounds
   - Minimum fields to lock: runtime, frontend/backend framework, styling approach (if GUI), data/storage approach
   - If still undecided, propose 2-3 concrete stack options and ask the user to pick one as the working baseline

   **--- UI Preferences (Round 11, GUI projects only) ---**

   **Round 11 — UI component & styling approach**: Based on the project type, target users, and
   complexity gathered so far, ask about the UI implementation approach:
   - **UI library / component framework** — recommend based on the tech stack (e.g., shadcn/ui, Radix,
     Ant Design, Material UI, fully custom) and explain why it fits the project
   - **CSS approach** — Tailwind, CSS Modules, styled-components, vanilla CSS, etc.
   - **Key UI components** — based on all pages discussed, identify the shared UI primitives needed
     (e.g., Button, Input, Card, Modal, Table, Avatar, Badge, Toast, etc.)
   - **Iconography** — suggest an icon set (e.g., Lucide, Phosphor, Heroicons)
   - Ask the user to confirm or adjust

   **--- CLI Interface Design (Rounds 11C-13C, CLI projects only) ---**

   For CLI / terminal tools, ask these CLI-specific rounds:

   **Round 11C — Command structure & interface design**: Propose a CLI architecture based on the features
   gathered in Rounds 1-10:
   - **Command pattern** — single command with flags, subcommands (like `git`), or hybrid?
     Present concrete examples: `mytool --input file.txt` vs `mytool convert file.txt --format json`
   - **Argument parsing library** — recommend based on tech stack (e.g., `commander`, `yargs`, `citty`,
     `clipanion`, or built-in `parseArgs`)
   - **Global flags** — what flags apply to all commands? (e.g., `--verbose`, `--quiet`, `--json`, `--no-color`,
     `--config <path>`)
   - **Required vs optional args** — for each command, which arguments are required positional args vs optional flags?
   - Ask the user to confirm the command tree structure

   **Round 12C — Output formatting & interaction model**: Define how the CLI communicates with the user:
   - **Output modes** — human-readable (styled text, tables, colors) vs machine-readable (`--json` flag)?
     Propose supporting both with a flag.
   - **Interactive prompts** — does the CLI need interactive input? (e.g., confirmation prompts, multi-select,
     password input). If yes, recommend a library (e.g., `prompts`, `inquirer`, `@clack/prompts`)
   - **Progress reporting** — spinners, progress bars, or streaming output for long-running operations?
   - **Color & styling** — recommend a terminal styling approach (e.g., `chalk`, `picocolors`, ANSI direct).
     Must respect `NO_COLOR` env var and `--no-color` flag.
   - **Table output** — if the CLI displays tabular data, how should it be formatted?
   - **Verbosity levels** — default (normal), `--verbose` (debug info), `--quiet` (errors only)?
   - Ask the user to confirm or adjust

   **Round 13C — Error handling, config & conventions**: Define CLI behavior standards:
   - **Exit codes** — propose a strategy: `0` success, `1` general error, `2` usage error, custom codes for
     specific failures?
   - **Error output** — errors to `stderr`, normal output to `stdout`. Error messages should be actionable
     ("File not found: config.json. Run `mytool init` to create one.")
   - **Config file** — does the CLI need a config file? If yes: format (JSON/TOML/YAML), location
     (`~/.config/mytool/`, `.mytoolrc`, `mytool.config.ts`), discovery strategy (walk up directories?)
   - **Pipe support** — should the CLI work in pipes? (`cat file | mytool process | jq .result`)
     If yes, detect `stdin` pipe and adjust behavior (no colors, no interactive prompts)
   - **Shell completions** — generate completions for bash/zsh/fish?
   - **Version & help** — `--version` and `--help` / `mytool help <command>` are mandatory
   - Ask the user to confirm or adjust

   **--- Deployment (Round 14) ---**

   **Round 14 — Deployment platform & infrastructure**: Ask the user where and how the project will
   be deployed. Present options tailored to the platform type and any tech preferences already mentioned:

   For **Web apps**:
   - **Hosting platform** — Cloudflare Pages/Workers, Vercel, Netlify, AWS, self-hosted, other?
   - **Why it matters** — the deployment target affects build config, edge functions, middleware,
     environment variable handling, and framework-specific optimizations (e.g., Next.js on Vercel
     vs. Cloudflare has different adapter requirements)
   - **Database / backend hosting** — if applicable: Cloudflare D1, Vercel Postgres, PlanetScale,
     Supabase, Railway, self-hosted?
   - **Domain & CDN** — custom domain? CDN strategy?
   - **CI/CD** — GitHub Actions, Vercel auto-deploy, Cloudflare Pages auto-deploy?

   For **Desktop apps**:
   - **Distribution** — installer (MSI/DMG), portable exe, app store, auto-update mechanism?
   - **Code signing** — needed for distribution?
   - **Update server** — where will updates be hosted?

   For **Mobile apps**:
   - **Distribution** — App Store, Google Play, TestFlight, internal distribution?
   - **OTA updates** — CodePush, EAS Update, etc.?

   For **CLI tools**:
   - **Distribution** — npm registry, standalone binary (pkg/bun build --compile), Homebrew tap, GitHub Releases?
   - **Global install** — `npm i -g`, `npx`, `bunx`, or standalone executable?
   - **Auto-update** — built-in update check, or rely on package manager?
   - **CI/CD** — automated publishing on git tag? GitHub Actions workflow?

   Record the deployment choice — it affects `docs/architecture.md` (Technical Architecture section),
   `docs/plans.md` (deployment milestone), and `CLAUDE.md` / `AGENT.md` (build/deploy commands).

3. Each round: ask **1-2 focused questions** using `AskUserQuestion` with concrete answer options when possible
4. Each new round should build on previous answers — reference what the user said and dig deeper
5. Aim for **at least 9 rounds** before moving on. Only stop earlier if the user explicitly says they want to move on.
6. **Adaptive follow-up**: After any round, if the user's answer is vague, ambiguous, or opens up new
   dimensions worth exploring, **insert additional follow-up rounds** before moving to the next planned topic.
   These follow-up rounds do NOT count toward the base 9-12 — they are extra depth.
   Set a hard cap of **20 follow-up rounds total** for Step 3.
   Continue probing while there are genuinely unclear or expandable areas, but stop follow-ups once:
   - all major ambiguities are resolved, OR
   - follow-up count reaches 20.
7. Before leaving Step 3, always ask one final open-ended confirmation question:
   - "在进入下一步前，你还有没有任何想追加、修正、或强调的需求？"
   Only proceed after the user confirms no further additions or provides the final additions.

   Triggers for follow-up rounds:
   - The user's answer is vague or hand-wavy (e.g., "something like that", "maybe", "not sure yet")
     → Dig deeper: ask for specifics, offer concrete options, or propose a default and ask if it fits
   - The user mentions a feature or concept in passing without elaborating
     → Expand: "You mentioned X — can you tell me more about how that should work?"
   - The answer reveals complexity that wasn't anticipated (e.g., multiple sub-roles, conditional logic,
     branching workflows)
     → Drill in: break the complexity into sub-questions and explore each
   - The AI identifies a potential design conflict or gap between what the user described in different rounds
     → Reconcile: "Earlier you said A, but just now you mentioned B — how should these work together?"
   - The user describes something that could be implemented multiple ways
     → Clarify approach: present 2-3 concrete options with trade-offs and ask which fits their vision

   Follow-up round format:
   - Label as "Round N.1", "Round N.2" etc. (e.g., "Round 3.1 — Clarifying admin permissions")
   - Keep each follow-up focused on ONE specific clarification
   - After the follow-up is resolved, return to the next planned round

Important rules:
- The user journeys (Rounds 1-5) come FIRST — you need to understand how users flow through the product
  before you can meaningfully discuss components
- Components (Rounds 6-10) are derived from the journeys — when asking about components, reference the
  specific journey step where they appear (e.g., "In the onboarding flow you described, the sign-up form needs...")
- Only ask questions that are **relevant to what the user described** — skip rounds that don't apply
- Each round should feel like a natural follow-up conversation, not a generic checklist
- When the user's answers reveal new dimensions, follow up on those — it's OK to deviate from the planned rounds
- After each round, briefly summarize what you learned before asking the next question
- **Do NOT rush through rounds just to hit the count** — depth matters more than speed. If Round 3 needs
  three follow-ups to fully clarify, that's better than a shallow Round 3 followed by a shallow Round 4
- The user can say "enough" or "let's move on" at any time to skip remaining rounds

Example flow:
```
User described: "I want to build a team task management tool"

Round 1 — User roles:
  "Who are the different types of users in this tool?"
  - Just one role — everyone is equal
  - Admin + regular members
  - Admin + members + guest/viewer (read-only)
  → User: "Admin + regular members"

Round 2 — Primary journey (member):
  "Let's trace a regular member's journey. They open the app — then what?
   Walk me through: How do they find their tasks? How do they update progress?
   What does 'done' look like for them?"
  → User: "See dashboard → pick a task from my list → update status → mark done → see it in completed"

Round 3 — Secondary journey (admin):
  "Now for the admin — besides doing regular member tasks, what extra things can they do?
   Create projects? Invite people? Set permissions? View reports?"
  → User: "Create projects, invite members, see overview dashboard of all tasks across team"

Round 4 — Edge cases:
  "What happens when: a member opens the app and has zero tasks? A task is overdue?
   Someone tries to access a project they're not part of?"
  → User: "Empty state with suggestion to browse open tasks. Overdue tasks get highlighted. 404 for unauthorized."

Round 5 — Journey validation:
  "Let me recap the journeys so far:
   - Member: sign up → dashboard → pick task → update status → done
   - Admin: all member actions + create projects, invite members, overview dashboard
   Are there any flows I'm missing? What about onboarding, password reset, or notification preferences?"
  → User: "Add an onboarding flow — first-time members get a guided tour of the dashboard"

Round 6 — Page inventory:
  "Based on what you described, I see these pages:
   1. Login / Sign-up
   2. Onboarding tour (first-time members)
   3. Dashboard (member view — my tasks)
   4. Dashboard (admin view — team overview)
   5. Project page (task list within a project)
   6. Task detail page
   7. Settings / team management (admin)
   Am I missing any?"
  → User: "Add a notification center page"

Round 7 — Component deep-dive:
  "Let's look at the Dashboard. You said members see 'my tasks' — what's on this page?
   - A list or kanban board?
   - Filters (by project, status, priority)?
   - Quick actions (mark done, change status) without opening the task?
   - Any summary stats (tasks due today, overdue count)?"
  → User: "Kanban board with columns per status. Filters by project and priority. Quick drag to change status. Stats bar at top."

Round 8 — Data flow:
  "When a member drags a task to 'Done' on the kanban board:
   - Does it update instantly (optimistic) or wait for server confirmation?
   - Should other team members see the change in real-time?
   - Does it trigger a notification to the admin?"
  → User: "Optimistic update, real-time sync for others, notify admin only if it's a milestone task"

Round 9 — State management:
  "How should the app handle offline scenarios or slow connections?
   And for the kanban board state — should column order and filters persist across sessions?"
  → User: "No offline support needed for MVP. Yes, persist filters and column preferences per user."

Round 10 — Integrations & constraints:
  "Any external tools to connect with? And is this a hosted SaaS or self-hosted?"
  → User: "Slack notifications for task assignments. Hosted SaaS. MVP first, no enterprise needs."
```

When the user indicates they've provided enough info (e.g., "enough", "let's move on", "就这些", "可以了"),
run one final additions check ("还有没有要补充/修正的内容？"), then proceed to the next step.

#### Step 4 — Tech Stack Finalization

Finalize the technology choices based on the baseline confirmed in Round 10.5.
If Round 10.5 already locked a stack, use this step to confirm final details (versions, key libraries, infra choices).
If not locked yet, complete stack selection here before Step 5.
Offer common stacks as options but always allow custom input.
Consider the user's existing preferences from CLAUDE.md if available (e.g., if they prefer Bun over npm).

Example question: "What tech stack do you want to use?"
Suggested options based on common patterns:
- TypeScript + React + Vite + Tailwind
- TypeScript + Next.js + Tailwind
- TypeScript + Node.js backend
- Custom (let user type)

#### Step 5 — Synthesis & Confirmation

After gathering enough context from Steps 2-4, **synthesize everything into a complete project summary**.
Present to the user:

1. **Project overview** — 2-3 sentence summary in your own words based on what you learned
2. **Core features** — A structured feature list (3-8 features) broken down from the conversation:
   - Feature name (short label)
   - What it does (1-3 sentences)
   - Key constraints or requirements you inferred
3. **Tech stack** — Confirmed stack from Step 4
4. **UI approach** — UI framework, CSS approach, key components, icon set (GUI projects only)
   **CLI interface** — Command structure, output modes, config strategy, key conventions (CLI projects only)
5. **Deployment** — Hosting platform, database hosting, CI/CD approach
6. **Scope notes** — Anything explicitly out of scope or deferred

Ask the user to confirm, or revise anything before doc generation.

Use `AskUserQuestion` with options like:
- "Looks good, generate the docs"
- "I want to adjust some things"

If the user wants changes, iterate until they're satisfied.

### Phase 2: Generate Documentation

After confirmation, create the `docs/` directory and generate all documents (4 documents total).

#### File: `docs/architecture.md`

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

#### File: `docs/plans.md`

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

#### File: `docs/implement.md`

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

#### File: `docs/documentation.md`

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

#### Files: `CLAUDE.md` + `AGENT.md` (both at project root)

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

### Phase 2.5: Multi-Agent Documentation Review

After generating all documents, launch a **multi-agent review team** to validate the documentation
quality, consistency, and completeness before handing off to the user. Use the `Agent` tool to spawn
reviewers in parallel — each agent reviews from a different perspective.

Determine project complexity first, then spawn reviewers in parallel using the tiers below:

- **Lite tier** (simple/small scope): spawn Agent 1 + Agent 2 + Agent 3.
- **Standard tier** (most projects): spawn Agent 1 + Agent 2 + Agent 3.
- **Complex tier** (multi-role, multi-platform, integration-heavy): spawn Agent 1 + Agent 2 + Agent 3, then run a quick second-pass recheck with Agent 2 + Agent 3 after fixes.

Use the agent definitions below as the review pool.

#### Agent 1 — Architecture & Spec Reviewer
- Read `docs/architecture.md` end-to-end
- Check:
  - [ ] Every user role from the interview is documented with permissions
  - [ ] Every user journey is complete (entry → core action → goal), no missing steps
  - [ ] Every page/screen has purpose, components, user actions, and responsive behavior
  - [ ] Every core feature has a detailed spec section with edge cases
  - [ ] Technical architecture (tech stack, data model, API design, integrations) is consistent with interview answers
  - [ ] Directory structure is realistic and matches the chosen framework conventions
  - [ ] Hard requirements section captures all constraints mentioned
  - [ ] Deliverable section lists all output docs
- Report: list any gaps, contradictions, or vague sections that need improvement

#### Agent 2 — Plans & Milestones Reviewer
- Read `docs/plans.md` end-to-end
- Cross-reference with `docs/architecture.md` features
- Check:
  - [ ] Project metadata (platform, tech stack, UI framework, deployment) is accurate
  - [ ] Every feature in architecture.md maps to at least one milestone
  - [ ] Milestones are ordered logically (scaffold → core features → integrations → polish)
  - [ ] Each milestone has: scope, sub-tasks, key files/modules, acceptance criteria, verification commands
  - [ ] Each milestone has 3-8 numbered sub-tasks, each describing ONE atomic action
  - [ ] Sub-tasks follow a logical implementation order within each milestone
  - [ ] Acceptance criteria are concrete and testable (not vague like "works correctly")
  - [ ] Verification commands are real and runnable for the chosen tech stack
  - [ ] CLI Foundation milestone (CC) is Milestone 02, right after repo scaffold (CLI projects only)
  - [ ] No feature is left uncovered by milestones
  - [ ] Risk register has realistic entries
- Report: list any missing features, vague criteria, or ordering issues

#### Agent 3 — Execution Rules & Cross-doc Consistency Reviewer
- Read ALL docs: `docs/implement.md`, `docs/documentation.md`, `CLAUDE.md`, `AGENT.md`
- Cross-reference with `docs/plans.md` and `docs/architecture.md`
- Check:
  - [ ] implement.md completion criteria match the actual doc set generated
  - [ ] implement.md verification commands match the tech stack
  - [ ] implement.md git strategy (work on main) is present
  - [ ] documentation.md milestone list matches plans.md milestones
  - [ ] documentation.md setup commands match the tech stack
  - [ ] CLAUDE.md and AGENT.md are identical
  - [ ] CLAUDE.md Execution Protocol lists all docs in correct order
  - [ ] CLAUDE.md Key Docs section matches actual generated files
  - [ ] CLAUDE.md commands are accurate for the chosen package manager and framework
  - [ ] If CLI: implement.md has CLI-specific rules (exit codes, help, stdout/stderr, NO_COLOR)
  - [ ] If CLI: implement.md completion criteria include CLI standards checklist
- Report: list any cross-doc contradictions, missing references, or broken commands

**After all agents complete**, collect their reports and:
1. **Fix all issues** found by the reviewers — edit the docs directly
2. If fixes are significant (e.g., missing features, restructured milestones), briefly inform the user what was corrected
3. If no issues found, proceed silently

This review ensures the documentation is production-quality before the user starts implementation.

### Phase 3: Next Steps

After the review is complete and all issues are fixed, tell the user:

1. The docs are ready at `docs/`
2. Suggest they review:
   - `docs/architecture.md` — project background, user journeys, components, technical architecture
   - `docs/plans.md` — milestones and execution plan
3. Explain they can now start execution by feeding `docs/implement.md` as instructions
4. Mention they can adjust milestone count/scope in `docs/plans.md` before starting

## Language

Follow the user's language preference. If they write in Chinese, generate documents in Chinese.
If they write in English, generate in English. Technical terms (file names, commands, code) stay in English regardless.
