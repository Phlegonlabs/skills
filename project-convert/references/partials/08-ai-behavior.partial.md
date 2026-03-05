## AI Behavior Rules
- Follow user language.
- Read files before modifying.
- Confirm before push.
- Use first-principles reasoning first: infer root causes from requirements and architecture before choosing an implementation path.
- Treat task and sub-task as the same execution unit.
- One task must end with exactly one atomic commit; do not bundle multiple tasks in one commit.
- Follow code-is-cheap execution: when a module drifts into patch layering, delete and rewrite the module cleanly.
- Do not introduce compatibility code (adapters, shims, dual-path logic, deprecated aliases, temporary compatibility flags).
- If a rewrite changes interfaces, update all impacted callers in the same task; do not defer breakage fixes.
