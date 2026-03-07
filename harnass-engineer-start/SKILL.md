---
name: harnass-engineer-start
description: Bootstrap or retrofit a repository so agents can work safely. Use when Codex needs to create or normalize the repo entry layer, documents folder, design, runtime, release, audit, and decision files, hook and guard constraints, validation skeletons, worktree rules, or the full agentic scaffold before research, ask-user, planning, task execution, or final signoff. This skill owns the canonical scaffold source that materializes `harnass-os/...` in the target repo.
docking:
  phase: start
  entry_condition: repo lacks the full scaffold
  reads: []
  writes:
    - harnass-os/**
    - AGENTS.md
    - CLAUDE.md
    - Plan.md
    - Architecture.md
  requires_phase: null
  emits_to_phase: plan
---

# Harnass Engineer Start

Read [documents/router.yaml](./documents/router.yaml).

This skill owns the canonical scaffold source under `documents/shared/`.

Use `scripts/bootstrap_target_repo.py . --mode auto --overwrite-policy create-or-merge` to materialize the target repo scaffold (`.` = current working directory, which is the target repo root), then scaffold the frontend-design route without doing design generation.

Do:
- create target repo `harnass-os/`
- own the canonical scaffold source inside this skill's `documents/shared/`
- materialize target repo templates from the canonical spec
- run `scripts/bootstrap_target_repo.py . --mode auto --overwrite-policy create-or-merge`
- emit root entry files: `AGENTS.md`, `CLAUDE.md`, `Plan.md`, `Architecture.md`
- emit canonical runbooks under `harnass-os/`: `Implement.md`, `Deploy.md`, `Audit.md`, `Documentation.md`
- emit canonical intake, design, runtime, release, audit, run, status, decision, design validation, deploy, route, and handoff skeletons under `harnass-os/documents/`
- emit browser-audit report scaffolding under `harnass-os/documents/audit/browser/`
- write the mandatory route for the external `frontend-design` skill on ui-facing work
- wire the post-production final audit route and release-signoff gates
- wire hooks, guard entry, validation, and worktrees

Do not:
- do research, ask-user, or planning
- do not generate final ui pages
- skip bootstrap gates

Gates:
- documents first
- templates before placeholders
- bootstrap engine before scaffold-complete
- frontend-design route before ui execution
- full scaffold before planning
- planning belongs to `harnass-engineer-plan`
