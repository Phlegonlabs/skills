## Coding Constraints
- Use first-principles reasoning to solve root causes before implementation.
- First principles over patch layering.
- Preserve single source of truth between specs, contracts, tests.
- Do not close tasks without verification.
- Treat task and sub-task as the same execution unit.
- Enforce one task -> one atomic commit.
- Prefer rewrite over patch layering: if a module is on a wrong path, delete and rewrite it.
- Never add compatibility code (adapters, shims, dual-path logic, deprecated aliases, temporary compatibility flags).
- If interfaces change during rewrite, fix every affected caller in the same task before commit.
