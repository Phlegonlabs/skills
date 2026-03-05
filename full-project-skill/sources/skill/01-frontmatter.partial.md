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
