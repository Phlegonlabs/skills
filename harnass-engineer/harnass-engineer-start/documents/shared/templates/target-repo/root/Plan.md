# Planning Route

## Bootstrap Gate
- Confirm the target repo scaffold is present before discovery.
- If root runbooks, route stack, state stack, or guard stack are missing, bootstrap first.

## Intake Route
- Read `harnass-os/documents/intake/request.yaml`.
- Confirm the user goal, requested changes, constraints, and initial horizon.

## Discovery Route
- Inspect repo reality before asking the user.
- Write findings to `harnass-os/documents/inventory/current-state.yaml`.
- Capture entrypoints, package manager commands, build/test commands, and deploy-relevant command facts during discovery.
- Run web search to validate detected tech stack against current market reality and record results in `market_context`.

## Question Route
- Ask only unresolved product, UX, architecture, data, integration, or rollout questions.
- Keep the question set to the minimum unblocking set.

## Frontend Design Skill Route
- For UI-facing work, call the external `frontend-design` skill during planning.
- Use repo intake, inventory, and design-system facts as the skill input.
- If `frontend-design` is unavailable, stop UI-facing planning and surface it as a blocking issue.

## Design Docs Route
- Create `harnass-os/documents/design/wireframe.md` and `harnass-os/documents/design/design.md` during planning.
- Treat them as required inputs for later UI execution.

## Design Validation
- For UI-facing work, define how the design is validated before implementation approval.
- Write or update `harnass-os/documents/validation/design-review.yaml` with refs to the wireframe and design docs, plus `scenarios`, `states_checked`, `breakpoints_checked`, findings, and decision.

## Decision Route
- Write or update `harnass-os/documents/decisions/index.yaml` when a major UI, architecture, runtime, or release decision is made.
- Create an ADR from `harnass-os/documents/decisions/adr-template.md` when the decision is durable and non-trivial.

## Plan Output
- Write the reviewed machine-readable plan to `harnass-os/documents/plans/<slug>.yaml`.
- Attach top-level design/runtime/release/decision refs when they apply.
- Attach milestones, atomic tasks, read scopes, entrypoints, implementation steps, validation commands, commit rules, and handoff outputs.
- Refresh `harnass-os/documents/orchestrator/current.yaml` after draft creation, major scope changes, and plan approval.

## Deployment Route
- Define preview, production, smoke, and rollback flow in `harnass-os/documents/deploy/current.yaml`.
- When the deployment surface is Cloudflare, record runtime details in `harnass-os/documents/runtime/<provider>.yaml` and release gating in `harnass-os/documents/release/current.yaml` before execution approval.
- Prefer real project commands over placeholders whenever discovery can identify them.

## Final Audit Route
- For release-affecting work, require a post-production final audit before release signoff.
- Seed `harnass-os/documents/audit/current.yaml` and keep `release.current.final_audit_ref` pointed at it.
- When the repo is UI-facing, include SEO, content quality, content safety, and accessibility in the expected audit scope.
- When the repo includes blockchain contracts, require contract smoke coverage and logic/security review.

## Review Gate
- Self-review before approval.
- Clear blocking findings before setting `status: approved`.
- When the plan becomes approved, the orchestrator should transition the repo toward `IMPLEMENTING`.

## Long-Run State
- Seed `harnass-os/documents/runs/current.yaml` and `harnass-os/documents/status/current.yaml` for long-run work.
- Update both ledgers when milestone or task state changes.

