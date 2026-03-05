---
name: project-convert
description: >
  Convert an existing codebase into the structured long-running workflow when code already exists but required docs
  are missing (`docs/architecture.md`, `docs/plans.md`). Use this for bootstrap/upgrade of cloned or legacy repos
  so they gain consistent docs, milestones, and hook/HK setup without losing current behavior.
---

# Project Convert

Run this workflow for existing repositories that need structured workflow bootstrap.

## 1. Mode Guard

Use this skill when:

1. `docs/architecture.md` and `docs/plans.md` are missing.
2. Codebase signals exist (`src/`, `app/`, `apps/*/src`, `packages/*/src`, `services/*/src`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`).

If docs already exist, switch to `project-update`.
If docs and codebase signals are both absent, switch to `project-init`.

## 2. Discovery Baseline (Read-Only)

Build factual baseline before writing docs:

1. Discover all code roots in monorepo/single-repo layouts.
2. Map runtime shape: entry points, routes/API surfaces, modules, data/storage/integrations.
3. Detect existing docs fragments (`README`, ad-hoc notes) and reusable information.
4. Detect missing workflow assets (`docs/`, `tasks/`, `.claude/hooks/`, `.codex/hooks/`).
5. Summarize current reality and gaps to user; require baseline confirmation.

## 3. Conversion Interview Parity (Must Match `full-project-skill`)

This split skill must run the same conversion interview protocol as `full-project-skill`.
Do not use a shortened or simplified Q&A path.

### 3.1 Mandatory Protocol Source

Before asking conversion interview questions, load and follow:

- `references/interview.md` (`Convert/Upgrade Mode Interview` section)

If this file is unavailable, stop and ask the user whether to:
- provide an alternate protocol file, or
- switch to using `full-project-skill` directly.

### 3.2 Required Interview Flow (Exact Order)

1. Step 1 - Current-state confirmation:
   - Present the discovery baseline (structure/runtime, feature boundaries, command/test/deploy shape, missing assets).
   - Require user confirmation/correction before Step 2.
2. Step 1.5 - Conversion profile classification:
   - Baseline Conversion or Upgrade Conversion.
   - Announce profile and allow override.
   - If scope expands during interview, reclassify and announce.
3. Step 2 - Clarifying rounds (profile-scoped):
   - Baseline Conversion: CV0-CV3, use 2-4 rounds, follow-up cap 6.
   - Upgrade Conversion: include CV0 + CU1-CU4, use 3-6 rounds, follow-up cap 10.
   - Shared round rules: 1-2 focused questions per round, anchor every question to discovered code reality, skip non-applicable rounds.
4. Before leaving Step 2, run one final additions/confirmation question in the user's language.
5. Step 3 - Convert synthesis & confirmation:
   - Present conversion plan summary.
   - Require explicit user approval before writing any docs.

### 3.3 Hard Constraints (No Simplification)

1. Do not skip CV/CU round IDs defined in the protocol without explicit user direction.
2. Follow-up rounds are extra depth and do not replace required base rounds.
3. Do not generate docs, write files, or install hooks before explicit synthesis confirmation.
4. If user adds requirements during synthesis, fold them back into interview rounds first.

## 4. Documentation Bootstrap

Generate workflow docs from actual code reality:

- `docs/architecture.md` (include current-state snapshot + known divergences)
- `docs/plans.md` (conversion milestones, final Production Readiness Gate milestone)
- `docs/implement.md`
- `docs/secrets.md`
- `docs/documentation.md`
- `docs/design.md`
- `tasks/todo.md`
- `tasks/lessons.md`
- `CLAUDE.md`
- `AGENTS.md`

Profile rules:

1. Baseline Conversion: prioritize accurate documentation of existing behavior.
2. Upgrade Conversion: separate baseline-capture milestones from upgrade milestones; include migration/rollback notes when contracts change.
3. Do not silently refactor implementation during conversion unless explicitly requested.
4. In `docs/implement.md`, include mandatory sections:
   - `First-Principles Execution`
   - `Atomic Task Execution`
   - `Rewrite-First Policy`
   - `No-Compatibility Rule`
5. In `docs/plans.md`, every task must include `Commit Boundary: exactly one atomic commit`.
6. In `tasks/todo.md`, every task must include `Task ID` and `Commit Status` (`pending` or `done`).

## 4.5. Implementation Discipline (Mandatory)

Apply these rules to post-conversion implementation tasks:

1. Use first-principles execution: solve the real root cause from requirements and architecture.
2. Treat `task` and `sub-task` as the same execution unit.
3. Enforce `one task -> one atomic commit`.
4. Complete each task fully before commit, including impacted code/tests/config/scripts/docs.
5. Follow `code is cheap`: if a module is problematic, delete and rewrite the module.
6. Do not introduce compatibility code (`adapter`, `shim`, dual-path logic, deprecated aliases, temporary compatibility flags).
7. If a rewrite changes interfaces, fix every impacted caller in the same task.
8. Do not defer breakage fixes to future tasks.

## 5. Review Protocol

Before handoff:

1. Agent 2 + Agent 3 review converted docs.
2. Mandatory `mcp__codex__codex` review focused on docs-code alignment, missing edge cases, and milestone coverage.
3. Apply findings and run exactly one Agent 2 + Agent 3 post-Codex re-review.
4. Run one user annotation pass on `docs/architecture.md` + `docs/plans.md`, resolve notes, and wait for explicit readiness confirmation.

If `mcp__codex__codex` is unavailable, pause and ask user to choose manual checklist path or alternate-model path.

## 6. Hooks Installation (Mandatory)

Install/update hooks after docs are accepted:

1. Resolve installer path:
   - `scripts/setup-hooks.sh`
2. Run:

```bash
bash <resolved-setup-hooks-path> --pm <detected-pm> --project-dir <project-dir> --platform both
```

3. Detect package manager by lockfile (`bun.lock`, `pnpm-lock.yaml`, `yarn.lock`, fallback npm).
4. If no installer path exists, ask the user where their hook installer lives and stop.
5. If command fails, surface error and stop for user resolution.

## 7. Final Handoff

Tell the user:

1. Conversion/upgrade docs bootstrap is complete.
2. Hooks are installed/updated in `.claude/` and `.codex/`.
3. Baseline capture items vs upgrade backlog items.
4. They should review `docs/architecture.md` + `docs/plans.md` before implementation.
5. Completion still depends on passing the final Production Readiness Gate.
