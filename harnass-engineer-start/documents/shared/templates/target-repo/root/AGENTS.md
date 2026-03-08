Rules:
- do not execute before an approved plan exists in `harnass-os/documents/plans/`
- do not implement ui-facing work before `harnass-os/documents/design/wireframe.md` and `harnass-os/documents/design/design.md` exist
- do not deploy before preview validation and deployment gates pass
- do not mark a release complete before `harnass-os/documents/audit/current.yaml` passes final audit
- keep plan, handoff, run, and status documents synchronized with code changes
- keep `harnass-os/documents/orchestrator/current.yaml` synchronized with the active lifecycle phase
- use `harnass-os/hooks/` and `harnass-os/scripts/agent-guard.py` or a stack-equivalent guard layer
- prefer composable data structures over branch-heavy logic
- keep functions small enough to reason about quickly
- remove dead code instead of preserving compatibility shims
- keep tests close to behavior changes

Red-Line Defaults:

| Metric | Recommended Threshold |
|---|---|
| File lines | <= 800 |
| Function lines | <= 40 (split if comprehension drops) |
| Nesting depth | <= 3 |
| Branch count | <= 3 |

