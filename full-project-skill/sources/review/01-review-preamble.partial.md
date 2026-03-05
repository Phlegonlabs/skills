# Phase 2.5: Multi-Agent Documentation Review

After generating all documents, launch a **multi-agent review team** to validate the documentation
quality, consistency, and completeness before handing off to the user.
If your environment supports spawning parallel reviewers/agents, use it — otherwise run the same checklists sequentially.

Use the **complexity tier** assigned during Phase 1 (see SKILL.md) to determine review scope:

- **Standard**: spawn Agent 2 + Agent 3, then run Codex review.
- **Complex**: spawn Agent 1 + Agent 2 + Agent 3, then run Codex review, then post-Codex re-review with Agent 2 + Agent 3, then run a second-pass recheck with Agent 2 + Agent 3 after fixes.

Use the agent definitions below as the review pool.
