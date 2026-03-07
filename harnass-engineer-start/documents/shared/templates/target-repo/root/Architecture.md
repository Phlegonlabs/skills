# Project Architecture

## Lifecycle Phases

```
start → plan → implement → deploy → audit
```

| Phase | Owner | Entry | Output |
|---|---|---|---|
| Start | harnass-engineer-start | repo lacks scaffold | `harnass-os/` scaffold materialized |
| Plan | harnass-engineer-plan | scaffold exists | approved plan in `harnass-os/documents/plans/` |
| Implement | agent (solo or lead-worker) | approved plan | committed code + handoffs |
| Deploy | agent | implementation complete | preview → production deployment |
| Audit | harnass-engineer-final-audit | production deployed | release signoff or remediation |

## Repository Layout

```
<repo-root>/
  AGENTS.md              # agent entry — routing rules and red-line defaults
  CLAUDE.md              # alternate agent entry — read order and routing
  Plan.md                # planning runbook — intake, discovery, review, approval
  Architecture.md        # this file — project structure and lifecycle overview
  harnass-os/
    Implement.md         # execution runbook — task pickup, validation, commit
    Deploy.md            # deployment runbook — preview, production, rollback
    Audit.md             # final audit runbook — post-deploy checks, release signoff
    Documentation.md     # documentation runbook — status, run log, handoffs
    documents/
      .harnass-version.yaml
      routes/
        router.yaml      # phase routing and gate definitions
        load-order.yaml  # per-phase document read order
      intake/
        request.yaml     # user goal, project name, constraints
        change-requests/current.yaml
        re-plan-requests/current.yaml
      inventory/
        current-state.yaml  # discovered repo shape, stack, commands
      plans/
        <slug>.yaml      # machine-readable execution plan
        milestone-tasks.md  # human-readable progress tracker
      design/
        wireframe.md     # screen flows and layout (UI projects)
        design.md        # component specs and styling (UI projects)
      validation/
        profiles.yaml    # validation profile definitions
        design-review.yaml  # design review checklist (UI projects)
      runtime/
        cloudflare.yaml  # runtime binding and config details
      release/
        current.yaml     # release gating and promotion state
      deploy/
        current.yaml     # deployment commands and environment state
      audit/
        current.yaml     # final audit state and findings
        browser/current.yaml  # browser evidence for UI projects
        history/         # archived audits
        findings/        # human-readable audit reports
      decisions/
        index.yaml       # architecture decision log
        adr-template.md  # ADR template
      orchestrator/
        current.yaml     # lifecycle phase state machine
      runs/
        current.yaml     # active run ledger
        history/         # archived run reports
      status/
        current.yaml     # current milestone and task status
      handoffs/
        <task-id>.yaml   # per-task completion handoffs
      waivers/
        active.yaml      # gate waiver registry
      scenarios/         # execution scenario definitions
    hooks/
      pre-commit         # plan-gate and lint checks
      commit-msg         # commit message format enforcement
      pre-push           # push-gate validation
    scripts/
      agent-guard.py     # gate enforcement CLI
      orchestrator.py    # lifecycle state machine
      executor.py        # task/deploy/audit automation runner
      harnass.py         # thin CLI wrapper
      harnass_yaml.py    # shared YAML parser
```

## Routing

Agents enter through `AGENTS.md` or `CLAUDE.md` at the repo root.
Both route to `harnass-os/documents/routes/router.yaml` which defines per-phase read lists and gate conditions.
`harnass-os/documents/routes/load-order.yaml` specifies the exact document read sequence for each phase.

## Gates

Every phase transition is gated:
- **Bootstrap → Plan**: scaffold files must exist
- **Plan → Implement**: plan must be approved, execution_ready flags set
- **Implement → Deploy**: all milestone tasks committed and validated
- **Deploy → Audit**: production deployment recorded
- **Audit → Complete**: final audit passes with no blocking findings

Gate enforcement runs through `harnass-os/scripts/agent-guard.py` and git hooks.

## Orchestrator

`harnass-os/documents/orchestrator/current.yaml` tracks the active lifecycle state.
`harnass-os/scripts/orchestrator.py tick` reconciles phase transitions after document updates.

## Execution Model

- Plans contain **milestones** (testable capabilities) and **tasks** (atomic commits)
- Each milestone gets a dedicated worktree: `../milestone-<id>` on branch `milestone/<id>`
- Each task follows: pick → code → validate → commit → handoff → update plan
- The milestone-tasks tracker (`harnass-os/documents/plans/milestone-tasks.md`) is the human-readable progress view

