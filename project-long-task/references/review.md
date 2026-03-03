# Phase 2.5: Multi-Agent Documentation Review

After generating all documents, launch a **multi-agent review team** to validate the documentation
quality, consistency, and completeness before handing off to the user. Use the `Agent` tool to spawn
reviewers in parallel — each agent reviews from a different perspective.

Determine project complexity first, then spawn reviewers in parallel using the tiers below:

- **Lite tier** (simple/small scope): spawn Agent 1 + Agent 2 + Agent 3.
- **Standard tier** (most projects): spawn Agent 1 + Agent 2 + Agent 3.
- **Complex tier** (multi-role, multi-platform, integration-heavy): spawn Agent 1 + Agent 2 + Agent 3, then run a quick second-pass recheck with Agent 2 + Agent 3 after fixes.

Use the agent definitions below as the review pool.

## Agent 1 — Architecture & Spec Reviewer
- Read `docs/architecture.md` end-to-end
- Check:
  - [ ] Every user role from the interview is documented with permissions
  - [ ] Every user journey is complete (entry → core action → goal), no missing steps
  - [ ] Every page/screen has purpose, components, user actions, and responsive behavior
  - [ ] Every core feature has a detailed spec section with edge cases
  - [ ] Technical architecture (tech stack, data model, API design, integrations) is consistent with interview answers
  - [ ] Directory structure is realistic and matches the chosen framework conventions
  - [ ] Hard requirements section captures all constraints mentioned
  - [ ] Deliverable section lists all output docs
- Report: list any gaps, contradictions, or vague sections that need improvement

## Agent 2 — Plans & Milestones Reviewer
- Read `docs/plans.md` end-to-end
- Cross-reference with `docs/architecture.md` features
- Check:
  - [ ] Project metadata (platform, tech stack, UI framework, deployment) is accurate
  - [ ] Every feature in architecture.md maps to at least one milestone
  - [ ] Milestones are ordered logically (scaffold → core features → integrations → polish)
  - [ ] Each milestone has: scope, sub-tasks, key files/modules, acceptance criteria, verification commands
  - [ ] Each milestone has 3-8 numbered sub-tasks, each describing ONE atomic action
  - [ ] Sub-tasks follow a logical implementation order within each milestone
  - [ ] Acceptance criteria are concrete and testable (not vague like "works correctly")
  - [ ] Verification commands are real and runnable for the chosen tech stack
  - [ ] CLI Foundation milestone (CC) is Milestone 02, right after repo scaffold (CLI projects only)
  - [ ] No feature is left uncovered by milestones
  - [ ] Risk register has realistic entries
- Report: list any missing features, vague criteria, or ordering issues

## Agent 3 — Execution Rules & Cross-doc Consistency Reviewer
- Read ALL docs: `docs/implement.md`, `docs/documentation.md`, `CLAUDE.md`, `AGENT.md`
- Cross-reference with `docs/plans.md` and `docs/architecture.md`
- Check:
  - [ ] implement.md completion criteria match the actual doc set generated
  - [ ] implement.md verification commands match the tech stack
  - [ ] implement.md git strategy (work on main) is present
  - [ ] documentation.md milestone list matches plans.md milestones
  - [ ] documentation.md setup commands match the tech stack
  - [ ] CLAUDE.md and AGENT.md are identical
  - [ ] CLAUDE.md Execution Protocol lists all docs in correct order
  - [ ] CLAUDE.md Key Docs section matches actual generated files
  - [ ] CLAUDE.md commands are accurate for the chosen package manager and framework
  - [ ] If CLI: implement.md has CLI-specific rules (exit codes, help, stdout/stderr, NO_COLOR)
  - [ ] If CLI: implement.md completion criteria include CLI standards checklist
- Report: list any cross-doc contradictions, missing references, or broken commands

## After Review

**After all agents complete**, collect their reports and:
1. **Fix all issues** found by the reviewers — edit the docs directly
2. If fixes are significant (e.g., missing features, restructured milestones), briefly inform the user what was corrected
3. If no issues found, proceed silently

This review ensures the documentation is production-quality before the user starts implementation.
