## Step 3.5 — Tier Recheck

After completing all interview rounds, **reassess the complexity tier** based on what was actually discovered.
The initial tier was assessed after Step 2 (a rough description) — now you have full context.

- If the project turned out **more complex** than initially assessed (e.g., more roles, more integrations,
  multi-platform needs discovered during rounds), **upgrade the tier to Complex** and announce the change.
- Tier changes affect: milestone count in docs/plans.md, review scope in Phase 2.5.

This step is silent if the tier hasn't changed — only announce when there's a change.

## Step 4 — Synthesis & Confirmation

After gathering enough context from Steps 2, 2.5, 2.7, 2.8, and 3, **synthesize everything into a complete project summary**.
Present to the user:

1. **Project overview** — 2-3 sentence summary in your own words based on what you learned
2. **Market research snapshot** — 3-5 comparable products and 2-5 references, including what to borrow,
   what to avoid, and how this project differentiates
3. **Project introduction & core flow** — Refined version of the Step 2.7 draft:
   - Project introduction (problem, target users, positioning)
   - End-to-end core flow (entry → activation → core loop → success → retention)
4. **Design direction** — Confirmed output from Step 2.8:
   - Chosen product architecture direction
   - Visual style baseline (color system, typography, layout style, aesthetic principles)
5. **Core features** — A structured feature list (3-8 features) broken down from the conversation:
   - Feature name (short label)
   - What it does (1-3 sentences)
   - Key constraints or requirements you inferred
6. **Tech stack** — Confirmed stack from Round R10.7
7. **UI approach** — UI framework, CSS approach, key components, icon set (GUI projects only)
   **CLI interface** — Command structure, output modes, config strategy, key conventions (CLI projects only)
8. **Deployment** — Hosting platform, database hosting, CI/CD approach
9. **Quality & infrastructure** — Testing strategy, a11y requirements, i18n support, error tracking,
   SEO approach (summarize decisions from Rounds R10.3 and R10.5)
10. **Scope notes** — Anything explicitly out of scope or deferred
11. **Production standard** — Remind the user: "The generated plan includes a **Production Readiness Gate**
    as the final milestone. Every milestone is written to produce production-quality code from the start.
    The final deliverable will be deployment-ready — not a demo or prototype."

Ask the user to confirm, or revise anything before doc generation.

Offer a simple confirmation choice like:
- "Looks good, generate the docs"
- "I want to adjust some things"

If your environment supports selectable options/prompts, use them; otherwise ask the user to reply with one of the options above.

If the user wants changes, iterate until they're satisfied.

**Guard**: After presenting the synthesis, STOP. Do NOT proceed to Phase 2 until the user
explicitly confirms. Do not generate documents, write files, or begin implementation.
If the user describes additional features instead of confirming, treat it as feedback
and continue the interview.
