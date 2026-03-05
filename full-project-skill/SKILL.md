---
name: full-project-skill
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
- A **production readiness gate** that ensures the final output is deployment-ready, not a demo or prototype

The interview phase is critical — it forces clarity before any code is written, which saves hours of rework later.

## Mode Detection

At the start, detect which mode to use:

1. Check if `docs/architecture.md` and `docs/plans.md` already exist in the project
2. If **both exist** → **Update mode** (the project was previously initialized with this skill)
3. If **neither exists** → **Init mode** (new project)
4. If **only one exists** → Potentially corrupted state. Inform the user which file is missing and ask:
   init from scratch (overwrite), or attempt update with incomplete docs?
5. If ambiguous for other reasons, ask the user whether they are modifying the existing project or starting fresh

## Complexity Tiers

After Step 2 (Project Goals), assess complexity and assign a tier. This determines interview depth,
milestone count, and review scope throughout the entire workflow.

**Default tier is Standard.** When in doubt, stay at Standard.

| Tier | When | Target Questions | Interview Rounds | Follow-up Cap | Milestones | Review |
|------|------|-----------------|-----------------|---------------|------------|--------|
| **Standard** | **Default for all projects** — most projects fall here | ~15 | All applicable rounds (full protocol; GUI ~10-11, CLI ~10-13 effective rounds) | 8 | 7-10 | Agent 2 + Agent 3 + Codex review |
| **Complex** | Multi-role, multi-platform, integration-heavy, enterprise | ~25-30 | All applicable rounds (full protocol) + extended depth on architecture, security, scale | 20 | 10-14 | Agent 1 + Agent 2 + Agent 3 + Codex review + exactly one post-Codex Agent 2 + Agent 3 re-review |

Announce the tier to the user after Step 2 and let them override it. Default assumption is Standard.

## Workflow

### Phase 1: Interactive Interview

Collect project information through an interactive conversation. See `references/interview.md` for the full
interview protocol including all rounds, follow-up triggers, and examples.

**Steps overview:**
1. **Project Name** — Ask the user for the project name
2. **Project Goals** — Free-form description of what they're building, the problem, and target users
3. **Market Research Snapshot** — Run one focused market scan before deep scoping: identify similar products,
   open-source analogs, and reference implementations/patterns worth borrowing or avoiding.
4. **Project Intro & Core Flow Draft** — Based on goals + market scan, draft a sharper project introduction
   (problem, target users, positioning) and a candidate end-to-end flow. Confirm this draft with the user.
5. **Design Direction (Step 2.8: Product Architecture + Visual Style)** — Based on the market scan + project intro/core
   flow draft, propose 3-4 product architecture directions and corresponding visual style directions.
   User must choose/confirm one direction before moving on.
6. **Clarifying Questions** — AI-driven discovery interview (rounds and depth determined by complexity tier,
   covering user journeys, components, tech stack finalization, UI/CLI preferences, and deployment).
   Adaptive follow-ups for ambiguities. Tech stack is locked during this step (Round R10.7).
   Use `references/tech-components.md` for category-based stack options and `assets/versions.json`
   for version guidance during lock-in.
7. **Tier Recheck** — After all interview rounds, reassess tier based on what was discovered. If the project
   turned out more complex than initially assessed, upgrade the tier and announce the change to the user.
8. **Synthesis & Confirmation** — Present a complete project summary for user approval before generating docs

### Phase 2: Generate Documentation

After confirmation, create the `docs/` directory and generate all documents. See `references/templates.md`
for the full templates and structure of each file.

