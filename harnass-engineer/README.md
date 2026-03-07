# Harnass Engineer

A Claude Code Skill suite that transforms any code repository into a **structured, trackable, and verifiable AI Agent working environment**. It uses YAML contracts, templates, scenarios, and routes to constrain Agent behavior — ensuring Agents follow approved plans, execute task-by-task, validate task-by-task, and commit task-by-task.

## Pipeline Overview

The system consists of **three Skills** and **two implicit phases** (implement + deploy), forming a complete pipeline:

```
harnass-engineer-start  -->  harnass-engineer-plan  -->  implement  -->  deploy  -->  harnass-engineer-final-audit
     (bootstrap)              (research + plan)       (scaffold-driven)  (runbook-driven)   (post-production audit)
```

```
+---------------------------+
|  harnass-engineer-start   |
|                           |
|  detect repo shape        |
|  --> bootstrap engine     |
|  --> materialize 42 files |
|  --> configure git hooks  |
|  --> seed orchestrator    |
|  --> bootstrap gates      |
|                           |
|  emit: scaffold-ready     |
|  next_owner: plan         |
+-----------+---------------+
            | harnass-os/ scaffold exists
            v
+---------------------------+
|  harnass-engineer-plan    |
|                           |
|  check scaffold:          |
|    exists --> research-and-plan
|    missing -> read-only-draft
|    version mismatch -> warn-and-continue
|                           |
|  research repo --> ask    |
|  --> write inventory      |
|  --> call frontend-design |
|  --> build plan + tasks   |
|  --> self-review          |
|  --> user approval        |
|                           |
|  emit: plan approved      |
+-----------+---------------+
            | approved plan exists
            v
+---------------------------+
|  implement (not a Skill)  |
|                           |
|  driven by scaffold docs  |
|  + hooks + agent-guard.py |
|  + orchestrator.py        |
|  + harnass.py             |
|                           |
|  pick --> implement -->   |
|  validate --> commit -->  |
|  handoff --> next task    |
+-----------+---------------+
            | all tasks done, release-affecting
            v
+---------------------------+
|  deploy (not a Skill)     |
|                           |
|  driven by Deploy.md +    |
|  deploy/current.yaml      |
|                           |
|  build --> preview -->    |
|  production deploy -->    |
|  record deployment status |
+-----------+---------------+
            | production deployment recorded
            v
+-------------------------------+
| harnass-engineer-final-audit  |
|                               |
|  verify production deployed   |
|  --> select audit modules     |
|  --> smoke test first         |
|  --> deep audit per module    |
|  --> write audit report       |
|  --> block or pass release    |
|                               |
|  emit: audit artifacts +      |
|        release signoff        |
+-------------------------------+
```

---

## Skill Docking Protocol

Each skill declares its scaffold dependencies and outputs via a **docking block** in its `SKILL.md` frontmatter:

```yaml
---
name: harnass-engineer-plan
description: ...
docking:
  phase: plan
  entry_condition: scaffold exists and intent must be written
  reads:
    - harnass-os/documents/.harnass-version.yaml
    - harnass-os/documents/orchestrator/current.yaml
  writes:
    - harnass-os/documents/plans/<slug>.yaml
    - harnass-os/documents/inventory/current-state.yaml
  requires_phase: start
  emits_to_phase: implement
---
```

The docking block provides:

| Field | Purpose |
|---|---|
| `phase` | The orchestrator phase this skill owns |
| `entry_condition` | Human-readable precondition for entering this skill |
| `reads` | Scaffold files this skill needs to read |
| `writes` | Scaffold files this skill produces or modifies |
| `requires_phase` | Which phase must complete before this skill runs |
| `emits_to_phase` | Which phase this skill hands off to (null = terminal) |

The shared `default-sequence.yaml` also declares `docking_convention` — the canonical scaffold paths and extension points for new skills.

### How the Orchestrator Uses Docking

At bootstrap time, `bootstrap_target_repo.py` discovers all skills from `suite.json`, reads each `SKILL.md` docking block, and writes `registered_phases` into `harnass-os/documents/orchestrator/current.yaml`. The orchestrator reads phases from this config instead of hardcoding them, so adding a new skill automatically registers its phase.

---

## Adding a New Skill

