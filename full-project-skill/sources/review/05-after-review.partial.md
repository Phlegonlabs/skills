## After Review

**After all agents complete**, collect their reports and:
1. **Fix all issues** found by the reviewers — edit the docs directly
2. If fixes are significant (e.g., missing features, restructured milestones), briefly inform the user what was corrected
3. If no issues found, proceed silently

This review ensures the documentation is production-quality before the user starts implementation.

## Phase 2.6 — Cross-Model Review Protocol (Mandatory)

After Phase 2.5 issues are fixed:
1. Send the full `docs/architecture.md` + `docs/plans.md` content to `mcp__codex__codex`.
2. Ask for an independent review focused on architectural gaps, edge cases, and milestone realism.
3. Apply valid findings.
4. **Complex tier only**: run **exactly one** post-Codex re-review with **Agent 2 + Agent 3**, then apply valid findings.
   **Standard tier** can proceed directly to Phase 2.7 after Codex findings are applied.
5. If `mcp__codex__codex` is unavailable, do not skip silently. Ask the user to choose one explicit alternative:
   - **Option A (manual checklist path)**: run the same review scope with the documented checklists
     sequentially (including tier-specific reviewers), and require zero unresolved critical issues.
   - **Option B (alternate model path)**: run an equivalent independent review using another available
      model/tool with the same prompt scope, then apply and summarize findings.
   Record which alternative path was used.