**Documents generated:**
- `docs/architecture.md` — Single source of truth: project background, user journeys, components, product spec, technical architecture
- `docs/plans.md` — Execution plan with milestones, sub-tasks, acceptance criteria, verification commands
- `docs/implement.md` — Non-negotiable execution rules for disciplined autonomous work
- `docs/secrets.md` — Secrets & API keys guidance (env vars + safe key handling)
- `docs/documentation.md` — User-facing documentation, kept in sync with reality
- `docs/design.md` — Design system and page-level design spec
- `docs/decisions.md` — Architecture Decision Records (Standard/Complex tier only)
- `tasks/todo.md` — Execution-time sub-task tracker (Current Sprint / Review / Blocked / Completed)
- `tasks/lessons.md` — Correction-derived prevention rules
- `CLAUDE.md` + `AGENTS.md` — Quick-reference files for AI coding tools (same project facts, different operating focus)

### Phase 2.5: Multi-Agent Documentation Review

Launch a multi-agent review team to validate documentation quality, consistency, and completeness.
See `references/review.md` for the full review protocol and agent definitions.
If multi-agent spawning isn't available in your environment, run the same checklists sequentially as a self-review.

**Review agents by tier:**
- **Standard**: Agent 2 + Agent 3.
- **Complex**: Agent 1 + Agent 2 + Agent 3.

Fix all issues found, then proceed.

### Phase 2.6: Cross-Model Review (Mandatory)

Cross-model review is mandatory and must run via `mcp__codex__codex`.

**Protocol:**
1. Prepare a prompt that includes the full `docs/architecture.md` and `docs/plans.md` content.
2. Send that prompt to `mcp__codex__codex` for an independent review.
3. Ask Codex to focus on: architectural gaps, missing edge cases, unrealistic milestones, and
   cross-doc inconsistencies.
4. Fix all valid findings from Codex.
5. **Complex tier only**: after fixes, run **exactly one** post-Codex re-review with **Agent 2 + Agent 3** before proceeding.
   **Standard tier** can proceed directly to Phase 2.7 after Codex findings are applied.
6. Record in output that Phase 2.6 was executed and summarize what was fixed.

If `mcp__codex__codex` is unavailable, do NOT skip silently. Ask the user to either install/enable it
or choose one explicit alternative path:
- **Option A (manual checklist path)**: run the same tier-scoped review checklists sequentially and
  require zero unresolved critical issues.
- **Option B (alternate model path)**: use another available model/tool for an equivalent independent review,
  then apply and summarize findings.
Record which path was used before continuing.

### Phase 2.7: User Annotation Review

After Phase 2.5 and Phase 2.6, present the generated documents to the user for a lightweight annotation pass:

1. Tell the user: "The docs are ready for your review. Please read through `docs/architecture.md`
   and `docs/plans.md`. For anything that needs changes, add inline notes directly in the file
   (e.g., `<!-- NOTE: should use WebSocket not polling -->` or plain-text comments next to the
   relevant section). Then come back and say 'address all notes.'"

2. When the user returns with annotated files:
   - Read the annotated files and identify all user notes/comments
   - Address each note: modify the document to incorporate the feedback
   - Remove the resolved note markers
   - Present a summary of changes made

3. Default expectation: one review pass is usually enough. If the user adds new notes, run another pass
   and resolve them.

4. **Guard**: Do NOT proceed to Phase 3 until the user explicitly says the docs are ready.
   If the user starts describing new features, treat it as additional input and continue
   the annotation cycle, not as a signal to move forward.

This step turns generated docs into a **shared mutable workspace** between user and AI while keeping
the workflow lightweight.

### Phase 3: Next Steps

After review:

**Step 1 — Auto-install hooks (mandatory, run before telling the user anything else):**

Automatically execute the hook installer. Detect the package manager from the project
(check for `bun.lock` → bun, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, default → npm)
and run:

```bash
bash <skill-root>/scripts/setup-hooks.sh --pm <detected-pm> --project-dir <project-dir>
```

Where `<skill-root>` is the root directory of this skill (containing `scripts/setup-hooks.sh`).
If the script fails, show the error to the user and ask them to resolve it before continuing.
Do NOT skip hook installation silently.

