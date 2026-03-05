### Step 3 — Convert Synthesis & Confirmation

Synthesize the conversion plan and present it to the user for explicit confirmation.

**For Baseline Conversion:**
1. **Current-state snapshot** — concise architecture + behavior summary
2. **Documentation scope** — what will be captured now
3. **Gap list** — missing docs/hooks/HK assets to bootstrap
4. **Conversion milestones** — baseline capture + stabilization milestones
5. **Out of scope** — upgrades intentionally deferred

**For Upgrade Conversion:**
1. **Current-state snapshot** — baseline and key constraints
2. **Upgrade objectives** — what will improve during/after conversion
3. **Migration & compatibility plan** — risk controls and rollback posture
4. **Milestone split** — capture milestones vs upgrade milestones
5. **Production impact notes** — quality-gate changes required by upgrades

Ask the user to confirm or adjust before generating docs.

**Guard**: After presenting synthesis, STOP. Do not generate docs until explicit confirmation.
If the user adds new requirements, fold them into interview adjustments first.
