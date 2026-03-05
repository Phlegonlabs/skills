---

## Convert/Upgrade Mode Interview

This protocol is used when onboarding an existing codebase into this skill's structured workflow
(Convert/Upgrade mode). It assumes Convert Phase 1 discovery has already produced a baseline snapshot.

Both conversion profiles share Step 1 (Current-state confirmation) and Step 3 (Synthesis), but use
different round sets in Step 2.

### Step 1 — Current-State Confirmation

Before asking new questions, present the discovered baseline from Convert Phase 1:
1. code structure and runtime surface
2. current feature boundaries
3. detected command/test/deploy shape
4. missing docs + hook/HK assets

Ask the user to confirm or correct this baseline. Do not proceed until baseline is aligned.

### Step 2 — Clarifying Questions

Ask only conversion-relevant questions. This is not a full greenfield interview.

---

#### Baseline Conversion Rounds (CV0-CV3, use 2-4)

**Round CV0 — Documentation scope lock**: Which areas should be captured now vs deferred?
Confirm the minimum required fidelity for `docs/architecture.md` and `docs/plans.md`.

**Round CV1 — Architecture mapping fidelity**: For each major module, should docs reflect
exact current behavior or normalize naming/structure for clarity?

**Round CV2 — Operations baseline**: What are the canonical build/test/run commands today?
Which secrets/integrations must be documented immediately in `docs/secrets.md`?

**Round CV3 — Stabilization priorities**: Which known risks or inconsistencies should become
immediate milestones before Production Readiness Gate?

Follow-up cap: 6.

---

#### Upgrade Conversion Rounds (CU1-CU4, use 3-6, include CV0)

**Round CU1 — Upgrade objectives**: What should improve during conversion (architecture,
module boundaries, test coverage, delivery workflow), and what must remain unchanged now?

**Round CU2 — Compatibility & migration**: Do upgrade goals require migration, deprecation,
or compatibility windows? Define rollback expectations.

**Round CU3 — Sequencing strategy**: Separate "capture current reality" milestones from
"upgrade/optimization" milestones so execution can stay safe and incremental.

**Round CU4 — Quality gate deltas**: What additional production-readiness checks are needed
because of the upgrade scope (performance, observability, security, release safety)?

Follow-up cap: 10.

---

#### Shared rules for both conversion profiles:
- Anchor every question to discovered code reality, not assumptions
- Ask 1-2 focused questions per round
- Skip non-applicable rounds
- Before leaving Step 2, ask a final confirmation question in the user's language