**Step 2 — Tell the user:**
1. The docs are ready at `docs/`
2. Hooks have been automatically installed to `.claude/hooks/` and `.claude/settings.json`
3. Suggest they review `docs/architecture.md` and `docs/plans.md`
4. Explain they can start execution by feeding `docs/implement.md` as instructions
5. Mention they can adjust milestone count/scope in `docs/plans.md` before starting
6. **Emphasize**: The final milestone is a **Production Readiness Gate** — the project is NOT considered
   complete until it passes all production-readiness checks. Every milestone builds toward a production-grade
   deliverable, not a demo or prototype.

---

## Update Mode (modifying an existing project)

When mode detection determines **Update mode**, follow this lighter workflow instead of the full Init flow.
See `references/interview.md` § "Update Mode Interview" for the full protocol.

### Update Phase 1: Context Loading

1. Read core docs required for Update mode: `docs/architecture.md`, `docs/plans.md`
2. Load supporting docs: `docs/implement.md`, `docs/secrets.md`, `docs/documentation.md`, `docs/design.md`.
   If any are missing (legacy project), **auto-create** them from current templates before continuing.
   Record which docs were auto-created in the update summary.
3. Identify: current milestone progress, existing features, tech stack, established patterns
4. Briefly summarize the project's current state to the user to confirm alignment
5. **Codebase Pattern Scan** (if source code exists): Before the interview, scan the existing
   source directory to verify docs–code alignment:

   **Scan strategy:**
   1. Discover code roots in this order: `src/`, `app/`, `apps/*/src`, `apps/*/app`, `packages/*/src`, `packages/*/app`, `services/*/src`.
      Scan every root that exists (single-app and monorepo layouts).
   2. Compare against the Directory Structure section in `docs/architecture.md`
   3. Grep for key patterns: route definitions, component naming conventions, API endpoint formats
   4. If >3 divergences are found, summarize them (with concrete path examples) and ask the user:
      "I found these divergences between docs and code: [list]. Should we plan against the
      **code** (update docs to match) or the **docs** (treat code as drifted)?"

   If fewer divergences are found, note them but proceed without blocking.
   This is read-only — do not modify anything.

### Update Phase 1.5: Update Type Classification

Ask the user what kind of change they're making, or infer from their description:

| Type | When | Interview Rounds | Follow-up Cap |
|------|------|-----------------|---------------|
| **New Feature** | Adding new functionality to the project | 3-8 rounds (F0-F8 + F4.5, F0 optional) | 8-15 |
| **Bug Fix** | Fixing a bug that may change behavior, architecture, or require doc updates | 1-3 rounds (B1-B3) | 5 |
| **Change** | Requirement changes, refactors, tech migrations, removing features | 2-5 rounds (C1-C5) | 8 |

Announce the classified type to the user and let them override.

**Type reclassification**: If during the interview the actual scope significantly exceeds the classified type
(e.g., a Bug Fix turns out to require architectural changes, or a Change reveals new feature needs),
re-classify the update type, announce the reclassification to the user, and adjust the remaining
interview rounds accordingly.

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
- `docs/plans.md` — Insert new milestones **before the Production Readiness Gate (Milestone PR)**, not after it.
  The PR milestone must always remain the final milestone. For Bug Fix, add a fix milestone before PR.
  Follow the same milestone format. Keep existing milestones intact. Update Milestone PR sub-tasks if
  the change introduces new production-readiness requirements.
- `docs/documentation.md` — Add new milestones to the status section
- If any supporting docs were missing in Phase 1, create them first from current templates, then apply update edits.

**New Feature:**
- `docs/architecture.md` — Append new user journeys, pages, components, and product spec sections.
  Update technical architecture if the feature introduces new patterns or integrations.
- `docs/design.md` — Add design-system updates and page-level design for new pages/components/interactions
- `docs/secrets.md` — Update if the feature introduces new secrets or integrations
- `CLAUDE.md` + `AGENTS.md` — Update if new commands, structure, or conventions are introduced

**Bug Fix:**
- `docs/architecture.md` — Update only if the fix changes documented behavior or reveals a spec gap.
  Add a note in the relevant product spec section describing the corrected behavior.
