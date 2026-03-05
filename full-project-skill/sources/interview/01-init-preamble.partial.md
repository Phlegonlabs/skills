# Phase 1: Interactive Interview

Collect project information through conversation. If your environment supports interactive question prompts (with selectable options), use them — otherwise ask in plain text.

## Complexity Tiers

After collecting Project Goals (Step 2), assess complexity and assign a tier. The tier controls which
interview rounds to run, how many follow-ups are allowed, and how deep to probe.

**Default tier is Standard.** When in doubt, stay at Standard.

| Tier | Criteria | Target Questions | Rounds to run | Follow-up Cap |
|------|----------|-----------------|--------------|---------------|
| **Standard** | **Default for all projects.** Multiple roles or features, some integrations, moderate UI/data complexity | ~15 | All applicable rounds (full protocol; GUI ~10-11, CLI ~10-13, Mobile includes R11M-R13M when applicable) | 8 |
| **Complex** | Multi-role, multi-platform, integration-heavy, enterprise requirements | ~25-30 | All applicable rounds (full protocol) + extended depth on architecture, security, scale (Mobile includes R11M-R13M when applicable) | 20 |

After Step 2, announce the assessed tier to the user and let them override. Default assumption is Standard.

## Step 1 — Project Name

Ask the user for the project name. This becomes the directory context and document titles.

Example question: "What's the project name?"

## Step 2 — Project Goals (Free-form)

This is the most important step. Before diving into tech stack or feature lists, ask the user to describe
their project goals in their own words — what problem they're solving, who it's for, what the end result
should look like. This can be as brief or detailed as they want. The point is to capture intent and context
before any structured breakdown.

Example question: "Tell me about your project — what are you building, what problem does it solve, and who is it for? Just describe it in your own words, no need to be structured."

Let the user write freely. Do NOT interrupt with follow-up questions mid-description.

## Step 2.5 — Market Research Snapshot (similar projects & references)

Before deep questioning, run one concise market scan based on the goals from Step 2.
The objective is to ground planning in reality: what already exists, what patterns work,
and where this project can differentiate.

Research output (keep it concise, high-signal):
1. **Comparable products/projects (3-5)**:
   - Name + link (if available)
   - Target user + core value proposition
   - Notable flow/pattern relevant to this project
2. **Reference candidates (2-5)**:
   - Potential objects to borrow from (UX flow, IA, onboarding, component pattern, pricing/packaging, integration model)
   - Why each reference is relevant
3. **Differentiation opportunities (2-4)**:
   - What this project should do differently to avoid being a clone
4. **Risks to avoid**:
   - Typical pitfalls seen in similar products
5. **Stack module signals**:
   - Identify likely stack modules used by those products
   - Use `references/tech-components.md` as the category map for later Round R10.7 decisions

Execution rules for this step:
- If web browsing/tools are available, use current sources and include links.
- If browsing is unavailable, use this fallback ladder:
  1. Ask the user for known competitors/references first.
  2. Add only high-confidence generic patterns (no fabricated links, metrics, or pricing claims).
  3. Clearly label output as best-effort inference with caveats.
  4. Add a follow-up note to validate references when browsing/tools become available.
- Keep this as a single research round, not an endless exploration.
- Do NOT skip this step when the user explicitly asks for market research first.

Ask for quick confirmation before moving on:
"Based on this landscape, should we use these references and differentiation points as the planning baseline?"

## Step 2.7 — Project Introduction & Core Flow Draft

After Step 2.5, draft a clearer project framing before detailed clarifying rounds.
This is the first editable draft the user can refine.

Draft structure:
1. **Project introduction** (4-8 bullets): what it is, who it serves, why now, key value proposition
2. **Candidate core flow** (end-to-end):
   - Entry point
   - Activation/onboarding
   - Core usage loop
   - Success/exit state
   - Return/retention trigger
3. **Open assumptions** (if any): explicitly mark unknowns that need clarification in Step 3

Guard:
- This draft must be based on Step 2 goals + Step 2.5 market research.
- Ask the user to revise/approve this draft before starting Step 2.8.

## Step 2.8 — Design Direction (Product Architecture + Visual Style)

After Step 2.7 is confirmed, run a dedicated design-direction step before deep clarifying rounds.

Protocol:
1. Based on Step 2.5 + Step 2.7, propose **3-4 product architecture directions** with clearly different
   product shape / core UX modes.
2. Ask the user to choose one direction (or provide reference images/websites).
3. Based on the selected direction, propose a visual style recommendation:
   - color system
   - typography direction
   - layout style
   - overall aesthetic principles
4. Get explicit user confirmation on the chosen design direction before entering Step 3.