1. **Create a skill directory** under `harnass-engineer/` (e.g., `harnass-engineer-lint`)
2. **Write `SKILL.md`** with a docking frontmatter block declaring `phase`, `reads`, `writes`, `requires_phase`, and `emits_to_phase`
3. **Register in `suite.json`** — add the skill entry
4. **Add a `documents/router.yaml`** — define scenario selection, document loading, and emit targets. Reference the shared `default-sequence.yaml` via relative path: `../../harnass-engineer-start/documents/shared/routes/default-sequence.yaml`
5. **Add scenarios and contracts** under `documents/scenarios/` and `documents/contracts/`
6. **Re-bootstrap** — run `harnass-engineer-start` to pick up the new phase in `registered_phases`

The skill entry point chain is: **SKILL.md** → **router.yaml** → **scenario** → **contracts**

---

## Skill 1: harnass-engineer-start (Bootstrap)

**Responsibility:** Generate the complete `harnass-os/` working infrastructure in the target repository.

### What It Does

1. **Detects repo state** — determines if the repo is greenfield (empty) or retrofit (has code but no Agent layer)
2. **Runs `bootstrap_target_repo.py`** — materializes **42 template files** from `documents/shared/templates/target-repo/` into the target repo
3. **Configures Git hooks** — `git config core.hooksPath harnass-os/hooks`
4. **Seeds Orchestrator State** — initializes `harnass-os/documents/orchestrator/current.yaml` to `READY_FOR_PLAN` with dynamically discovered `registered_phases`
5. **Runs Bootstrap Gates** — verifies all materialized files exist
6. **Writes Bootstrap Report** — records to `runs/history/bootstrap-*.yaml`

### Generated Scaffold

| Layer | Output |
|---|---|
| Root entry stubs | `AGENTS.md`, `CLAUDE.md`, `Plan.md`, `Implement.md`, `Deploy.md`, `Documentation.md`, `Audit.md` |
| harnass-os runbooks | `harnass-os/AGENTS.md`, `CLAUDE.md`, `Plan.md`, `Implement.md`, `Deploy.md`, `Documentation.md`, `Audit.md` |
| Design docs | `harnass-os/documents/design/wireframe.md`, `design.md` |
| Routes | `harnass-os/documents/routes/router.yaml`, `load-order.yaml` |
| Intake | `intake/request.yaml`, `intake/change-requests/current.yaml` (reserved), `intake/re-plan-requests/current.yaml` (reserved) |
| State management | `inventory/current-state.yaml`, `runs/current.yaml`, `status/current.yaml`, `orchestrator/current.yaml` |
| Runtime / Deploy | `runtime/cloudflare.yaml`, `release/current.yaml`, `deploy/current.yaml` |
| Audit | `audit/current.yaml` |
| Decision records | `decisions/index.yaml`, `adr-template.md` |
| Validation | `validation/design-review.yaml`, `profiles.yaml` |
| Git Hooks | `hooks/pre-commit`, `commit-msg`, `pre-push` |
| Guard / control scripts | `scripts/harnass_yaml.py` (shared YAML helpers), `scripts/agent-guard.py` (20 runtime guard commands), `scripts/orchestrator.py` (tick-driven lifecycle state machine), `scripts/harnass.py` (thin unified CLI) |
| Version stamp | `.harnass-version.yaml` |
| Waiver system | `waivers/active.yaml` |
| Manifest | `manifest.yaml` |

### What It Does NOT Do

- No research, no user questions, no planning — all delegated to `harnass-engineer-plan`
- No UI page generation — UI design is delegated to the `frontend-design` skill

### Scenarios

| Scenario | Trigger |
|---|---|
| `greenfield-start` | Empty or light repo |
| `retrofit-bootstrap` | Has code but no Agent layer |

### Handoff to Plan

On completion, emits `scaffold-ready` + `plan-ready`. The handoff document at `harnass-os/documents/runs/history/bootstrap-*.yaml` sets `next_owner: plan`.

---

## Skill 2: harnass-engineer-plan (Research + Planning)

**Responsibility:** Research the target repository, align with the user, and generate a reviewed, machine-readable execution plan.

### Prerequisite Check

The Plan skill first checks whether the `harnass-os/` scaffold exists:

