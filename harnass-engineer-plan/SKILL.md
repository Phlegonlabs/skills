---
name: harnass-engineer-plan
version: 1.1.0
description: Research an existing repository, align with the user, and generate a reviewed machine-readable execution plan. After plan approval, immediately proceed to implementation without waiting for user input. Use when Codex needs to inspect the current stack, discover frontend and backend design choices, call the external frontend-design skill for ui-facing work, create wireframe and design docs, classify task horizon, create milestones and tasks, define validation per task, self-review the result, and approve a task-by-task implementation plan. When the target repo lacks the `harnass-os/...` scaffold from `harnass-engineer-start`, this skill may only produce a read-only draft and must not write planning artifacts.
docking:
  phase: plan
  entry_condition: scaffold exists and intent must be written
  reads:
    - harnass-os/documents/.harnass-version.yaml
    - harnass-os/documents/routes/router.yaml
    - harnass-os/documents/routes/load-order.yaml
    - harnass-os/documents/validation/profiles.yaml
    - harnass-os/documents/orchestrator/current.yaml
  writes:
    - harnass-os/documents/intake/request.yaml
    - harnass-os/documents/inventory/current-state.yaml
    - harnass-os/documents/plans/<slug>.yaml
    - harnass-os/documents/plans/milestone-tasks.md
    - harnass-os/documents/design/*.md (when ui_facing)
    - harnass-os/documents/validation/design-review.yaml (when ui_facing)
    - harnass-os/documents/release/current.yaml (when release_affecting)
    - harnass-os/documents/deploy/current.yaml (when release_affecting)
    - harnass-os/documents/runtime/cloudflare.yaml (when runtime_relevant)
    - harnass-os/documents/decisions/** (when direction changes)
  requires_phase: start
  emits_to_phase: implement
---

# Harnass Engineer Plan

Read [documents/router.yaml](./documents/router.yaml).

If `harnass-os/...` is missing, stay in read-only draft mode: inspect the repo, align with the user, summarize the draft in chat, and direct the repo through `harnass-engineer-start` before writing plan files.

CRITICAL EXECUTION RULE:
After the user approves the plan, you MUST immediately begin executing tasks.
Do NOT output a summary and stop. Do NOT ask "should I proceed?". Do NOT wait.
The plan approval IS the signal to start. Read Implement.md, pick the first pending task, and execute it now.

Do:
- announce current phase and step before executing (planning visibility)
- scan repo reality
- use the start-generated `harnass-os/...` scaffold as the canonical planning surface
- switch to read-only draft mode when the scaffold is missing
- write inventory
- capture entrypoints, package manager commands, build/test commands, and deploy facts from repo reality
- ask user
- write plan yaml
- call `frontend-design` for ui-facing work
- create `harnass-os/documents/design/wireframe.md` and `harnass-os/documents/design/design.md`
- define design validation for UI-facing work
- define deployment flow when release work is part of the plan
- define milestone-scoped worktree execution and per-task commit boundaries for long-run plans
- record durable decisions when ui, runtime, or release direction changes
- make tasks execution-ready with read scopes, entrypoints, implementation steps, validation commands, and structured integration audit flows when release/UI work is involved
- self-review before approval
- after plan approval: immediately read harnass-os/Implement.md and begin-implementation step — execute every task in the plan without pausing between them

Do not:
- backfill missing bootstrap layers during planning
- do not write `harnass-os/...` planning artifacts in read-only draft mode
- skip inspection
- finalize plan before alignment
- approve plan without review gates
- stop after plan approval and wait for user input — implementation must start automatically
- output a "plan is ready, shall I proceed?" message — the user's approval IS the proceed signal

Gates:
- planning visibility — announce phase and step before executing
- inventory first
- read-only draft mode when scaffold is missing
- full scaffold before writing or approving plan artifacts
- frontend-design before ui plan approval
- ask user before final plan
- self-review before approval
- tasks need validation, commit, handoff
- tasks need entrypoints, implementation steps, and validation commands
