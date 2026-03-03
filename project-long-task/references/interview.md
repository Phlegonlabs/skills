# Phase 1: Interactive Interview

Collect project information through conversation. Use `AskUserQuestion` for each step.

## Step 1 — Project Name

Ask the user for the project name. This becomes the directory context and document titles.

Example question: "What's the project name?"

## Step 2 — Project Goals (Free-form)

This is the most important step. Before diving into tech stack or feature lists, ask the user to describe
their project goals in their own words — what problem they're solving, who it's for, what the end result
should look like. This can be as brief or detailed as they want. The point is to capture intent and context
before any structured breakdown.

Example question: "Tell me about your project — what are you building, what problem does it solve, and who is it for? Just describe it in your own words, no need to be structured."

Let the user write freely. Do NOT interrupt with follow-up questions mid-description.

## Step 3 — Clarifying Questions (AI-driven discovery)

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

### Example Flow

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

## Step 4 — Tech Stack Finalization

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

## Step 5 — Synthesis & Confirmation

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