| Condition | Scenario | Behavior |
|---|---|---|
| Scaffold exists | `research-and-plan` | Full planning workflow |
| Scaffold missing | `research-read-only-draft` | Read-only draft mode — inspect, summarize in chat, direct user to run start first |
| Incompatible version | `warn-and-continue` | Warn and proceed |

### Full Planning Flow (research-and-plan)

#### Phase 0: Version Handshake

- Read `.harnass-version.yaml` to confirm scaffold compatibility

#### Phase 1: Research Repository

- Scan config files (`package.json`, `tsconfig.json`, `wrangler.toml`, etc.)
- Deep-scan frontend / backend / styling / data / infrastructure layers
- Extract package manager, dev/build/test/lint commands, entry point files

#### Phase 2: User Alignment

- Capture project name, goal, and idea (intake)
- Classify task horizon (`single_task` vs `long_run`) to determine question depth:
  - `single_task` — 1-3 rounds of questions
  - `long_run` — 3 fixed rounds + up to 7 deep-dive rounds
- Ask app type, framework preferences, package manager, styling approach, runtime target
- Ask product scope, key features, constraints
- **Web Search** — search market status of detected frameworks and tools to validate tech stack choices (after user confirms preferences)

#### Phase 3: Write Inventory

- Fill `harnass-os/documents/inventory/current-state.yaml` with research findings + user answers

#### Phase 4: Design (UI Projects)

- Call `frontend-design` skill to generate `wireframe.md` and `design.md` (contract: `frontend-design-interface.yaml`)
- Fill design validation checklist `design-review.yaml`
- **Block planning if `frontend-design` skill is unavailable for UI-facing work**

#### Phase 5: Build Plan

- Create `harnass-os/documents/plans/<slug>.yaml`
- Classify Agent topology (`solo` vs `lead-worker`)
- Build **capability milestones** — each delivers a testable capability (contract: `milestone-schema.yaml`)
- Build **atomic tasks** — each task must include:

| Required Field | Purpose |
|---|---|
| `id` | Unique task identifier |
| `goal` | One-sentence description |
| `depends_on` | Task dependency chain |
| `read_scope` | Files/directories the task needs to read |
| `write_scope` | Files the task will create or modify |
| `entrypoints` | Files to read FIRST with reason |
| `implementation_steps` | Concrete steps with action/tool/output |
| `validation_commands` | Actual shell commands to verify |
| `commit_required: true` | One task = one commit |
| `handoff_output` | Path to handoff document |

#### Phase 6: Conditional Routes

- If deployment is involved — fill runtime / release / deploy documents
- If major decisions are made — write ADRs to decisions/

#### Phase 7: Review and Approval

1. **Self-review** — verify all tasks are complete, no `<fill>` placeholders remain
2. **User confirmation** — present the complete plan for user approval
3. **Approve** — set `status: approved`, mark all `execution_ready` flags true
4. **Generate `milestone-tasks.md`** — human-readable milestone task tracker
5. **Hand ownership to the orchestrator** — later repo drift can auto-draft a new revision for reapproval, while explicit user follow-up requests are appended as auto-approved follow-up milestones

---

## Phase 3: Implement (Execution)

Implement is **not a packaged Skill**. It is driven by the scaffold's own documents (`Implement.md`, `AGENTS.md`, `CLAUDE.md`) and the Guard system.

### Execution Flow

Routes into two paths based on `plan.task_horizon` (`single_task` / `long_run`), but the core loop is the same:

```
pick task --> check scope --> enter worktree/branch --> read entrypoints
  --> implement (replacement-first) --> full review --> run validation
  --> repair if failed (max 3) --> commit --> write handoff --> update plan
  --> update milestone-tasks.md --> return to lead
```

The orchestrator owns the plan/task projection layer during execution:
- unplanned repo drift outside active task write scopes auto-bumps `plan.change_log.revision`, marks the plan `draft`, clears `approved_for_execution`, and forces reapproval
- explicit user follow-up requests written to `harnass-os/documents/intake/change-requests/current.yaml` auto-create a follow-up milestone, append new tasks, auto-approve the revision, and continue execution without rewriting committed history
- structural change requests written to `harnass-os/documents/intake/re-plan-requests/current.yaml` route back into a full re-plan lane and keep execution blocked until a new detailed plan is manually approved
- ambiguous change requests are recorded in the re-plan queue with `routing_decision: needs_human_triage` and stay in manual triage until a human resolves the route
- `milestone-tasks.md` is regenerated from the plan on every orchestrator tick instead of being manually patched

