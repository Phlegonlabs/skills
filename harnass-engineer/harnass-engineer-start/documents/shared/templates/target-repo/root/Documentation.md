# Documentation Route

## status_route
- Update `harnass-os/documents/status/current.yaml` after every validated task or milestone transition.

## orchestrator_route
- Update `harnass-os/documents/orchestrator/current.yaml` whenever the active phase changes or lifecycle blockers appear.
- Prefer `python harnass-os/scripts/orchestrator.py tick` over hand-editing the orchestrator state.

## run_ledger_route
- Update `harnass-os/documents/runs/current.yaml` whenever the active task, validation history, or runtime summary changes.

## deploy_route
- Update `harnass-os/documents/deploy/current.yaml` when preview, production, or rollback state changes.
- Update `harnass-os/documents/release/current.yaml` when preview acceptance or production gate state changes.

## audit_route
- Update `harnass-os/documents/audit/current.yaml` during final audit execution.
- Archive each audit under `harnass-os/documents/audit/history/` and write human-readable findings under `harnass-os/documents/audit/findings/`.
- Do not set `harnass-os/documents/release/current.yaml` to `complete` until final audit passes.

## handoff_route
- Record each finished task in `harnass-os/documents/handoffs/<task-id>.yaml` before the next task starts.

## decision_log_rule
- Capture decision notes while context is fresh.

## adr_route
- Update `harnass-os/documents/decisions/index.yaml` when a new ADR is created.
- Link ADRs back to plans, design docs, runtime docs, or release docs.

## known_issues_rule
- Record known issues, remaining risks, and follow-ups in the active status document.
- Record deployment notes and post-release issues in the active status document.

## update_timing
- Sync documents before commit, before push, and before returning work to the lead agent.

