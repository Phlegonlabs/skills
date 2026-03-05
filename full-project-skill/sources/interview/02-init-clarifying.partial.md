## Step 3 — Clarifying Questions (AI-driven discovery)

This step is critical. Based on what the user described in Step 2 and the validated Step 2.7/2.8 outputs,
**analyze their goals and identify gaps
or ambiguities**, then ask targeted clarifying questions to flesh out the project scope.

Do NOT skip this step. Do NOT jump straight to feature lists or tech stack. The goal is to deeply understand
the project before generating anything.

The two primary goals of this step are:
1. **Map out every user journey** — understand all the different paths users take through the product
2. **Identify every component** — understand what UI/functional building blocks are needed and how they behave

Process:
1. Read the Step 2 goals, Step 2.5 market findings, Step 2.7 intro/flow draft, and Step 2.8 design direction carefully
2. Plan the discovery interview based on the **complexity tier** assigned after Step 2:
   - **Standard**: All applicable rounds — full protocol (this is the default; GUI ~10-11, CLI ~10-13 effective rounds)
   - **Complex**: All applicable rounds with extended depth on architecture, security, and scale
   The first section covers user journeys, the second drills into components and details, then a required
   tech stack finalization checkpoint, then UI preferences (GUI) or CLI interface design (CLI), and finally
   deployment. Cover these areas progressively (skip any already answered in Step 2):

   **--- User Journeys (Rounds R1-R5) ---**

   **Round R1 — User roles & personas**: Who are the different types of users? (e.g., admin, regular user, guest,
   viewer). What are their goals and context? Ask the user to list every distinct role.

   **Round R2 — Primary user journey**: For the most important user role, walk through their complete journey
   step by step. From first landing / sign-up, through the core action, to the end goal. Ask: "Walk me through
   what [primary user] does from the moment they open the app to completing their main goal."

   **Round R3 — Secondary user journeys**: For each additional role identified in Round R1, ask about their
   distinct journey. How does their experience differ? What can they do that others can't? Focus on the
   differences from the primary journey.

   **Round R4 — Journey edge cases & transitions**: What happens when things go wrong? Error states, empty
   states, loading states. How do users transition between journeys? (e.g., a viewer gets upgraded to editor).
   What about first-time vs. returning user experience?

   **Round R5 — Journey validation & gaps**: Revisit the complete set of journeys mapped so far. Are there
   any missing flows? (e.g., onboarding, password reset, settings changes, data export). Ask the user to
   confirm the journey map is complete or identify gaps.

   **--- Components & Details (Rounds R6-R10) ---**

   **Round R6 — Page/screen inventory**: Based on the journeys above, list out every page or screen the app
   needs. Ask the user to confirm and add any missing ones. For each page, ask: "What are the key elements
   on this page? What actions can the user take here?"
   Also ask for a rough layout (wireframe/frame sketch): key regions (header/sidebar/main/footer) and the major components in each region.

   **Round R7 — Component deep-dive**: For each page identified, drill into the specific components:
   - What data does each component display?
   - What states does it have? (loading, empty, error, success, disabled)
   - What interactions does it support? (click, hover, drag, swipe)
   - How does it behave on mobile vs. desktop?
   Ensure the component inventory is exhaustive for design/implementation (include overlays like dialogs/drawers/popovers/toasts, not just the visible page body).

   **Round R8 — Data flow & relationships**: How do components connect to each other?
   - What happens when you click a button — what changes on screen?
   - Which components share data?
   - What needs real-time updates vs. static content?
   - Any complex forms or multi-step workflows?

   **Round R9 — State management & persistence**: How is application state managed?
   - What data needs to persist across sessions?
   - What's stored locally vs. server-side?
   - Caching strategy? Optimistic updates?
   - How is authentication state handled?

   **Round R10 — Third-party integrations & secrets**:
   - Third-party services or APIs to connect with?
   - Secrets/API keys: which integrations require keys? how will they be provided (env vars/secrets manager)?
     Does the product issue API keys to end users (show-once, revoke/rotate)?
   - **When the user confirms specific third-party API integrations** (e.g., Stripe, GitHub API, OpenAI,
     Twilio), use the **Context7 MCP tool** to fetch the latest API documentation for those services.
     Reference the fetched docs when recommending the tech stack, identifying required API keys/scopes,
     and flagging any known API constraints (rate limits, webhook requirements, auth flows).
   - If Context7 is unavailable: use WebSearch + WebFetch to retrieve official API docs directly.
     If official docs still cannot be fetched, ask the user to provide the API documentation links.
     If links are still unavailable, proceed with best-effort recommendations, explicitly mark assumptions/caveats,
     and require documentation validation before implementation starts.

   **Round R10.3 — Non-functional requirements**:
   - Scale expectation (personal tool vs. SaaS vs. enterprise)?
   - Performance requirements? (e.g., LCP < 2.5s, bundle < 200KB, supports slow 3G? Image optimization?) Offline support?
   - Security/privacy/compliance requirements? (PII, retention, audit logging, regulatory constraints)
   - Accessibility requirements (GUI projects): WCAG 2.1 AA compliance? Keyboard navigation? Screen reader support?
     (If the product has external users, recommend AA compliance as baseline)
   - SEO requirements (Web projects only): Public pages that need search indexing? SSR/SSG needed?
     Metadata strategy (OG tags, sitemap, robots.txt)?
   - Internationalization (i18n): Single language or multilingual? If multi-language, which locales?
     Any RTL support needed? (If yes, confirm i18n library as part of tech stack lock in Round R10.7)
   - Observability: Error tracking (Sentry/Datadog)? Structured logging strategy?
     Performance monitoring? Alerting on errors or latency spikes?
   - Analytics/tracking needs (Web projects only): GA4/GTM? key events? conversion goals? consent/banner? strict no-PII rule?

   **Round R10.5 — Testing & development workflow**:
   - Testing strategy: unit / integration / E2E? Which test runner (Vitest, Jest, Playwright, Cypress)?
     Coverage targets? Approach to mocking third-party services in tests?
   - Development workflow: trunk-based on `main` vs feature branches + PR? Any commit conventions?
   - Any hard business rules or constraints?

   **Round R10.7 — Tech Stack Finalization (required before UI/deployment)**:
   All stack decisions are finalized here. Do NOT proceed past this round until the tech stack is locked.
   - **User preference detection**: Before presenting stack options, read the user's global `CLAUDE.md`
     (and any project-level config) to detect existing preferences — e.g., preferred package manager (`bun`,
     `pnpm`), styling approach (`Tailwind`), testing framework (`bun test`, `vitest`), coding conventions
     (`type` over `interface`, string unions over enums). Present detected preferences as default selections
     and let the user confirm or override them.
   - Confirm runtime/package manager/framework baseline before entering UI and deployment rounds
   - Minimum fields to lock: runtime, package manager, frontend/backend framework, styling approach (if GUI),
     data/storage approach, test runner, i18n library (if multilingual)
   - Offer common stacks as options but always allow custom input. Consider the user's existing preferences
     from CLAUDE.md if available (e.g., if they prefer Bun over npm, `type` over `interface`)
   - Present options by category using `references/tech-components.md` (framework, routing, state, ui,
     styling, backend, data, auth, deployment, testing, tooling, etc.)
   - When providing concrete version suggestions, reference `assets/versions.json`
   - Suggested options based on common patterns:
     - TypeScript + React + Vite + Tailwind
     - TypeScript + Next.js + Tailwind
     - TypeScript + Node.js backend
     - Custom (let user type)
   - If still undecided, propose 2-3 complete stack bundles and ask the user to pick one

   **--- UI Preferences (Round R11, GUI projects only) ---**

   **Round R11 — UI component & styling approach**: Based on the project type, target users, and
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
   - **Accessibility** — Confirm a11y requirements gathered in Round R10.3. If WCAG AA was selected,
     note which UI library features support it (e.g., Radix primitives are accessible by default)
   - **Component hierarchy strategy** — will the project use a 3-tier approach
     (Tier 1: UI library primitives → Tier 2: custom composites → Tier 3: page components)?
     This was proposed in Step 2.8 — confirm the chosen organization model and discuss any adjustments.
   - **Interactive pattern conventions** — define standard conventions for interactive states:
     - Hover: what visual feedback on hover? (e.g., subtle background change, never text color change)
     - Focus: focus ring style? (e.g., 2px ring with offset)
     - Disabled: visual treatment? (e.g., 50% opacity + pointer-events-none)
     - If applicable: inline editing pattern, popover/selector behavior
   - **File conventions** — confirm where UI files live:
     - Tier 1 primitives directory (e.g., `components/ui/`)
     - Tier 2 custom components directory (e.g., `components/`)
     - Pages/routes directory (e.g., `app/` or `pages/`)
     - Hooks, utilities, contexts directories
     - Naming convention: PascalCase for components, camelCase for hooks/utils
     - Import alias convention (e.g., `@/components/...`)
   - **Living design guide page** — for GUI projects, recommend including a `/design-guide` route
     (or equivalent) as a development-only showcase page. This page displays all custom components
     with their variants, states, and usage examples. Confirm if the user wants this included.
   - Ask the user to confirm or adjust

   **--- CLI Interface Design (Rounds 11C-13C, CLI projects only) ---**

   For CLI / terminal tools, ask these CLI-specific rounds:

   **Round 11C — Command structure & interface design**: Propose a CLI architecture based on the features
   gathered in Rounds R1-R10:
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


   **--- Mobile Experience (Rounds R11M-R13M, mobile projects only) ---**

   For mobile app projects, ask these mobile-specific rounds:

   **Round R11M — Navigation & gesture design**:
   - Navigation pattern: bottom tab bar, drawer, nested stack, or hybrid?
   - Primary gesture interactions: swipe, pull-to-refresh, long press, drag-and-drop?
   - Back navigation behavior and deep-link entry flow?

   **Round R12M — Platform-specific behavior**:
   - iOS vs Android behavior differences that must be explicit?
   - Safe area handling strategy, permission prompts, push-notification flow?
   - Any platform-specific UI conventions that must be preserved?

   **Round R13M — Offline & performance**:
   - Offline-first vs online-only behavior for core flows?
   - Startup performance constraints and bundle-size constraints?
   - Image/media caching policy and retry/sync behavior after reconnect?

   **--- Deployment (Round R14) ---**

   **Round R14 — Deployment platform & infrastructure**: Ask the user where and how the project will
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
   `docs/plans.md` (deployment milestone), and `CLAUDE.md` / `AGENTS.md` (build/deploy commands).

