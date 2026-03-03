# Phase 1: Interactive Interview

Collect project information through conversation. If your environment supports interactive question prompts (with selectable options), use them — otherwise ask in plain text.

## Complexity Tiers

After collecting Project Goals (Step 2), assess complexity and assign a tier. The tier controls which
interview rounds to run, how many follow-ups are allowed, and how deep to probe.

**Default tier is Standard.** Only downgrade to Lite if the user explicitly requests a simplified interview
or the project is clearly trivial (e.g., a single-file script, a config wrapper). When in doubt, stay at Standard.

| Tier | Criteria | Target Questions | Rounds to run | Follow-up Cap |
|------|----------|-----------------|--------------|---------------|
| **Lite** | Single-purpose tool, 1 user role, no auth, no integrations, simple UI/CLI — **only if user explicitly requests simplified interview** | ~10 | Rounds 1-3, 6-7, 10, 10.5, 10.7, deployment. May condense Rounds 4-5, 8-9, 10.3 but do NOT skip entirely | 5 |
| **Standard** | **Default for all projects.** Multiple roles or features, some integrations, moderate UI/data complexity | ~15 | All applicable rounds (full protocol; GUI ~10-11, CLI ~10-13 effective rounds) | 8 |
| **Complex** | Multi-role, multi-platform, integration-heavy, enterprise requirements | ~25-30 | All applicable rounds (full protocol) + extended depth on architecture, security, scale | 20 |

