---
name: harnass-engineer-final-audit
description: Run a post-production final audit across frontend, backend, integration, security, content quality, SEO, runtime, release hygiene, and blockchain contracts when present. Use when Codex needs to verify release readiness for final signoff after production deployment, write final audit artifacts, block closeout on unresolved findings, or route failed audits into remediation planning.
docking:
  phase: final-audit
  entry_condition: production deployment is recorded and final signoff is pending
  reads:
    - harnass-os/Audit.md
    - harnass-os/documents/audit/current.yaml
    - harnass-os/documents/release/current.yaml
    - harnass-os/documents/deploy/current.yaml
    - harnass-os/documents/inventory/current-state.yaml
    - harnass-os/documents/status/current.yaml
    - harnass-os/documents/orchestrator/current.yaml
  writes:
    - harnass-os/documents/audit/current.yaml
    - harnass-os/documents/audit/history/<audit-id>.yaml
    - harnass-os/documents/audit/findings/<audit-id>.md
    - harnass-os/documents/release/current.yaml
    - harnass-os/documents/status/current.yaml
  requires_phase: deploy
  emits_to_phase: null
---

# Harnass Engineer Final Audit

Read [documents/router.yaml](./documents/router.yaml).

Audit only after production deployment is recorded. Write audit artifacts, block release signoff on blocking findings, and send failures into a new remediation plan instead of waiving them.

Do:
- confirm production deployment completed before auditing
- read `harnass-os/Audit.md`, `harnass-os/documents/audit/current.yaml`, `harnass-os/documents/release/current.yaml`, `harnass-os/documents/deploy/current.yaml`, `harnass-os/documents/inventory/current-state.yaml`, and repo reality
- select audit modules adaptively from repo shape, deployed surface, and detected stack
- run module-specific smoke checks before deep audit where required
- audit frontend, backend, API integration, security, content, SEO, deploy/runtime consistency, CI/CD hygiene, documentation signoff, and blockchain contracts when present
- detect blockchain stacks from repo files and audit contract logic and security risk when present
- write machine-readable audit state, append audit history, and write a human-readable findings report
- block release signoff until all blocking findings are cleared
- require a new remediation plan when the audit fails

Do not:
- waive final-audit failures
- mark a release complete before the final audit passes
- skip smoke checks for modules that require them
- silently ignore missing blockchain test or simulation commands when a blockchain module is detected

Gates:
- production deploy must be recorded before final audit starts
- run module-specific smoke checks before deep audit where required
- do not waive final-audit blocking findings
- do not mark release complete before final audit passes
- failed audits must route into remediation planning

Read [references/modules.md](./references/modules.md) when you need the adaptive module rules, smoke policy, or blockchain detection details.