### Hybrid Intake Routing

The intake layer splits explicit user requests into two durable queues:

| Queue | Path | Purpose |
|---|---|---|
| Follow-up lane | `intake/change-requests/current.yaml` | Additive work on current product and milestone axis |
| Re-plan lane | `intake/re-plan-requests/current.yaml` | Tech stack restructures, architecture rework, major feature deletion/redo |

Routing rules:
- continue current milestone / additive feature work -> follow-up lane
- tech stack restructure / architecture rework / major feature deletion-redo -> re-plan lane
- ambiguous requests -> manual triage before routing
- re-plan revisions always require manual approval before execution resumes

### Constraint Enforcement

| Mechanism | Purpose |
|---|---|
| `agent-guard.py` | 20 guard commands (check-plan-gate, check-execution-ready, check-handoff-ready, etc.) |
| `harnass.py` | Thin CLI wrapper for `check`, `status`, `sync`, and `version` entrypoints |
| `orchestrator.py` | Tick-driven lifecycle state machine — manages plan state, drift detection, intake routing |
| Git Hooks | pre-commit (lint + plan-gate), commit-msg (task context validation), pre-push (handoff existence) |
| Worktree protocol | Write-scope isolation, one task per worktree |
| Commit policy | One task = one commit, validation must pass before commit |
| Handoff protocol | 11 required fields, push blocked until handoff exists |

### Gates

- `one-task-per-worker`
- `one-commit-per-task`
- `no-validation-no-commit`
- `plan-review-before-execution`
- `repair-before-advance`
- `no-handoff-no-next-task`
- `milestone-exit-validation-required`

---

## Phase 4: Deploy

Deploy is **not a packaged Skill**. It is driven by the scaffolded repo's `Deploy.md` runbook and `deploy/current.yaml`.

### What It Does

1. **Build** — run the build command from the plan
2. **Preview deploy** — deploy to preview/staging environment
3. **Production deploy** — deploy to production
4. **Record status** — update `deploy/current.yaml` with deployment results

### Handoff to Final Audit

When production deployment is recorded and confirmed, the system transitions to `harnass-engineer-final-audit` for post-production quality verification.

---

## Skill 3: harnass-engineer-final-audit (Post-Production Audit)

**Responsibility:** Verify production deployment quality and gate release signoff.

### Prerequisite Check

The Final Audit skill first checks whether production deployment is recorded:

| Condition | Scenario | Behavior |
|---|---|---|
| Production deployed | `production-final-audit` | Full audit workflow |
| Not yet deployed | `run-deploy-first` | Direct user to deploy first |

### Audit Flow (production-final-audit)

#### Step 1: Module Selection

Adaptively select from **15 audit modules** based on app type, stack, and detected surface:

| Category | Modules |
|---|---|
| Frontend | frontend-experience, frontend-quality, accessibility |
| Backend | backend-runtime, api-contract, frontend-backend-integration |
| Security & Content | security, content-quality, content-safety |
| SEO & Performance | seo, performance-observability |
| Release Hygiene | deploy-runtime-consistency, ci-cd-release-hygiene, documentation-signoff |
| Blockchain | blockchain-contract-audit (when blockchain tooling detected) |

Module selection uses a **dual-layer classification**:
- **from_inventory** (planning-time): app_type, ui_facing
- **from_audit_inspection** (audit-time): rendering_model, has_public_pages, has_api_routes, blockchain_tooling_detected

#### Step 2: Smoke Test

- Run smoke tests on applicable modules first (8 modules require live-path smoke checks)
- If smoke fails, skip deep audit for that module

#### Step 3: Deep Audit

- Run deep audit checks per module
- Record findings with severity (critical, high, medium, low, info)

#### Step 4: Audit Report

- Write results to `harnass-os/documents/audit/current.yaml`
- Archive to `audit/history/<audit-id>.yaml`
- Write human-readable findings to `audit/findings/<audit-id>.md`

#### Step 5: Release Decision

- **Blocking findings exist** — block release signoff, generate remediation plan, route back to planning
- **No blocking findings** — pass release signoff, update `release/current.yaml` and `status/current.yaml`

### Key Constraints

