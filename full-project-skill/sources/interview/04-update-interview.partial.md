---

## Update Mode Interview

This protocol is used when modifying an existing project (Update mode).
It assumes all existing docs have been read in Update Phase 1.

All three update types share the same Step 1 (Description) and Step 3 (Synthesis), but have
different clarifying question rounds in Step 2.

### Step 1 — Description (Free-form)

Ask the user to describe the change in their own words. Same principle as Init Step 2: capture
intent before structured breakdown.

Example questions by type:
- New Feature: "Describe the feature you want to add — what does it do and why do you need it?"
- Bug Fix: "Describe the bug — what's the expected behavior vs. actual behavior? How is it reproduced?"
- Change: "Describe what you want to change — what's the current state and what should it become?"

Let the user write freely. Do NOT interrupt with follow-up questions mid-description.

### Step 2 — Clarifying Questions

Based on the description and existing project context, ask targeted questions.
This is NOT a full project interview — focus only on what's new or changing.

---

#### New Feature Rounds (F0-F8 + F4.5, use 3-8 depending on complexity)

**Round F0 — Quick reference scan** (optional, for significant features):
Before deep scoping, run a lightweight competitive scan for the new feature — 2-3 reference
implementations of similar functionality in comparable products. Reuse the format from Init
Step 2.5 but with a narrower scope:
1. **Reference implementations (2-3)**: Name + how they implement this specific feature
2. **Patterns to borrow or avoid**: What works well, what doesn't
3. **Differentiation angle**: How this project's version should differ

Trigger condition: only when the feature is significant enough to span >2 milestones.
For smaller features, skip F0 and start at F1.
If web browsing is unavailable, use this fallback ladder:
1. Ask the user for known reference implementations.
2. Add only high-confidence generic patterns (no fabricated links/metrics).
3. Mark findings as best-effort inference with caveats.
4. Flag reference validation as required when browsing/tools become available.

**Round F1 — User journey impact**: Which existing user journeys are affected? Are there new journeys?
Walk through the feature from the user's perspective step by step.

**Round F2 — Pages & components**: Does this feature need new pages/screens? Which existing pages
are modified? What new components are needed? What existing components need changes?
If the feature has UI, ask for visual references (screenshots, mockups, sketches) as in Round R11.
If the feature introduces new UI components, also ask:
- Should new components be added to the Component Inventory section in `docs/design.md`?
- Does the Living Design Guide page (if one exists) need to be updated with the new components?
- Do any new composition patterns or interactive patterns need to be documented?

**Round F3 — Data & API changes**: Does this feature require new data models, new API endpoints,
or changes to existing ones? How does it interact with the current data model?

**Round F4 — Edge cases & constraints**: Error states, permissions, validation rules, performance
concerns. What happens when things go wrong?

**Round F4.5 — Testing requirements**: Does this feature require new unit / integration / E2E tests?
Are existing tests affected? Any testing-specific constraints (mock APIs, test data setup)?

Round counting rule:
- F0 is optional (significant features only).
- F4.5 is conditional (include when testing impact is non-trivial).
- F6-F8 are depth rounds for complex features.

**Round F5 — Integrations** (if applicable): Does this feature require new third-party services,
new secrets/API keys, or changes to existing integrations?
If yes, use **Context7 MCP tool** to fetch the latest API docs for any newly introduced services
before proposing the implementation approach.
If Context7 is unavailable, use WebSearch + WebFetch for official docs, then ask the user for doc links.
If links are still unavailable, proceed with best-effort assumptions and caveats, and require API-doc
validation before implementation.

**Round F6-F8 — Additional depth** (for complex features): Drill into areas that need more clarity
based on the user's answers. Same adaptive follow-up rules as Init mode.

Follow-up cap: 8 for simple features, 15 for complex ones.

---

#### Bug Fix Rounds (B1-B3, use 1-3 depending on severity)

**Round B1 — Reproduction & root cause**: Clarify the exact reproduction steps if not already clear.
What's the suspected root cause? Which components/modules are involved? Reference the existing
architecture to pinpoint the affected area.

**Round B2 — Impact analysis**: What else might be affected by this fix? Are there related features
that depend on the current (broken) behavior? Does the fix change any documented behavior in
architecture.md?

**Round B3 — Fix approach** (for non-trivial bugs): If there are multiple ways to fix the issue,
present 2-3 options with trade-offs and ask the user to pick one. Consider: backward compatibility,
data migration needs, performance implications.

Follow-up cap: 5.

---

#### Change Rounds (C1-C5, use 2-5 depending on scope)

**Round C1 — Change scope**: What exactly is changing? Map the current state → desired state.
Which existing features, user journeys, or components are affected? Reference the existing
architecture to identify all touch points.

**Round C2 — Migration & compatibility**: Does this change require data migration? Is there a
transition period where old and new behavior coexist? How should existing users/data be handled?
Rollback strategy: if this change needs to be reverted after deploy, is that possible? Should it be
behind a feature flag during rollout?

**Round C3 — Cascading effects**: Based on the existing architecture, what other parts of the
system need to change as a result? API contracts, shared types, dependent components, tests?

**Round C4 — Removed or replaced functionality**: Is anything being removed? If so, how should
it be handled — hard removal, deprecation period, or replacement? Any data cleanup needed?

**Round C5 — Additional depth** (for complex changes): Drill into areas that need more clarity.

Follow-up cap: 8.

---

#### Shared rules for all update types:
- Reference existing architecture when asking questions (e.g., "The current data model has X — does this change affect it?")
- Skip rounds that don't apply
- Each round: 1-2 focused questions with concrete options when possible
- Before leaving Step 2, ask one final confirmation question (in the user's language)
