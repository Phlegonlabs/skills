# AGENTS.md Template

Use this as the dedicated AGENTS quick reference template (different from CLAUDE.md).

## Operating Mode
- Default runtime: Plan-first for non-trivial work.
- Execution contract: `tasks/todo.md`.
- Lessons contract: `tasks/lessons.md`.
- Worktree policy: warning by default, enforce with `.claude/.require-worktree`.

## Workflow Orchestration
- Use a plan node before implementation.
- Split independent tracks to subagents.
- Keep a self-improvement loop by writing prevention rules to `tasks/lessons.md`.

## Task Management Protocol
- Keep active, blocked, review, completed sections in `tasks/todo.md`.
- Every completed task must include verification evidence.

## Key Docs / Tech Stack / Commands / Structure / Conventions
- Reuse the same project-specific values as CLAUDE.md.
- Do not include user-facing STATUS contract blocks in AGENTS.md.
- Do not include hook setup recommendations in AGENTS.md.