- **No waiver** — blocking findings must be fixed, cannot be waived
- **Failed audit** — flows back into a remediation planning cycle
- **All modules** — skipped modules must have documented reasons

---

## Cross-Skill Handoff Chain

```
start                          plan                              final-audit
  |                              |                                   |
  +-- scaffold-ready ----------> check-scaffold-version              |
  +-- .harnass-version.yaml ---> version handshake                   |
  +-- harnass-os/ structure ---> read-scaffold-state                 |
  |                              |                                   |
  |                        plan approved                             |
  |                        execution_ready flags --> implement       |
  |                                                    |             |
  |                                                  deploy          |
  |                                               deploy/current.yaml|
  |                                             release/current.yaml |
  |                                                    +-----------> verify-production-ready
  |                                                                  |
  |                                                            audit result
  |                                                         release signoff
```

---

## Shared Layer (documents/shared/)

Both Skills and the implicit phases share a common document set owned by `harnass-engineer-start`:

| Directory | Contents |
|---|---|
| `contracts/` | 35+ YAML schemas defining data structures, field rules, and behavioral gates |
| `templates/` | Target repo template files (42 files materialized by start) |
| `routes/` | Load order, discipline rules, and suite-level flow (`default-sequence.yaml`) — single canonical source referenced by all skills |
| `scenarios/` | Implement scenario definition |
| `validation/` | Validation profile configuration |
| `examples/` | Golden-path example |

Each Skill also has its own `documents/` directory for Skill-specific contracts and scenarios.

---

## Suite-Level Self-Improvement

The Skill suite keeps its own meta artifacts in the root `documents/` tree of this repository. These are not target-repo scaffold files.

| Artifact | Purpose |
|---|---|
| `documents/self-improvement/review-log.yaml` | Record suite-level mistakes, issues, workarounds, and review findings across `start`, `plan`, and `final-audit` |
| `documents/self-improvement/proposals/current.yaml` | Aggregate approved-for-review improvement proposals derived from the review log |
| `documents/contracts/skill-suite-review-log-schema.yaml` | Contract for the suite review log |
| `documents/contracts/skill-suite-improvement-proposal-schema.yaml` | Contract for suite improvement proposals |

Rules:

- these artifacts are `record + proposal` only
- they may recommend contract, template, or workflow changes to the Skills
- they do not auto-edit any Skill source files
- any actual Skill change still requires an explicit human-approved edit path

---

## Local Development

Install dev tooling:

```bash
python -m pip install -e .[dev]
```

Primary commands:

```bash
make lint
make test
make format
make clean
```

Windows-friendly direct equivalents:

```powershell
python -m ruff check .
python -m pytest tests -v
python -m ruff format .
python -c "from pathlib import Path; import shutil; [shutil.rmtree(path, ignore_errors=True) for path in [Path('.tmp'), Path('.pytest_cache'), Path('.ruff_cache')]]; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').rglob('__pycache__')]; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').glob('*.egg-info')]"
```

Bootstrapped target repos also expose a thin wrapper:

```bash
python harnass-os/scripts/harnass.py check list
python harnass-os/scripts/harnass.py status
python harnass-os/scripts/harnass.py sync
python harnass-os/scripts/harnass.py version
```

The hooks still call `agent-guard.py` and `orchestrator.py` directly; `harnass.py` is the human-facing entrypoint.

---

## Router System

Each Skill has a `documents/router.yaml` that controls:

1. **Scenario selection** (`pick`) — which scenario to load based on repo state
2. **Document loading** (`load`) — shared routes, contracts, and templates to load
3. **Scenario-specific contracts** (`scenarios`) — local and shared contracts per scenario
4. **Emit targets** (`emit`) — what artifacts the Skill produces

The shared `default-sequence.yaml` defines the suite-level flow and docking conventions. It is the **single canonical source** referenced by all skills — Plan and Final Audit load it via relative path from `harnass-engineer-start/documents/shared/routes/`.

---

## Design Philosophy

**"Build the stage, write the script, perform, deploy, then audit."**

- **start** builds the stage (scaffold)
- **plan** writes the script (execution plan)
- **implement** performs act by act (task-by-task execution)
- **deploy** ships to production
- **final-audit** verifies the production result

Every step has **gates** (precondition checks), **validation** (postcondition checks), and **handoff** (structured transition documents), ensuring the AI Agent works on strict rails.
