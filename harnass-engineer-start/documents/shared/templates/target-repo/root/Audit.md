# Final Audit Route

## audit_gate
- Run only after production deployment is recorded.
- Do not waive final-audit failures.

## module_selection
- Select audit modules adaptively from repo shape, deployed surface, and detected stack.
- Include frontend, backend, integration, security, content, SEO, runtime, release hygiene, and blockchain contract audit when applicable.

## smoke_first_rule
- Run smoke checks before deep audit for modules that require live-path validation.
- Record smoke failures explicitly in `harnass-os/documents/audit/current.yaml`.
- For UI projects, capture browser evidence in `harnass-os/documents/audit/browser/current.yaml` before release signoff.
- Keep `harnass-os/documents/orchestrator/current.yaml current_audit_module` pointed at the module being audited.

## release_signoff
- Write current audit state to `harnass-os/documents/audit/current.yaml`.
- Treat missing or failed browser audit evidence as a blocking release failure for UI projects.
- Archive each completed audit to `harnass-os/documents/audit/history/<audit-id>.yaml`.
- Write the human-readable report to `harnass-os/documents/audit/findings/<audit-id>.md`.
- Only mark `harnass-os/documents/release/current.yaml` as `complete` when the final audit passes with no blocking findings.

## remediation_route
- If the audit fails, set `follow_up_required: true`.
- Route the repo into a new remediation plan instead of waiving or silently closing the release.
- Run `python harnass-os/scripts/orchestrator.py tick` after each module result so the lifecycle can advance to the next module or block on remediation.