3. Each round: ask **1-2 focused questions**, offering concrete answer options when possible (use your tool's option UI if available; otherwise plain text)
4. Each new round should build on previous answers — reference what the user said and dig deeper
5. Aim for **at least the minimum rounds for the assigned tier** before moving on. Only stop earlier if the user explicitly says they want to move on.
   - Standard: at least 9 rounds
   - Complex: at least 11 rounds
6. **Adaptive follow-up**: After any round, if the user's answer is vague, ambiguous, or opens up new
   dimensions worth exploring, **insert additional follow-up rounds** before moving to the next planned topic.
   These follow-up rounds do NOT count toward the base rounds — they are extra depth.
   Hard cap on follow-ups is determined by the complexity tier (Standard: 8, Complex: 20).
   **Err on the side of asking more, not less.** A thorough interview saves hours of rework later.
   Target total questions (base rounds + follow-ups): Standard ~15, Complex ~25-30.
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
       If Context7 is unavailable, fall back to WebSearch + WebFetch for official docs, then ask the user
       for the doc links. If links are still unavailable, proceed with best-effort assumptions and caveats,
       and flag API-doc validation as required before implementation.

   Follow-up round format:
   - Label as "Round RN.1", "Round RN.2" etc. (e.g., "Round R3.1 — Clarifying admin permissions")
   - Keep each follow-up focused on ONE specific clarification
   - After the follow-up is resolved, return to the next planned round

Important rules:
- The user journeys (Rounds R1-R5) come FIRST — you need to understand how users flow through the product
  before you can meaningfully discuss components
- Components (Rounds R6-R10) are derived from the journeys — when asking about components, reference the
  specific journey step where they appear (e.g., "In the onboarding flow you described, the sign-up form needs...")
- Only ask questions that are **relevant to what the user described** — skip rounds that don't apply
- Each round should feel like a natural follow-up conversation, not a generic checklist
- When the user's answers reveal new dimensions, follow up on those — it's OK to deviate from the planned rounds
- After each round, briefly summarize what you learned before asking the next question
- **Do NOT rush through rounds just to hit the count** — depth matters more than speed. If Round R3 needs
  three follow-ups to fully clarify, that's better than a shallow Round R3 followed by a shallow Round R4
- The user can say "enough" or "let's move on" at any time to skip remaining rounds

### Example Flow

```
User described: "I want to build a team task management tool"

Round R1 — User roles:
  "Who are the different types of users in this tool?"
  - Just one role — everyone is equal
  - Admin + regular members
  - Admin + members + guest/viewer (read-only)
  → User: "Admin + regular members"

Round R2 — Primary journey (member):
  "Let's trace a regular member's journey. They open the app — then what?
   Walk me through: How do they find their tasks? How do they update progress?
   What does 'done' look like for them?"
  → User: "See dashboard → pick a task from my list → update status → mark done → see it in completed"

Round R3 — Secondary journey (admin):
  "Now for the admin — besides doing regular member tasks, what extra things can they do?
   Create projects? Invite people? Set permissions? View reports?"
  → User: "Create projects, invite members, see overview dashboard of all tasks across team"

Round R4 — Edge cases:
  "What happens when: a member opens the app and has zero tasks? A task is overdue?
   Someone tries to access a project they're not part of?"
  → User: "Empty state with suggestion to browse open tasks. Overdue tasks get highlighted. 404 for unauthorized."

Round R5 — Journey validation:
  "Let me recap the journeys so far:
   - Member: sign up → dashboard → pick task → update status → done
   - Admin: all member actions + create projects, invite members, overview dashboard
   Are there any flows I'm missing? What about onboarding, password reset, or notification preferences?"
  → User: "Add an onboarding flow — first-time members get a guided tour of the dashboard"

Round R6 — Page inventory:
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

Round R7 — Component deep-dive:
  "Let's look at the Dashboard. You said members see 'my tasks' — what's on this page?
   - A list or kanban board?
   - Filters (by project, status, priority)?
   - Quick actions (mark done, change status) without opening the task?
   - Any summary stats (tasks due today, overdue count)?"
  → User: "Kanban board with columns per status. Filters by project and priority. Quick drag to change status. Stats bar at top."

Round R8 — Data flow:
  "When a member drags a task to 'Done' on the kanban board:
   - Does it update instantly (optimistic) or wait for server confirmation?
   - Should other team members see the change in real-time?
   - Does it trigger a notification to the admin?"
  → User: "Optimistic update, real-time sync for others, notify admin only if it's a milestone task"

Round R9 — State management:
  "How should the app handle offline scenarios or slow connections?
   And for the kanban board state — should column order and filters persist across sessions?"
  → User: "No offline support needed for MVP. Yes, persist filters and column preferences per user."

Round R10 — Integrations & constraints:
  "Any external tools to connect with? And is this a hosted SaaS or self-hosted?"
  → User: "Slack notifications for task assignments. Hosted SaaS. MVP first, no enterprise needs."
```

When the user indicates they've provided enough info (e.g., "enough", "let's move on", "就这些", "可以了"),
run one final additions check (in the user's language, e.g., "Anything else to add or change?"), then proceed to the next step.
