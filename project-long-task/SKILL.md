---
name: project-long-task
description: >
  Initialize a long-running project with a structured docs workflow, or update an existing project (new features,
  bug fixes, refactors, requirement changes). Use this skill whenever the user wants to start a new project,
  kick off a long-running build task, set up project documentation structure, or says things like "new project",
  "start a project", "init project", "project setup", or "I want to build something from scratch". Also use
  when the user mentions wanting a milestone-based plan, structured execution workflow, or asks to scaffold
  documentation for a complex multi-step build. Additionally, use this skill when the user wants to modify an
  existing project that already has a `docs/` directory — e.g., "add a new feature", "fix this bug",
  "refactor X", "I want to change how Y works", "new feature request".
---

# Project Long Task

A structured workflow for long-running, milestone-based builds. This skill supports two modes:

- **Init mode** — New project: collects requirements through an interactive interview, then generates a complete
  documentation scaffold that guides autonomous execution from planning through implementation.
- **Update mode** — Existing project: collects requirements for a change through a focused interview, then
  updates the existing documentation to incorporate the change. Supports three update types:
  - **New Feature** — Adding new functionality (3-8 interview rounds)
  - **Bug Fix** — Fixing issues that may change behavior or architecture (1-3 interview rounds)
  - **Change** — Requirement changes, refactors, tech migrations (2-5 interview rounds)

## Why this structure works

Long-running tasks fail when context drifts or the executor loses track of what's done and what's next. This
workflow prevents that by separating concerns into distinct documents that each serve a clear purpose:

- A **spec** that never changes (what to build)
- A **plan** that tracks progress (what's done, what's next)
- **Execution rules** that enforce discipline (how to work)
- **Living docs** that stay accurate (architecture + user docs)

The interview phase is critical — it forces clarity before any code is written, which saves hours of rework later.

## Mode Detection

At the start, detect which mode to use:

1. Check if `docs/architecture.md` and `docs/plans.md` already exist in the project
2. If **both exist** → **Update mode** (the project was previously initialized with this skill)
3. If **neither exists** → **Init mode** (new project)
4. If ambiguous, ask the user whether they are modifying the existing project or starting fresh

## Complexity Tiers

After Step 2 (Project Goals), assess complexity and assign a tier. This determines interview depth,
milestone count, and review scope throughout the entire workflow.

| Tier | When | Interview Rounds | Follow-up Cap | Milestones | Review |
|------|------|-----------------|---------------|------------|--------|
| **Lite** | Single-purpose tool, 1 role, no auth, no integrations | 5-7 base rounds (skip Rounds 4-5, 8-9) | 8 | 4-6 | Agent 1 + Agent 2 |
| **Standard** | Most projects — multiple roles or features, some integrations | 9-12 base rounds (full) | 20 | 7-10 | Agent 1 + Agent 2 + Agent 3 |
| **Complex** | Multi-role, multi-platform, integration-heavy, enterprise | 9-12 base rounds (full) + extended depth | 20 | 10-14 | Agent 1 + Agent 2 + Agent 3, then second-pass recheck |

Announce the tier to the user after Step 2 and let them override it (e.g., "I know it looks simple but I want thorough coverage").

## Workflow

### Phase 1: Interactive Interview

Collect project information through an interactive conversation. See `references/interview.md` for the full
interview protocol including all rounds, follow-up triggers, and examples.

**Steps overview:**
1. **Project Name** — Ask the user for the project name
2. **Project Goals** — Free-form description of what they're building, the problem, and target users
3. **Clarifying Questions** — AI-driven discovery interview (rounds and depth determined by complexity tier,
   covering user journeys, components, tech stack finalization, UI/CLI preferences, and deployment).
   Adaptive follow-ups for ambiguities. Tech stack is locked during this step (Round 10.5).
4. **Synthesis & Confirmation** — Present a complete project summary for user approval before generating docs

### Phase 2: Generate Documentation

After confirmation, create the `docs/` directory and generate all documents. See `references/templates.md`
for the full templates and structure of each file.

**Documents generated:**
- `docs/architecture.md` — Single source of truth: project background, user journeys, components, product spec, technical architecture
- `docs/plans.md` — Execution plan with milestones, sub-tasks, acceptance criteria, verification commands
- `docs/implement.md` — Non-negotiable execution rules for disciplined autonomous work
- `docs/secrets.md` — Secrets & API keys guidance (env vars + safe key handling)
- `docs/documentation.md` — User-facing documentation, kept in sync with reality
- `CLAUDE.md` + `AGENT.md` — Quick-reference files for AI coding tools (identical content, under 80 lines)

### Phase 2.5: Multi-Agent Documentation Review

