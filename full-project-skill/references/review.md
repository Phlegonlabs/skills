# Phase 2.5: Multi-Agent Documentation Review

After generating all documents, launch a **multi-agent review team** to validate the documentation
quality, consistency, and completeness before handing off to the user.
If your environment supports spawning parallel reviewers/agents, use it — otherwise run the same checklists sequentially.

Use the **complexity tier** assigned during Phase 1 (see SKILL.md) to determine review scope:

- **Standard**: spawn Agent 2 + Agent 3, then run Codex review.
- **Complex**: spawn Agent 1 + Agent 2 + Agent 3, then run Codex review, then post-Codex re-review with Agent 2 + Agent 3, then run a second-pass recheck with Agent 2 + Agent 3 after fixes.

Use the agent definitions below as the review pool.

## Agent 1 — Architecture & Spec Reviewer
- Read `docs/architecture.md` and `docs/design.md` end-to-end
- Check:
  - [ ] Every user role from the interview is documented with permissions
  - [ ] Every user journey is complete (entry → core action → goal), no missing steps
  - [ ] (GUI) Every page/screen has purpose, a low-fidelity wireframe/frame sketch, an exhaustive component tree/inventory, user actions, and responsive behavior
  - [ ] (CLI) Command tree is documented with all subcommands, flags, argument types, exit codes, and pipe support
  - [ ] Every core feature has a detailed spec section with edge cases
  - [ ] Technical architecture (tech stack, data model, API design, integrations) is consistent with interview answers
  - [ ] If third-party integrations exist, Integrations section includes Context7 API documentation rule
  - [ ] If analytics/tracking is in scope (e.g., GA4/GTM), Integrations documents provider, consent strategy, and a no-PII rule
  - [ ] `docs/design.md` includes a complete design system (color, typography, spacing, component variants/sizes/states)
  - [ ] `docs/design.md` includes page-level design coverage for each in-scope page/screen (layout, interactions, state changes, ASCII wireframe)
  - [ ] `docs/design.md` is consistent with architecture.md user journeys, features, and UI approach
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
  - [ ] Milestones are ordered logically (scaffold → core features → integrations → polish → **Production Readiness Gate**)
  - [ ] Each milestone has: scope, sub-tasks, key files/modules, acceptance criteria, verification commands
  - [ ] Each milestone has 3-8 numbered sub-tasks, each describing ONE atomic action
  - [ ] Sub-tasks follow a logical implementation order within each milestone
  - [ ] Acceptance criteria are concrete and testable (not vague like "works correctly")
  - [ ] Verification commands are real and runnable for the chosen tech stack
  - [ ] CLI Foundation milestone (CC) is Milestone 02, right after repo scaffold (CLI projects only)
  - [ ] If analytics/tracking is in scope (e.g., GA4/GTM), there is at least one milestone covering instrumentation + consent + verification
  - [ ] Milestones with non-obvious implementation choices include trade-offs considered
  - [ ] No feature is left uncovered by milestones
  - [ ] **Production Readiness Gate (Milestone PR) exists as the FINAL milestone** with comprehensive audit sub-tasks (including PR.11 dependency audit, PR.12 a11y check if GUI, PR.13 license audit)
  - [ ] Risk register has at least 2 realistic entries (not placeholder text)
- Report: list any missing features, vague criteria, or ordering issues

## Agent 3 — Execution Rules & Cross-doc Consistency Reviewer
- Read ALL docs: `docs/implement.md`, `docs/secrets.md`, `docs/documentation.md`, `CLAUDE.md`, `AGENTS.md`
- Cross-reference with `docs/plans.md` and `docs/architecture.md`
- Check:
  - [ ] implement.md completion criteria match the actual doc set generated
  - [ ] implement.md completion criteria include **Production Readiness Gate** as a mandatory final check
  - [ ] implement.md verification commands match the tech stack
  - [ ] implement.md git strategy matches the workflow chosen in the interview (trunk-based vs branches)
  - [ ] implement.md includes "Production mindset from Day 1" rule and post-milestone production spot-check
  - [ ] implement.md includes Context7 MCP rule for third-party API documentation
  - [ ] documentation.md milestone list matches plans.md milestones
  - [ ] documentation.md setup commands match the tech stack
  - [ ] CLAUDE.md and AGENTS.md are consistent on core docs/commands, while keeping role-specific differences
  - [ ] CLAUDE.md Execution Protocol lists all docs in correct order
  - [ ] CLAUDE.md Key Docs section matches actual generated files
  - [ ] CLAUDE.md commands are accurate for the chosen package manager and framework
  - [ ] If CLI: implement.md has CLI-specific rules (exit codes, help, stdout/stderr, NO_COLOR)
  - [ ] If CLI: implement.md completion criteria include CLI standards checklist
  - [ ] If analytics/tracking is in scope: implement.md has analytics rules and docs/plans/doc setup remain consistent
  - [ ] If secrets/API keys are in scope: docs/secrets.md guidance is present and consistent (no secret leaks; safe output/display; show-once + hashed storage if issuing API keys)
  - [ ] implement.md contains Immutable/Mutable Layer declaration
  - [ ] implement.md contains Code Quality Red Lines table
  - [ ] implement.md contains Session Handoff Protocol
  - [ ] implement.md contains TDD/BDD Workflow guidance
  - [ ] CLAUDE.md contains AI Behavior Rules section
  - [ ] CLAUDE.md contains Lessons & Prevention Rules section
  - [ ] CLAUDE.md contains STATUS Response Contract block
  - [ ] Task tracking files (`tasks/todo.md`, `tasks/lessons.md`) are referenced consistently where required
- Report: list any cross-doc contradictions, missing references, or broken commands

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
4. **Complex tier only**: run post-Codex re-review with **Agent 2 + Agent 3**.
   **Standard tier** can proceed directly to Phase 2.7 after Codex findings are applied.
5. If `mcp__codex__codex` is unavailable, do not skip silently. Ask the user to choose one explicit alternative:
   - **Option A (manual checklist path)**: run the same review scope with the documented checklists
     sequentially (including tier-specific reviewers), and require zero unresolved critical issues.
   - **Option B (alternate model path)**: run an equivalent independent review using another available
     model/tool with the same prompt scope, then apply and summarize findings.
   Record which alternative path was used.