- `docs/plans.md` — Record the bug in Implementation Notes

**Change:**
- `docs/architecture.md` — Modify affected sections (user journeys, components, tech architecture, etc.).
  Mark removed or replaced content clearly — do not silently delete.
- `docs/design.md` — Update all affected design sections (system tokens, component variants, page layouts/states)
- `docs/secrets.md` — Update if integrations or secrets change
- `CLAUDE.md` + `AGENTS.md` — Update if commands, structure, or conventions change
- `docs/implement.md` — Update only if the change alters execution rules (e.g., new tech stack, new workflow)

**Do NOT modify:**
- Existing completed milestone content (unless fixing a discovered inconsistency)
- `docs/implement.md` (unless the change genuinely requires new execution rules)

### Update Phase 3.5: Documentation Review

Run a lighter review focused on the changes. See `references/review.md` for full checklist details.

Use Agent 2 (Plans reviewer) + Agent 3 (Consistency reviewer). Skip Agent 1 unless the change adds
entirely new user roles or major architectural changes.

Focus areas:
- Agent 2: Verify new/modified milestones cover all aspects of the change; new milestones are inserted
  before Milestone PR; milestone ordering is logical
- Agent 3: Verify no contradictions between new and existing content; updated architecture sections are
  consistent; CLAUDE.md/AGENTS.md are updated if needed

**Cross-Model Review (Mandatory):**
After Agent 2+3 review, run `mcp__codex__codex` on the modified sections (or full updated docs when needed),
focused on: consistency with existing content, missed edge cases, and milestone coverage gaps.
After applying valid Codex findings, run **exactly one** post-Codex re-review with **Agent 2 + Agent 3**.
If `mcp__codex__codex` is unavailable, stop and ask the user to install/enable it or choose one explicit
alternative path:
- **Option A (manual checklist path)**: run Agent 2 + Agent 3 checklists end-to-end on the updated docs,
  and require zero unresolved critical issues.
- **Option B (alternate model path)**: run an equivalent independent review using another available model/tool,
  then apply and summarize findings.
Record which path was used before continuing.

### Update Phase 3.7: User Annotation Review

After the documentation review, present the updated documents to the user for a **lightweight
annotation cycle** (mirrors Init Phase 2.7 but scoped to changes):

1. Tell the user: "The docs have been updated. Please review the modified sections in
   `docs/architecture.md` and `docs/plans.md`. Add inline notes for anything that needs changes
   (e.g., `<!-- NOTE: ... -->`), then say 'address all notes.'"

2. When the user returns with annotated files:
   - Identify all user notes/comments in the modified sections
   - Address each note and remove the resolved markers
   - Present a summary of changes made

3. **1 round is sufficient** — unlike Init's multi-round cycle, Update mode only needs one
   annotation pass. If the user provides additional feedback, address it, but do not loop
   indefinitely.

4. **Type-based skip rule**: Bug Fix updates may skip this phase if the fix is straightforward
   and does not alter documented behavior. New Feature and Change types should always run this phase.

### Update Phase 4: Next Steps

After review:

**Step 1 — Auto-install/update hooks (mandatory):**

Check if `.claude/hooks/` already exists in the project. Run the hook installer regardless
(it will merge/update existing hooks):

```bash
bash <skill-root>/scripts/setup-hooks.sh --pm <detected-pm> --project-dir <project-dir>
```

Detect the package manager from the project (check for `bun.lock` → bun, `pnpm-lock.yaml` → pnpm,
`yarn.lock` → yarn, default → npm). If the script fails, show the error and ask the user to resolve it.

**Step 2 — Tell the user:**
1. The docs have been updated
2. Hooks have been installed/updated in `.claude/hooks/`
3. Summarize what was changed (new/modified milestones, updated architecture sections, etc.)
4. Suggest they review the changes in `docs/architecture.md` and `docs/plans.md`
5. Mention they can adjust the new milestones before starting execution
6. **Remind**: New milestones follow the same production-quality standard — every sub-task produces
   deployment-ready code. If the update adds significant new functionality, ensure the Production
   Readiness Gate milestone is updated to cover the new scope.