Launch a multi-agent review team to validate documentation quality, consistency, and completeness.
See `references/review.md` for the full review protocol and agent definitions.
If multi-agent spawning isn't available in your environment, run the same checklists sequentially as a self-review.

**Review agents:**
- **Agent 1** — Architecture & Spec Reviewer (validates architecture.md completeness)
- **Agent 2** — Plans & Milestones Reviewer (validates plans.md coverage and ordering)
- **Agent 3** — Execution Rules & Cross-doc Consistency Reviewer (validates all docs are consistent)

Fix all issues found, then proceed.

### Phase 3: Next Steps

After review, tell the user:
1. The docs are ready at `docs/`
2. Suggest they review `docs/architecture.md` and `docs/plans.md`
3. Explain they can start execution by feeding `docs/implement.md` as instructions
4. Mention they can adjust milestone count/scope in `docs/plans.md` before starting

---

## Update Mode (modifying an existing project)

When mode detection determines **Update mode**, follow this lighter workflow instead of the full Init flow.
See `references/interview.md` § "Update Mode Interview" for the full protocol.

### Update Phase 1: Context Loading

1. Read all existing docs: `docs/architecture.md`, `docs/plans.md`, `docs/implement.md`, `docs/secrets.md`, `docs/documentation.md`
2. Identify: current milestone progress, existing features, tech stack, established patterns
3. Briefly summarize the project's current state to the user to confirm alignment

### Update Phase 1.5: Update Type Classification

Ask the user what kind of change they're making, or infer from their description:

| Type | When | Interview Rounds | Follow-up Cap |
|------|------|-----------------|---------------|
| **New Feature** | Adding new functionality to the project | 3-8 rounds (F1-F8) | 5-10 |
| **Bug Fix** | Fixing a bug that may change behavior, architecture, or require doc updates | 1-3 rounds (B1-B3) | 3 |
| **Change** | Requirement changes, refactors, tech migrations, removing features | 2-5 rounds (C1-C5) | 5 |

Announce the classified type to the user and let them override.

### Update Phase 2: Update Interview

A focused interview scoped to the change (NOT a full project interview). See `references/interview.md` for
the full protocol for each update type.

**Steps overview:**
1. **Description** — Ask the user to describe the change in their own words
2. **Clarifying Questions** — Rounds and depth determined by update type (see table above)
3. **Synthesis & Confirmation** — Present a change summary for user approval

### Update Phase 3: Update Documentation

After confirmation, **update** (not recreate) the existing documents. What to update depends on the type:

**All types:**
- `docs/plans.md` — Append new milestones after the last existing milestone (for New Feature / Change),
  or add a fix milestone (for Bug Fix). Follow the same milestone format. Keep existing milestones intact.
- `docs/documentation.md` — Add new milestones to the status section

**New Feature:**
- `docs/architecture.md` — Append new user journeys, pages, components, and product spec sections.
  Update technical architecture if the feature introduces new patterns or integrations.
- `docs/secrets.md` — Update if the feature introduces new secrets or integrations
- `CLAUDE.md` + `AGENT.md` — Update if new commands, structure, or conventions are introduced

**Bug Fix:**
- `docs/architecture.md` — Update only if the fix changes documented behavior or reveals a spec gap.
  Add a note in the relevant product spec section describing the corrected behavior.
- `docs/plans.md` — Record the bug in Implementation Notes

**Change:**
- `docs/architecture.md` — Modify affected sections (user journeys, components, tech architecture, etc.).
  Mark removed or replaced content clearly — do not silently delete.
- `docs/secrets.md` — Update if integrations or secrets change
- `CLAUDE.md` + `AGENT.md` — Update if commands, structure, or conventions change
- `docs/implement.md` — Update only if the change alters execution rules (e.g., new tech stack, new workflow)

**Do NOT modify:**
- Existing completed milestone content (unless fixing a discovered inconsistency)
- `docs/implement.md` (unless the change genuinely requires new execution rules)

### Update Phase 3.5: Documentation Review

Run a lighter review focused on the changes:
- Verify new/modified milestones cover all aspects of the change
- Verify updated architecture sections are consistent with existing ones
- Verify no contradictions between new and existing content

Use Agent 2 (Plans reviewer) + Agent 3 (Consistency reviewer). Skip Agent 1 unless the change adds
entirely new user roles or major architectural changes.

### Update Phase 4: Next Steps

Tell the user:
1. The docs have been updated
2. Summarize what was changed (new/modified milestones, updated architecture sections, etc.)
3. Suggest they review the changes in `docs/architecture.md` and `docs/plans.md`
4. Mention they can adjust the new milestones before starting execution

## Language

Follow the user's language preference. If they write in Chinese, generate documents in Chinese.
If they write in English, generate in English. Technical terms (file names, commands, code) stay in English regardless.
