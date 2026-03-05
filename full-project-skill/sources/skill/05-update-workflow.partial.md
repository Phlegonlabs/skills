---

## Update Mode (modifying an existing project)

When mode detection determines **Update mode**, follow this lighter workflow instead of the full Init flow.
See `references/interview.md` § "Update Mode Interview" for the full protocol.

### Update Phase 1: Context Loading

1. Read core docs required for Update mode: `docs/architecture.md`, `docs/plans.md`
2. Load supporting docs: `docs/implement.md`, `docs/secrets.md`, `docs/documentation.md`, `docs/design.md`.
   If any are missing (legacy project), **auto-create** them from current templates before continuing.
   Record which docs were auto-created in the update summary.
3. Identify: current milestone progress, existing features, tech stack, established patterns
4. Briefly summarize the project's current state to the user to confirm alignment
5. **Codebase Pattern Scan** (if source code exists): Before the interview, scan the existing
   source directory to verify docs–code alignment:

   **Scan strategy:**
   1. Discover code roots in this order: `src/`, `app/`, `apps/*/src`, `apps/*/app`, `packages/*/src`, `packages/*/app`, `services/*/src`.
      Scan every root that exists (single-app and monorepo layouts).
   2. Compare against the Directory Structure section in `docs/architecture.md`
   3. Grep for key patterns: route definitions, component naming conventions, API endpoint formats
   4. If >3 divergences are found, summarize them (with concrete path examples) and ask the user:
      "I found these divergences between docs and code: [list]. Should we plan against the
      **code** (update docs to match) or the **docs** (treat code as drifted)?"

   If fewer divergences are found, note them but proceed without blocking.
   This is read-only — do not modify anything.

### Update Phase 1.5: Update Type Classification

Ask the user what kind of change they're making, or infer from their description:

| Type | When | Interview Rounds | Follow-up Cap |
|------|------|-----------------|---------------|
| **New Feature** | Adding new functionality to the project | 3-8 rounds (F0-F8 + F4.5, F0 optional) | 8-15 |
| **Bug Fix** | Fixing a bug that may change behavior, architecture, or require doc updates | 1-3 rounds (B1-B3) | 5 |
| **Change** | Requirement changes, refactors, tech migrations, removing features | 2-5 rounds (C1-C5) | 8 |

Announce the classified type to the user and let them override.

**Type reclassification**: If during the interview the actual scope significantly exceeds the classified type
(e.g., a Bug Fix turns out to require architectural changes, or a Change reveals new feature needs),
re-classify the update type, announce the reclassification to the user, and adjust the remaining
interview rounds accordingly.

### Update Phase 2: Update Interview

A focused interview scoped to the change (NOT a full project interview). See `references/interview.md` for
the full protocol for each update type.

**Steps overview:**
1. **Description** — Ask the user to describe the change in their own words
2. **Clarifying Questions** — Rounds and depth determined by update type (see table above)
3. **Synthesis & Confirmation** — Present a change summary for user approval

### Update Phase 3: Update Documentation

After confirmation, **update** (not recreate) the existing documents. What to update depends on the type:

**All types:**
- `docs/plans.md` — Insert new milestones **before the Production Readiness Gate (Milestone PR)**, not after it.
  The PR milestone must always remain the final milestone. For Bug Fix, add a fix milestone before PR.
  Follow the same milestone format. Keep existing milestones intact. Update Milestone PR sub-tasks if
  the change introduces new production-readiness requirements.
- `docs/documentation.md` — Add new milestones to the status section
- If any supporting docs were missing in Phase 1, create them first from current templates, then apply update edits.

**New Feature:**
- `docs/architecture.md` — Append new user journeys, pages, components, and product spec sections.
  Update technical architecture if the feature introduces new patterns or integrations.
- `docs/design.md` — Add design-system updates and page-level design for new pages/components/interactions
- `docs/secrets.md` — Update if the feature introduces new secrets or integrations
- `CLAUDE.md` + `AGENTS.md` — Update if new commands, structure, or conventions are introduced

**Bug Fix:**
- `docs/architecture.md` — Update only if the fix changes documented behavior or reveals a spec gap.
  Add a note in the relevant product spec section describing the corrected behavior.
- `docs/plans.md` — Record the bug in Implementation Notes

**Change:**
- `docs/architecture.md` — Modify affected sections (user journeys, components, tech architecture, etc.).
  Mark removed or replaced content clearly — do not silently delete.
- `docs/design.md` — Update all affected design sections (system tokens, component variants, page layouts/states)
- `docs/secrets.md` — Update if integrations or secrets change
- `CLAUDE.md` + `AGENTS.md` — Update if commands, structure, or conventions change
- `docs/implement.md` — Update only if the change alters execution rules (e.g., new tech stack, new workflow)

**Do NOT modify:**
- Existing completed milestone content (unless fixing a discovered inconsistency)
- `docs/implement.md` (unless the change genuinely requires new execution rules)

### Update Phase 3.5: Documentation Review

Run a lighter review focused on the changes. See `references/review.md` for full checklist details.

Use Agent 2 (Plans reviewer) + Agent 3 (Consistency reviewer). Skip Agent 1 unless the change adds
entirely new user roles or major architectural changes.

Focus areas:
- Agent 2: Verify new/modified milestones cover all aspects of the change; new milestones are inserted
  before Milestone PR; milestone ordering is logical
- Agent 3: Verify no contradictions between new and existing content; updated architecture sections are
  consistent; CLAUDE.md/AGENTS.md are updated if needed

**Cross-Model Review (Mandatory):**
After Agent 2+3 review, run `mcp__codex__codex` on the modified sections (or full updated docs when needed),
focused on: consistency with existing content, missed edge cases, and milestone coverage gaps.
After applying valid Codex findings, run **exactly one** post-Codex re-review with **Agent 2 + Agent 3**.
If `mcp__codex__codex` is unavailable, stop and ask the user to install/enable it or choose one explicit
alternative path:
- **Option A (manual checklist path)**: run Agent 2 + Agent 3 checklists end-to-end on the updated docs,
  and require zero unresolved critical issues.
- **Option B (alternate model path)**: run an equivalent independent review using another available model/tool,
  then apply and summarize findings.
Record which path was used before continuing.

### Update Phase 3.7: User Annotation Review

After the documentation review, present the updated documents to the user for a **lightweight
annotation cycle** (mirrors Init Phase 2.7 but scoped to changes):

1. Tell the user: "The docs have been updated. Please review the modified sections in
   `docs/architecture.md` and `docs/plans.md`. Add inline notes for anything that needs changes
   (e.g., `<!-- NOTE: ... -->`), then say 'address all notes.'"

2. When the user returns with annotated files:
   - Identify all user notes/comments in the modified sections
   - Address each note and remove the resolved markers
   - Present a summary of changes made

3. **1 round is sufficient** — unlike Init's multi-round cycle, Update mode only needs one
   annotation pass. If the user provides additional feedback, address it, but do not loop
   indefinitely.

4. **Type-based skip rule**: Bug Fix updates may skip this phase if the fix is straightforward
   and does not alter documented behavior. New Feature and Change types should always run this phase.

### Update Phase 4: Next Steps

Tell the user:
1. The docs have been updated
2. Summarize what was changed (new/modified milestones, updated architecture sections, etc.)
3. Suggest they review the changes in `docs/architecture.md` and `docs/plans.md`
4. Mention they can adjust the new milestones before starting execution
5. **Remind**: New milestones follow the same production-quality standard — every sub-task produces
   deployment-ready code. If the update adds significant new functionality, ensure the Production
   Readiness Gate milestone is updated to cover the new scope.
