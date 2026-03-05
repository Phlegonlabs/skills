---
name: project-update
description: >
  Update an existing long-running project that already has structured docs (`docs/architecture.md` and
  `docs/plans.md`). Use this skill for new features, bug fixes, requirement changes, refactors, and migrations
  where docs and milestones must be updated without reinitializing the project.
---

# Project Update

Run this workflow only for existing projects with initialized docs.

## 1. Mode Guard

Before starting:

1. Require both `docs/architecture.md` and `docs/plans.md`.
2. If both files are missing and code exists, switch to `project-convert`.
3. If docs and code are both missing, switch to `project-init`.
4. If only one required doc exists, report partial state and ask user whether to repair via convert, continue with caution, or re-init.

## 2. Context Loading

Load current state first:

1. Read `docs/architecture.md` and `docs/plans.md`.
2. Read supporting docs: `docs/implement.md`, `docs/secrets.md`, `docs/documentation.md`, `docs/design.md`.
3. Auto-create missing supporting docs from templates before update edits.
4. Summarize current milestones, architecture, and patterns to the user.
5. If code exists, scan code roots and compare docs vs code; report major divergences before planning.

## 3. Classify Update Type

Classify and announce one type (allow override):

- New Feature: 3-8 focused rounds
- Bug Fix: 1-3 focused rounds
- Change/Refactor/Migration: 2-5 focused rounds

Reclassify if discovered scope no longer matches the original type.

## 4. Focused Interview

1. Capture user description of requested change.
2. Run scoped clarifying rounds based on type.
3. Produce synthesis and require explicit approval before editing docs.

## 5. Update Documentation

Update existing files instead of recreating:

1. Always update `docs/plans.md` by inserting new milestones **before** the final Production Readiness Gate milestone.
2. Always update `docs/documentation.md` status section.
3. Update `docs/architecture.md` only where behavior/spec/architecture is affected.
4. Update `docs/design.md`, `docs/secrets.md`, `CLAUDE.md`, `AGENTS.md` only when the change impacts them.
5. Keep completed milestone history intact unless fixing proven inconsistency.
6. Do not silently remove replaced requirements; mark and explain transitions.
7. Keep `docs/implement.md` aligned with these mandatory sections:
   - `First-Principles Execution`
   - `Atomic Task Execution`
   - `Rewrite-First Policy`
   - `No-Compatibility Rule`
8. In `docs/plans.md`, every new or modified task must include `Commit Boundary: exactly one atomic commit`.
9. In `tasks/todo.md`, every new or modified task must include `Task ID` and `Commit Status` (`pending` or `done`).

## 5.5. Implementation Discipline (Mandatory)

Apply these rules to every update task:

1. Use first-principles execution: address root causes based on product intent and architecture, not workaround layers.
2. Treat `task` and `sub-task` as the same execution unit.
3. Enforce `one task -> one atomic commit`.
4. Complete one task end-to-end before commit, including all impacted files (code/tests/config/scripts/docs).
5. Follow `code is cheap`: prefer deleting and rewriting problematic modules instead of patching around them.
6. Never introduce compatibility code (`adapter`, `shim`, dual-path logic, deprecated aliases, temporary compatibility flags).
7. If a rewrite changes interfaces, update all impacted callers in the same task.
8. Do not split breakage repair into later tasks.

## 6. Review Protocol

Run lightweight review on modified scope:

1. Agent 2 (plans coverage) + Agent 3 (cross-doc consistency).
2. Mandatory `mcp__codex__codex` review on changed sections (or full docs if needed).
3. Apply valid findings, then run exactly one Agent 2 + Agent 3 post-Codex re-review.
4. Run one user annotation pass on updated `docs/architecture.md` + `docs/plans.md` (Bug Fix can skip only when strictly local and behavior docs are unchanged).

If `mcp__codex__codex` is unavailable, stop and ask user to choose manual checklist path or alternate-model path.

## 7. Hooks Installation (Mandatory)

Install/update hooks for both platforms:

1. Resolve installer path in this order:
   - `scripts/setup-hooks.sh`
   - `../full-project-skill/scripts/setup-hooks.sh`
2. Run:

```bash
bash <resolved-setup-hooks-path> --pm <detected-pm> --project-dir <project-dir> --platform both
```

3. Detect package manager using lockfiles (`bun.lock`, `pnpm-lock.yaml`, `yarn.lock`, fallback npm).
4. If no installer path exists, ask the user where their hook installer lives and stop.
5. If install fails, show error and stop.

## 8. Final Handoff

Tell the user:

1. Docs were updated.
2. Hooks were installed/updated in `.claude/` and `.codex/`.
3. Which milestones/sections changed.
4. They should review `docs/architecture.md` and `docs/plans.md` before execution.
5. New work still must pass the final Production Readiness Gate.
