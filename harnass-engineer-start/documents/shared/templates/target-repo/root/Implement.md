# Implementation Route

## plan_route
- Read root `Plan.md` and the approved `harnass-os/documents/plans/<slug>.yaml`.

## execution_gate
- Confirm self-review passed and `execution_ready` is true before edits.
- Read `harnass-os/documents/orchestrator/current.yaml` before task pickup and keep it aligned with the active phase.

## horizon_route
- Route by `task_horizon` and current milestone state.

## design_route
- For UI-facing work, read `harnass-os/documents/design/wireframe.md` and `harnass-os/documents/design/design.md` before coding.
- Re-enter `frontend-design` only when the design docs are stale or explicitly revised.

## task_pickup
- Pick one approved task.
- Confirm read scope, write scope, entrypoints, implementation steps, dependencies, and validation commands before coding.

## worktree_rules
- Default to one dedicated worktree and branch per milestone: `../milestone-<milestone-id>` on `milestone/<milestone-id>`.
- Keep per-task commits inside that milestone worktree; merge back only after milestone exit validation passes.
- Do not overlap write scopes in parallel work.

## validation_before_commit
- Run the task validation profile and task validation commands before committing.
- Repair failures before advancing.

## plan_change_rule
- Update the plan change log before any task-shape change.

## handoff_rule
- Write `harnass-os/documents/handoffs/<task-id>.yaml` after each committed task.

## release_handoff_rule
- Do not treat implementation complete as deployment complete.
- Hand release work to `Deploy.md`, `harnass-os/documents/runtime/<provider>.yaml`, `harnass-os/documents/release/current.yaml`, and `harnass-os/documents/deploy/current.yaml`.

## next_task_rule
- Do not advance the next task until the current handoff exists.

## long_run_status_route
- Update `harnass-os/documents/runs/current.yaml` and `harnass-os/documents/status/current.yaml` during long-run execution.

## post_task_atomic_workflow
- After each task, follow this exact sequence: review changed files → run validation → repair failures → commit → write handoff → update plan → update `harnass-os/documents/plans/milestone-tasks.md`.
- Do not skip or reorder steps. Each step must complete before the next begins.
- Let `python harnass-os/scripts/orchestrator.py tick` reconcile phase state after task and deploy document updates.