After Step 2, announce the assessed tier to the user and let them override. Default assumption is Standard.

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
2. Plan the discovery interview based on the **complexity tier** assigned after Step 2:
   - **Lite**: 7-9 base rounds — condense Rounds 4-5, 8-9, 10.3 into lighter versions but do NOT skip them
   - **Standard**: All applicable rounds — full protocol (this is the default; GUI ~10-11, CLI ~10-13 effective rounds)
   - **Complex**: All applicable rounds with extended depth on architecture, security, and scale
   The first section covers user journeys, the second drills into components and details, then a required
   tech stack finalization checkpoint, then UI preferences (GUI) or CLI interface design (CLI), and finally
   deployment. Cover these areas progressively (skip any already answered in Step 2):

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
   Also ask for a rough layout (wireframe/frame sketch): key regions (header/sidebar/main/footer) and the major components in each region.

   **Round 7 — Component deep-dive**: For each page identified, drill into the specific components:
   - What data does each component display?
   - What states does it have? (loading, empty, error, success, disabled)
   - What interactions does it support? (click, hover, drag, swipe)
   - How does it behave on mobile vs. desktop?
   Ensure the component inventory is exhaustive for design/implementation (include overlays like dialogs/drawers/popovers/toasts, not just the visible page body).

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

   **Round 10 — Third-party integrations & secrets**:
   - Third-party services or APIs to connect with?
   - Secrets/API keys: which integrations require keys? how will they be provided (env vars/secrets manager)?
     Does the product issue API keys to end users (show-once, revoke/rotate)?
   - **When the user confirms specific third-party API integrations** (e.g., Stripe, GitHub API, OpenAI,
     Twilio), use the **Context7 MCP tool** to fetch the latest API documentation for those services.
     Reference the fetched docs when recommending the tech stack, identifying required API keys/scopes,
     and flagging any known API constraints (rate limits, webhook requirements, auth flows).

   **Round 10.3 — Non-functional requirements**:
   - Scale expectation (personal tool vs. SaaS vs. enterprise)?
   - Performance requirements? (e.g., LCP < 2.5s, bundle < 200KB, supports slow 3G? Image optimization?) Offline support?
   - Security/privacy/compliance requirements? (PII, retention, audit logging, regulatory constraints)
   - Accessibility requirements (GUI projects): WCAG 2.1 AA compliance? Keyboard navigation? Screen reader support?
     (If the product has external users, recommend AA compliance as baseline)
   - SEO requirements (Web projects only): Public pages that need search indexing? SSR/SSG needed?
     Metadata strategy (OG tags, sitemap, robots.txt)?
   - Internationalization (i18n): Single language or multilingual? If multi-language, which locales?
     Any RTL support needed? (If yes, confirm i18n library as part of tech stack lock in Round 10.7)
   - Observability: Error tracking (Sentry/Datadog)? Structured logging strategy?
     Performance monitoring? Alerting on errors or latency spikes?
   - Analytics/tracking needs (Web projects only): GA4/GTM? key events? conversion goals? consent/banner? strict no-PII rule?

   **Round 10.5 — Testing & development workflow**:
   - Testing strategy: unit / integration / E2E? Which test runner (Vitest, Jest, Playwright, Cypress)?
     Coverage targets? Approach to mocking third-party services in tests?
   - Development workflow: trunk-based on `main` vs feature branches + PR? Any commit conventions?
   - Any hard business rules or constraints?

   **Round 10.7 — Tech Stack Finalization (required before UI/deployment)**:
   All stack decisions are finalized here. Do NOT proceed past this round until the tech stack is locked.
   - Confirm runtime/package manager/framework baseline before entering UI and deployment rounds
   - Minimum fields to lock: runtime, package manager, frontend/backend framework, styling approach (if GUI),
     data/storage approach, test runner, i18n library (if multilingual)
   - Offer common stacks as options but always allow custom input. Consider the user's existing preferences
     from CLAUDE.md if available (e.g., if they prefer Bun over npm, `type` over `interface`)
   - Suggested options based on common patterns:
     - TypeScript + React + Vite + Tailwind
     - TypeScript + Next.js + Tailwind
     - TypeScript + Node.js backend
     - Custom (let user type)
   - If still undecided, propose 2-3 concrete stack options and ask the user to pick one

   **--- UI Preferences (Round 11, GUI projects only) ---**

   **Round 11 — UI component & styling approach**: Based on the project type, target users, and
   complexity gathered so far, ask about the UI implementation approach:
   - **Visual references** — ask the user if they have any reference images (screenshots, mockups,
     Dribbble/Behance links, photos of sketches, etc.) that represent the look & feel they want.
     If provided, analyze the images to extract: color palette, layout patterns, typography style,
     component density, and overall aesthetic (e.g., minimal, dense, playful, corporate).
     Use these observations to inform the recommendations below.
   - **UI library / component framework** — recommend based on the tech stack (e.g., shadcn/ui, Radix,
     Ant Design, Material UI, fully custom) and explain why it fits the project
   - **CSS approach** — Tailwind, CSS Modules, styled-components, vanilla CSS, etc.
   - **Key UI components** — based on all pages discussed, identify the shared UI primitives needed
     (e.g., Button, Input, Card, Modal, Table, Avatar, Badge, Toast, etc.)
   - **Iconography** — suggest an icon set (e.g., Lucide, Phosphor, Heroicons)
   - **Accessibility** — Confirm a11y requirements gathered in Round 10.3. If WCAG AA was selected,
     note which UI library features support it (e.g., Radix primitives are accessible by default)
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

