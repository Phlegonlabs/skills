---
name: project-long-task
description: >
  Initialize a long-running project with a structured docs workflow. Use this skill whenever the user wants to
  start a new project, kick off a long-running build task, set up project documentation structure, or says things
  like "new project", "start a project", "init project", "project setup", or "I want to build something from scratch".
  Also use when the user mentions wanting a milestone-based plan, structured execution workflow, or asks to
  scaffold documentation for a complex multi-step build.
---

# Project Long Task

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

Collect project information through an interactive conversation. See `references/interview.md` for the full
interview protocol including all rounds, follow-up triggers, and examples.

**Steps overview:**
1. **Project Name** — Ask the user for the project name
2. **Project Goals** — Free-form description of what they're building, the problem, and target users
3. **Clarifying Questions** — AI-driven discovery interview (9-12 base rounds covering user journeys,
   components, tech baseline, UI/CLI preferences, and deployment). Adaptive follow-ups for ambiguities.
4. **Tech Stack Finalization** — Lock in runtime, framework, styling, database choices
5. **Synthesis & Confirmation** — Present a complete project summary for user approval before generating docs

### Phase 2: Generate Documentation

After confirmation, create the `docs/` directory and generate all documents. See `references/templates.md`
for the full templates and structure of each file.

**Documents generated:**
- `docs/architecture.md` — Single source of truth: project background, user journeys, components, product spec, technical architecture
- `docs/plans.md` — Execution plan with milestones, sub-tasks, acceptance criteria, verification commands
- `docs/implement.md` — Non-negotiable execution rules for disciplined autonomous work
- `docs/documentation.md` — User-facing documentation, kept in sync with reality
- `CLAUDE.md` + `AGENT.md` — Quick-reference files for AI coding tools (identical content, under 80 lines)

### Phase 2.5: Multi-Agent Documentation Review

Launch a multi-agent review team to validate documentation quality, consistency, and completeness.
See `references/review.md` for the full review protocol and agent definitions.

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

## Language

Follow the user's language preference. If they write in Chinese, generate documents in Chinese.
If they write in English, generate in English. Technical terms (file names, commands, code) stay in English regardless.
