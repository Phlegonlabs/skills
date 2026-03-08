# Execution Runtime — Agent Guidelines

Conceptual guidelines that complement the harness CLI.
The CLI handles mechanics (state, validation, task picking). This doc handles
judgment calls that can't be automated: context management, parallel coordination,
quality gates, and when to ask humans.

---

## Parallel Worktree Protocol

Multiple agents can work on different milestones simultaneously.

**Rules:**
1. **One agent, one worktree** — CLI enforces this via `agents` array in progress.json
2. **Milestones with no dependencies run in parallel** (check PLAN.md `Depends on`)
3. **progress.json is the coordination point** — agents self-register via `harness init`
4. **Merge order follows dependency order** — `worktree:finish` blocks if deps aren't merged
5. **Stale heartbeat (>2h) = reclaimable** — another agent can take the milestone
6. **Rebase after upstream merge** — when a parallel milestone merges, others rebase

Example parallel setup:
```
Agent 1: harness worktree:start M1  → working on M1
Agent 2: harness worktree:start M3  → working on M3 (no dep on M1)

# Agent 1 finishes M1:
cd main-repo && harness worktree:finish M1  → merges M1 into main

# Agent 2 rebases M3 onto updated main (inside M3 worktree):
harness worktree:rebase  → git rebase main
# resolve any conflicts, then continue working

# Agent 2 finishes M3:
cd main-repo && harness worktree:finish M3  → auto-rebases, merges M3

# Check status from main:
harness worktree:status  → shows agents, heartbeats, merge readiness
```

**Agent registration lifecycle:**
- `harness init` (in worktree) → registers agent with id, milestone, heartbeat
- `harness next/start/done` → updates heartbeat timestamp
- `harness worktree:finish` → deregisters agent, removes worktree
- Heartbeat >2h old → shown as STALE in `worktree:status`, reclaimable by other agents

---

## Context Budget

Performance degrades beyond ~40% context utilization. Budget:

| Zone | Budget |
|------|--------|
| System prompt + AGENTS.md / CLAUDE.md | ≤ 15% |
| `harness status` output + current PLAN section | ≤ 10% |
| PRD section for current story | ≤ 5% |
| Source files for current task | ≤ 30% |
| Working memory (code + reasoning) | ≤ 40% |

**Progressive disclosure:**
- Never load entire codebase, entire PLAN, or entire PRD
- Load only files relevant to the current task
- Load `docs/frontend-design.md` only when task involves frontend
- Files >200 lines → load only the relevant section
- Context overloaded? → `harness done`, commit, start fresh session

**Signs of overload:** repeating itself, forgetting rules, conflicting patterns, re-asking answered questions.

---

## Quality Checkpoints

| Event | Mode | Action |
|-------|------|--------|
| Task passes `harness validate` | **Auto** | `harness done`, continue |
| Task failed 3x | **Human** | `harness block`, report, wait |
| Milestone all done | **Auto** | `harness merge-gate` |
| Merge gate fails | **Human** | Report, wait |
| Integration tests fail | **Human** | Report, suggest fix, wait |
| New module created | **Human** | Review ARCHITECTURE.md update |
| Security-sensitive change | **Human** | Always request review |
| Dependency conflict | **Auto** | Delete and rebuild (Iron Rule 3) |
| File approaching 500 lines | **Auto** | Split (Iron Rule 1) |
| Stale doc detected | **Auto** | Fix, commit, continue |
| TODO/FIXME found in code | **Auto** | Convert to task in PLAN.md, remove comment (Iron Rule 7) |
| console.log in production code | **Auto** | Replace with structured logger (Iron Rule 7) |
| Unhandled error path detected | **Auto** | Add try/catch + error logging (Iron Rule 7) |
| Build warning | **Auto** | Fix before commit — zero warnings policy (Iron Rule 7) |

**How to request human review:**
1. `harness block <id> "needs human review: <reason>"`
2. Commit current work with `[WIP: Mn-id]` prefix
3. Pick next unblocked task via `harness next`, or pause if none

---

## Integration Testing

Three test tiers:

| Tier | Scope | Trigger | Command |
|------|-------|---------|---------|
| Unit | Per-module | Every task | `harness validate` |
| Integration | Cross-module | Milestone merge | `harness validate:full` |
| E2E | Full user journey | Milestone merge | `harness validate:full` |

Test directory structure:
```
tests/
├── unit/              ← run per-task
├── integration/       ← run at milestone merge
└── e2e/               ← run at milestone merge
```

---

## Learnings Format

When `harness learn` logs an entry, it uses this structure in progress.json:

```json
{
  "date": "2026-03-05",
  "context": "M1-003",
  "category": "dependency",
  "problem": "bcrypt native bindings fail on Alpine Docker",
  "solution": "Use bcryptjs (pure JS) instead",
  "affected_files": ["package.json", "src/lib/auth/hash.ts"],
  "prevention": "Prefer pure-JS packages for Docker compatibility"
}
```

Categories: `dependency`, `config`, `architecture`, `testing`, `deploy`, `performance`, `security`, `tooling`

During session init (`harness init`), scan learnings relevant to the current task.
Load those. Skip irrelevant history — don't waste context budget.