3. Each round: ask **1-2 focused questions**, offering concrete answer options when possible (use your tool's option UI if available; otherwise plain text)
4. Each new round should build on previous answers — reference what the user said and dig deeper
5. Aim for **at least the minimum rounds for the assigned tier** before moving on. Only stop earlier if the user explicitly says they want to move on.
   - Lite: at least 7 rounds
   - Standard: at least 9 rounds
   - Complex: at least 11 rounds
6. **Adaptive follow-up**: After any round, if the user's answer is vague, ambiguous, or opens up new
   dimensions worth exploring, **insert additional follow-up rounds** before moving to the next planned topic.
   These follow-up rounds do NOT count toward the base rounds — they are extra depth.
   Hard cap on follow-ups is determined by the complexity tier (Lite: 5, Standard: 8, Complex: 20).
   **Err on the side of asking more, not less.** A thorough interview saves hours of rework later.
   Target total questions (base rounds + follow-ups): Lite ~10, Standard ~15, Complex ~25-30.
   Continue probing while there are genuinely unclear or expandable areas, but stop follow-ups once:
   - all major ambiguities are resolved, OR
   - follow-up count reaches the tier cap.
7. Before leaving Step 3, always ask one final open-ended confirmation question (in the user's language):
   - e.g., "Before moving on, is there anything you'd like to add, change, or emphasize?"
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
   - The user mentions a specific third-party service (payment gateway, auth provider, messaging, etc.)
     without specifying integration depth
     → Ask immediately: "You mentioned [service] — is this a core dependency or a nice-to-have?
       What specific operations do you need from it? Do you already have API credentials?"
       Then use Context7 MCP tool to fetch that service's latest API docs for reference.

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
run one final additions check (in the user's language, e.g., "Anything else to add or change?"), then proceed to the next step.

## Step 3.5 — Tier Recheck

After completing all interview rounds, **reassess the complexity tier** based on what was actually discovered.
The initial tier was assessed after Step 2 (a rough description) — now you have full context.

- If the project turned out **more complex** than initially assessed (e.g., more roles, more integrations,
  multi-platform needs discovered during rounds), **upgrade the tier** and announce the change.
- If the project turned out **simpler**, optionally downgrade (but only if the user agrees).
- Tier changes affect: milestone count in docs/plans.md, review scope in Phase 2.5.

This step is silent if the tier hasn't changed — only announce when there's a change.

## Step 4 — Synthesis & Confirmation

After gathering enough context from Steps 2-3, **synthesize everything into a complete project summary**.
Present to the user:

1. **Project overview** — 2-3 sentence summary in your own words based on what you learned
2. **Core features** — A structured feature list (3-8 features) broken down from the conversation:
   - Feature name (short label)
   - What it does (1-3 sentences)
   - Key constraints or requirements you inferred
3. **Tech stack** — Confirmed stack from Round 10.5
4. **UI approach** — UI framework, CSS approach, key components, icon set (GUI projects only)
   **CLI interface** — Command structure, output modes, config strategy, key conventions (CLI projects only)
5. **Deployment** — Hosting platform, database hosting, CI/CD approach
6. **Quality & infrastructure** — Testing strategy, a11y requirements, i18n support, error tracking,
   SEO approach (summarize decisions from Rounds 10.3 and 10.5)
7. **Scope notes** — Anything explicitly out of scope or deferred
8. **Production standard** — Remind the user: "The generated plan includes a **Production Readiness Gate**
   as the final milestone. Every milestone is written to produce production-quality code from the start.
   The final deliverable will be deployment-ready — not a demo or prototype."

Ask the user to confirm, or revise anything before doc generation.

Offer a simple confirmation choice like:
- "Looks good, generate the docs"
- "I want to adjust some things"

If your environment supports selectable options/prompts, use them; otherwise ask the user to reply with one of the options above.

If the user wants changes, iterate until they're satisfied.

---

## Update Mode Interview

This protocol is used when modifying an existing project (Update mode).
It assumes all existing docs have been read in Update Phase 1.

All three update types share the same Step 1 (Description) and Step 3 (Synthesis), but have
different clarifying question rounds in Step 2.

### Step 1 — Description (Free-form)

Ask the user to describe the change in their own words. Same principle as Init Step 2: capture
intent before structured breakdown.

Example questions by type:
- New Feature: "Describe the feature you want to add — what does it do and why do you need it?"
- Bug Fix: "Describe the bug — what's the expected behavior vs. actual behavior? How is it reproduced?"
- Change: "Describe what you want to change — what's the current state and what should it become?"

Let the user write freely. Do NOT interrupt with follow-up questions mid-description.

### Step 2 — Clarifying Questions

Based on the description and existing project context, ask targeted questions.
This is NOT a full project interview — focus only on what's new or changing.

---

#### New Feature Rounds (F1-F8, use 3-8 depending on complexity)

**Round F1 — User journey impact**: Which existing user journeys are affected? Are there new journeys?
Walk through the feature from the user's perspective step by step.

**Round F2 — Pages & components**: Does this feature need new pages/screens? Which existing pages
are modified? What new components are needed? What existing components need changes?
If the feature has UI, ask for visual references (screenshots, mockups, sketches) as in Round 11.

**Round F3 — Data & API changes**: Does this feature require new data models, new API endpoints,
or changes to existing ones? How does it interact with the current data model?

**Round F4 — Edge cases & constraints**: Error states, permissions, validation rules, performance
concerns. What happens when things go wrong?

**Round F4.5 — Testing requirements**: Does this feature require new unit / integration / E2E tests?
Are existing tests affected? Any testing-specific constraints (mock APIs, test data setup)?

**Round F5 — Integrations** (if applicable): Does this feature require new third-party services,
new secrets/API keys, or changes to existing integrations?
If yes, use **Context7 MCP tool** to fetch the latest API docs for any newly introduced services
before proposing the implementation approach.

**Round F6-F8 — Additional depth** (for complex features): Drill into areas that need more clarity
based on the user's answers. Same adaptive follow-up rules as Init mode.

Follow-up cap: 8 for simple features, 15 for complex ones.

---

#### Bug Fix Rounds (B1-B3, use 1-3 depending on severity)

**Round B1 — Reproduction & root cause**: Clarify the exact reproduction steps if not already clear.
What's the suspected root cause? Which components/modules are involved? Reference the existing
architecture to pinpoint the affected area.

**Round B2 — Impact analysis**: What else might be affected by this fix? Are there related features
that depend on the current (broken) behavior? Does the fix change any documented behavior in
architecture.md?

**Round B3 — Fix approach** (for non-trivial bugs): If there are multiple ways to fix the issue,
present 2-3 options with trade-offs and ask the user to pick one. Consider: backward compatibility,
data migration needs, performance implications.

Follow-up cap: 5.

---

#### Change Rounds (C1-C5, use 2-5 depending on scope)

**Round C1 — Change scope**: What exactly is changing? Map the current state → desired state.
Which existing features, user journeys, or components are affected? Reference the existing
architecture to identify all touch points.

**Round C2 — Migration & compatibility**: Does this change require data migration? Is there a
transition period where old and new behavior coexist? How should existing users/data be handled?
Rollback strategy: if this change needs to be reverted after deploy, is that possible? Should it be
behind a feature flag during rollout?

**Round C3 — Cascading effects**: Based on the existing architecture, what other parts of the
system need to change as a result? API contracts, shared types, dependent components, tests?

**Round C4 — Removed or replaced functionality**: Is anything being removed? If so, how should
it be handled — hard removal, deprecation period, or replacement? Any data cleanup needed?

**Round C5 — Additional depth** (for complex changes): Drill into areas that need more clarity.

Follow-up cap: 8.

---

#### Shared rules for all update types:
- Reference existing architecture when asking questions (e.g., "The current data model has X — does this change affect it?")
- Skip rounds that don't apply
- Each round: 1-2 focused questions with concrete options when possible
- Before leaving Step 2, ask one final confirmation question (in the user's language)

### Step 3 — Synthesis & Confirmation

Synthesize the change into a summary. Present to the user:

**For New Feature:**
1. **Feature overview** — 1-2 sentence summary
2. **User journey changes** — New or modified journeys
3. **New/modified pages & components** — What's being added or changed
4. **Data model & API changes** — New entities, endpoints, or modifications
5. **New milestones** — Proposed milestones (continuing the numbering from existing plans.md)
6. **Scope notes** — What's explicitly not included

**For Bug Fix:**
1. **Bug summary** — What's broken and why
2. **Root cause** — The identified cause and affected components
3. **Fix approach** — How it will be fixed
4. **Impact** — What behavior changes (if any) and what docs need updating
5. **Fix milestone** — A single milestone with sub-tasks for the fix

**For Change:**
1. **Change summary** — What's changing and why
2. **Affected areas** — Which features, journeys, components are impacted
3. **Migration plan** — How to transition (if applicable)
4. **Updated/removed content** — What architecture sections change
5. **New milestones** — Proposed milestones for implementing the change

Ask the user to confirm or adjust before updating docs.