## Engineering Layer

Keep the workflow above as the source of truth, and use a machine-readable contract layer to make it testable.

### Contract Files

- `assets/workflow-map.v1.json` — Mode detection, tier defaults, phase order, update type ranges, output doc list
- `assets/interview-question-pack.v1.json` — Init/update interview round registry and round-level constraints
- `assets/quality-gates.v1.json` — Required references, required SKILL sections, and release gate checklist
- `assets/doc-build-map.v1.json` — Source module directories, assembly order files, and generated doc targets

These files **must not change the workflow semantics**. Their purpose is enforcement and consistency checks.

### Source Of Truth

- `sources/*` is the canonical editable source for generated docs.
- `SKILL.md` and `references/*.md` in this skill are generated artifacts from `sources/*`.
- Do not hand-edit generated artifacts. Edit source partials first, then run docs build.

### Script Entry Points

- `scripts/verify-skill.ts` — Runs contract validation and fails fast on drift
- `scripts/skill-contract.ts` — Shared loaders + validators used by scripts and tests
- `scripts/build-docs.ts` — Assembles source partials into generated docs (write/check modes)
- `scripts/build-docs.sh` — Shell wrapper for `scripts/build-docs.ts`

### Quality Gates

Before publishing changes to this skill, run:

1. `bun run contract:check`
2. `bun run typecheck`
3. `bun run test`

If any check fails, fix the issue before considering the skill update complete.

Doc assembly commands:
- `bun run docs:build` — Regenerate `SKILL.md` + `references/*.md` from `sources/*`
- `bun run docs:check` — Check source/artifact drift without writing

## Hooks

Install project hooks via `scripts/setup-hooks.sh`. Hooks are **platform-universal** and support
both Claude Code and Codex CLI.

### Supported Platforms

| Platform | Config Dir | Template | Event Names |
|----------|-----------|----------|-------------|
| Claude Code | `.claude/` | `settings.template.json` | `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` |
| Codex CLI | `.codex/` | `settings.template.codex.json` | `on_agent_message`, `pre_tool_call`, `post_tool_call`, `on_session_end` |

### Hook Scripts (shared across platforms)

All hook scripts live in `assets/hooks/` and are platform-agnostic. They use shared helpers:
- `hook-input.sh` — Unified input parsing (supports both Claude Code and Codex CLI env vars / JSON)
- `hook-output.sh` — Platform-aware structured output (auto-detects platform for JSON responses)

Default hook coverage:
- User prompt guards: `prompt-guard.sh`, `phase-tracker.sh`
- Pre-tool guards: `worktree-guard.sh`, `tdd-guard-hook.sh`, `pre-code-change.sh`, `plan-gate.sh`, `research-gate.sh`
- Pre-tool (Bash): `pre-commit-lint.sh`, `pre-push-test.sh`, `immutable-layer-guard.sh`
- Post-tool guards: `anti-simplification.sh`, `doc-drift-guard.sh`, `atomic-pending.sh`, `plan-sync-reminder.sh`
- Post-bash guards: `post-bash.sh`, `atomic-commit.sh`
- Session monitor: `context-pressure-hook.sh`
- Session end: `session-end-reminder.sh`
- Shared helpers: `hook-input.sh`, `hook-output.sh`

### Auto-Installation

Hooks are **automatically installed** during Phase 3 (Init) and Update Phase 4.
The skill auto-detects the package manager and runs `setup-hooks.sh` without user intervention.

Manual installation:
```bash
# Claude Code (default)
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project

# Codex CLI
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project --platform codex

# Both platforms at once
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project --platform claude
bash scripts/setup-hooks.sh --pm bun --project-dir /path/to/project --platform codex
```

## Language

Follow the user's language preference. If they write in Chinese, generate documents in Chinese.
If they write in English, generate in English. Technical terms (file names, commands, code) stay in English regardless.
