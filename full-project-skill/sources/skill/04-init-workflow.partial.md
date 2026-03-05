## Workflow

### Phase 1: Interactive Interview

Collect project information through an interactive conversation. See `references/interview.md` for the full
interview protocol including all rounds, follow-up triggers, and examples.

**Steps overview:**
1. **Project Name** — Ask the user for the project name
2. **Project Goals** — Free-form description of what they're building, the problem, and target users
3. **Market Research Snapshot** — Run one focused market scan before deep scoping: identify similar products,
   open-source analogs, and reference implementations/patterns worth borrowing or avoiding.
4. **Project Intro & Core Flow Draft** — Based on goals + market scan, draft a sharper project introduction
   (problem, target users, positioning) and a candidate end-to-end flow. Confirm this draft with the user.
5. **Design Direction (Step 2.8: Product Architecture + Visual Style)** — Based on the market scan + project intro/core
   flow draft, propose 3-4 product architecture directions and corresponding visual style directions.
   User must choose/confirm one direction before moving on.
6. **Clarifying Questions** — AI-driven discovery interview (rounds and depth determined by complexity tier,
   covering user journeys, components, tech stack finalization, UI/CLI preferences, and deployment).
   Adaptive follow-ups for ambiguities. Tech stack is locked during this step (Round R10.7).
   Use `references/tech-components.md` for category-based stack options and `assets/versions.json`
   for version guidance during lock-in.
7. **Tier Recheck** — After all interview rounds, reassess tier based on what was discovered. If the project
   turned out more complex than initially assessed, upgrade the tier and announce the change to the user.
8. **Synthesis & Confirmation** — Present a complete project summary for user approval before generating docs

### Phase 2: Generate Documentation

After confirmation, create the `docs/` directory and generate all documents. See `references/templates.md`
for the full templates and structure of each file.

**Documents generated:**
- `docs/architecture.md` — Single source of truth: project background, user journeys, components, product spec, technical architecture
- `docs/plans.md` — Execution plan with milestones, sub-tasks, acceptance criteria, verification commands
- `docs/implement.md` — Non-negotiable execution rules for disciplined autonomous work
- `docs/secrets.md` — Secrets & API keys guidance (env vars + safe key handling)
- `docs/documentation.md` — User-facing documentation, kept in sync with reality
- `docs/design.md` — Design system and page-level design spec
- `docs/decisions.md` — Architecture Decision Records (Standard/Complex tier only)
- `tasks/todo.md` — Execution-time sub-task tracker (Current Sprint / Review / Blocked / Completed)
- `tasks/lessons.md` — Correction-derived prevention rules
- `CLAUDE.md` + `AGENTS.md` — Quick-reference files for AI coding tools (same project facts, different operating focus)

### Phase 2.5: Multi-Agent Documentation Review

Launch a multi-agent review team to validate documentation quality, consistency, and completeness.
See `references/review.md` for the full review protocol and agent definitions.
If multi-agent spawning isn't available in your environment, run the same checklists sequentially as a self-review.

**Review agents by tier:**
- **Standard**: Agent 2 + Agent 3, then Codex review.
- **Complex**: Agent 1 + Agent 2 + Agent 3, then Codex review, then Agent 2 + Agent 3 post-Codex re-review, then a second-pass recheck after fixes.

Fix all issues found, then proceed.

### Phase 2.6: Cross-Model Review (Mandatory)

Cross-model review is mandatory and must run via `mcp__codex__codex`.

**Protocol:**
1. Prepare a prompt that includes the full `docs/architecture.md` and `docs/plans.md` content.
2. Send that prompt to `mcp__codex__codex` for an independent review.
3. Ask Codex to focus on: architectural gaps, missing edge cases, unrealistic milestones, and
   cross-doc inconsistencies.
4. Fix all valid findings from Codex.
5. **Complex tier only**: after fixes, run **Agent 2 + Agent 3** again (post-Codex re-review) before proceeding.
   **Standard tier** can proceed directly to Phase 2.7 after Codex findings are applied.
6. Record in output that Phase 2.6 was executed and summarize what was fixed.

If `mcp__codex__codex` is unavailable, do NOT skip silently. Ask the user to either install/enable it
or choose one explicit alternative path:
- **Option A (manual checklist path)**: run the same tier-scoped review checklists sequentially and
  require zero unresolved critical issues.
- **Option B (alternate model path)**: use another available model/tool for an equivalent independent review,
  then apply and summarize findings.
Record which path was used before continuing.

### Phase 2.7: User Annotation Review

After Phase 2.5 and Phase 2.6, present the generated documents to the user for a lightweight annotation pass:

1. Tell the user: "The docs are ready for your review. Please read through `docs/architecture.md`
   and `docs/plans.md`. For anything that needs changes, add inline notes directly in the file
   (e.g., `<!-- NOTE: should use WebSocket not polling -->` or plain-text comments next to the
   relevant section). Then come back and say 'address all notes.'"

2. When the user returns with annotated files:
   - Read the annotated files and identify all user notes/comments
   - Address each note: modify the document to incorporate the feedback
   - Remove the resolved note markers
   - Present a summary of changes made

3. Default expectation: one review pass is usually enough. If the user adds new notes, run another pass
   and resolve them.

4. **Guard**: Do NOT proceed to Phase 3 until the user explicitly says the docs are ready.
   If the user starts describing new features, treat it as additional input and continue
   the annotation cycle, not as a signal to move forward.

This step turns generated docs into a **shared mutable workspace** between user and AI while keeping
the workflow lightweight.

### Phase 3: Next Steps

After review, tell the user:
1. The docs are ready at `docs/`
2. Suggest they review `docs/architecture.md` and `docs/plans.md`
3. Explain they can start execution by feeding `docs/implement.md` as instructions
4. Mention they can adjust milestone count/scope in `docs/plans.md` before starting
5. **Emphasize**: The final milestone is a **Production Readiness Gate** — the project is NOT considered
   complete until it passes all production-readiness checks. Every milestone builds toward a production-grade
   deliverable, not a demo or prototype.
6. **Claude Code Hooks** (mandatory): Hooks MUST be installed.
   See `## Hooks` below for compatibility and installation details.
