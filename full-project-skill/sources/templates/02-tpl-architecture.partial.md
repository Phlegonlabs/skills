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
