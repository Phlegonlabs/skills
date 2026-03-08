# Execution Runtime — Agent Long-Task Protocol

This document defines how agents execute work across sessions. It covers session
initialization, progress tracking, the task execution loop, parallel coordination,
quality gates, and feedback mechanisms.

Read this file when starting any milestone execution.

---

## 1. Session Init Protocol

Every agent session — whether Codex or Claude Code — starts with the same boot sequence.
This is the progressive disclosure order. Load ONLY what's needed, in this exact order:

```
Step 1: Read AGENTS.md (or CLAUDE.md) — the map
         → Understand project, rules, repo layout
         → Takes ~100 lines of context

Step 2: Read docs/progress.json — where are we?
         → Current milestone, current task, blockers
         → Takes ~50 lines of context

Step 3: Read docs/PLAN.md — what's next?
         → Only the CURRENT milestone section, not the entire plan
         → Find the next ⬜ task that has no unresolved dependencies
         → Takes ~30 lines of context

Step 4: Read the relevant source files for the current task ONLY
         → Don't load the entire codebase
         → Use the dependency graph in progress.json to know what's relevant
         → Takes variable context

Step 5: Begin task execution (see §3)
```

**Context budget at boot:**
- Steps 1-3 should consume ≤ 30% of context window
- Step 4 should consume ≤ 30%
- Remaining 40% is reserved for the task execution (code, tool output, reasoning)

**If resuming a session:**
- Read progress.json FIRST to see if a task was in-progress
- If `current_task.status === "in_progress"`, check for uncommitted changes
- If dirty working tree → run validate. If green → commit and continue. If red → fix first.

---

## 2. Progress File — docs/progress.json

This is the cross-session memory. It's a machine-readable JSON file that agents update
after every significant action. NEVER edit PLAN.md without also updating progress.json.

### Schema

```json
{
  "project": "my-project",
  "last_updated": "2026-03-08T14:30:00Z",
  "last_agent": "claude-code",
  "current_milestone": {
    "id": "M1",
    "name": "Foundation",
    "branch": "milestone/M1",
    "worktree": "../my-project-M1",
    "status": "in_progress",
    "started_at": "2026-03-01T10:00:00Z",
    "tasks_total": 9,
    "tasks_done": 4,
    "tasks_in_progress": 1,
    "tasks_blocked": 0,
    "tasks_remaining": 4
  },
  "current_task": {
    "id": "M1-005",
    "story": "E1-S02",
    "description": "Implement email confirmation flow",
    "status": "in_progress",
    "started_at": "2026-03-08T14:00:00Z",
    "files_touched": [
      "src/modules/auth/confirmation.ts",
      "src/modules/auth/confirmation.test.ts"
    ],
    "notes": "Email service mock needed for testing"
  },
  "completed_milestones": [
    {
      "id": "M0",
      "name": "Scaffold",
      "completed_at": "2026-03-01T09:00:00Z",
      "tag": "v0.0.1-scaffold"
    }
  ],
  "blockers": [],
  "learnings": [
    {
      "date": "2026-03-05",
      "context": "M1-003",
      "problem": "bcrypt causes build failure on Alpine Docker",
      "solution": "Use bcryptjs (pure JS) instead of bcrypt (native)",
      "affected_files": ["package.json", "src/lib/auth/hash.ts"]
    }
  ],
  "dependency_graph": {
    "M1-001": { "depends_on": [], "blocks": ["M1-002", "M1-003"] },
    "M1-002": { "depends_on": ["M1-001"], "blocks": ["M1-004"] },
    "M1-003": { "depends_on": ["M1-001"], "blocks": ["M1-004"] },
    "M1-004": { "depends_on": ["M1-002", "M1-003"], "blocks": ["M1-005"] },
    "M1-005": { "depends_on": ["M1-004"], "blocks": ["M1-006"] },
    "M1-006": { "depends_on": ["M1-005"], "blocks": [] },
    "M1-007": { "depends_on": [], "blocks": [] },
    "M1-008": { "depends_on": ["M1-006"], "blocks": [] },
    "M1-009": { "depends_on": ["M1-008"], "blocks": [] }
  },
  "stale_check": {
    "last_run": "2026-03-08T14:00:00Z",
    "stale_files": []
  }
}
```

### Update rules

- Update `last_updated` and `last_agent` on EVERY write
- Update `current_task` when starting, completing, or failing a task
- Append to `learnings` when an unexpected problem is solved
- Update `dependency_graph` if task dependencies change during execution
- Update milestone counters after every task status change
- JSON format is intentional — agents are less likely to corrupt structured data than markdown

---

## 3. Task Execution Loop

This is the autonomous loop that agents run. It continues until the milestone is
complete or a blocker requires human intervention.

```
┌─────────────────────────────────────────┐
│  SESSION INIT (§1)                      │
│  Read AGENTS.md → progress.json → PLAN  │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  PICK NEXT TASK                         │
│  From PLAN.md, find first task where:   │
│  - status is ⬜                         │
│  - all depends_on tasks are ✅           │
│  - not in blockers list                 │
│  If no task available → milestone done  │
│    or all remaining are blocked         │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  UPDATE PROGRESS                        │
│  Set current_task in progress.json      │
│  Set task status to 🟡 in PLAN.md       │
│  Commit: [M<n>-<id>] start: <desc>     │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  LOAD CONTEXT                           │
│  Read only the files relevant to this   │
│  task (use dependency_graph + story     │
│  from PRD to know what's in scope)      │
│  Stay within context budget (§5)        │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  EXECUTE TASK                           │
│  Write / modify code to satisfy the     │
│  "Done When" criteria from PLAN.md      │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  VALIDATE (Testing Loop)                │
│  lint:fix → lint → type-check → test    │
│  See SKILL.md Phase 4 for full diagram  │
│  Loop until ALL green or max 3 retries  │
└──────┬──────────────────┬───────────────┘
       │ ALL GREEN        │ FAILED 3x
       ▼                  ▼
┌──────────────┐  ┌───────────────────────┐
│  COMMIT      │  │  LOG FAILURE          │
│  [Mn-id]     │  │  Add to blockers in   │
│  <what done> │  │  progress.json        │
│              │  │  git stash            │
│              │  │  Log learning if any   │
│              │  │  → Pick next task or   │
│              │  │    request human help  │
└──────┬───────┘  └───────────────────────┘
       ▼
┌─────────────────────────────────────────┐
│  UPDATE STATE                           │
│  Mark task ✅ in PLAN.md                 │
│  Update progress.json counters          │
│  Update dependency_graph (unblock next) │
│  Commit: [Mn-id] done: <summary>       │
└──────────────────┬──────────────────────┘
       ▼
┌─────────────────────────────────────────┐
│  CHECK: Milestone complete?             │
│  If all tasks ✅ → Milestone Merge Gate  │
│  If tasks remain → go to PICK NEXT TASK │
│  If all remaining blocked → pause,      │
│    request human review                 │
└─────────────────────────────────────────┘
```

### Max retries

If the validate loop fails 3 times on the same task:
1. `git stash` all uncommitted changes
2. Add the task to `blockers` in progress.json with the error details
3. Log the attempt in `learnings`
4. Pick the next unblocked task and continue
5. If no unblocked tasks remain, pause and request human review

---

## 4. Parallel Worktree Protocol

Multiple agents can work on different milestones simultaneously. Each agent owns
exactly one worktree. No two agents work in the same worktree.

### Rules

1. **One agent, one worktree** — never share a worktree between agents
2. **Milestones with no dependencies can run in parallel**
   - Check `Depends on` field in PLAN.md
   - M1 depends on nothing → can start immediately
   - M2 depends on M1 → cannot start until M1 is merged to main
   - M3 depends on nothing → can run parallel to M1
3. **progress.json is the coordination point**
   - Before starting a milestone, check progress.json for active agents
   - Use the `agents` field (see extended schema below) to claim a milestone
   - If a milestone is already claimed, pick another
4. **Merge order matters**
   - Milestones merge to main in dependency order
   - If M1 and M3 are both done, M1 merges first (M2 depends on M1)
   - After merge, rebase any in-progress worktrees onto updated main

### Extended progress.json for parallel

Add to the progress.json schema:

```json
{
  "agents": [
    {
      "id": "agent-1",
      "type": "claude-code",
      "milestone": "M1",
      "worktree": "../my-project-M1",
      "started_at": "2026-03-08T10:00:00Z",
      "last_heartbeat": "2026-03-08T14:30:00Z"
    },
    {
      "id": "agent-2",
      "type": "codex",
      "milestone": "M3",
      "worktree": "../my-project-M3",
      "started_at": "2026-03-08T11:00:00Z",
      "last_heartbeat": "2026-03-08T14:25:00Z"
    }
  ]
}
```

- `last_heartbeat` updates every time the agent commits or updates progress
- If heartbeat is >1 hour stale, the milestone can be reclaimed by another agent

---

## 5. Context Budget

Agent context windows are finite. Overloading context degrades performance.
Performance drops sharply beyond ~40% context utilization.

### Budget allocation

```
Total context window: 100%

Reserved zones:
├── System prompt + AGENTS.md/CLAUDE.md    ≤ 15%
├── progress.json + current PLAN section   ≤ 10%
├── PRD section for current story          ≤  5%
│   (only the relevant journey + FRs)
├── Source files for current task           ≤ 30%
├── Working memory (code gen + reasoning)   ≤ 40%
└── TOTAL                                  = 100%
```

### Progressive disclosure rules

1. **Never load the entire codebase** — only files relevant to the current task
2. **Never load the entire PLAN.md** — only the current milestone section
3. **Never load the entire PRD** — only the journey and FRs for the current story
4. **Load ARCHITECTURE.md only when starting a new module** — not for every task
5. **Load reference files (eslint-configs.md, etc.) only when generating configs**
6. **Load docs/frontend-design.md when working on ANY frontend task** — components,
   pages, layouts, styles. Read it before writing any UI code. Skip for backend-only tasks.
6. **If a file is >200 lines, load only the relevant section** (use line ranges)
7. **When context feels full** — summarize what you've learned, drop raw file content,
   continue with the summary. Don't try to hold everything at once.

### Signs of context overload

- Agent starts repeating itself or contradicting earlier statements
- Agent forgets rules from AGENTS.md
- Agent generates code that conflicts with established patterns
- Agent asks questions that were already answered in loaded files

If any of these happen → the agent should stop, commit what works, update progress.json,
and start a fresh session with only the minimum required context.

---

## 6. Quality Checkpoints

Not everything should be fully autonomous. Some decision points need human review.

### Checkpoint matrix

| Event | Mode | Action |
|-------|------|--------|
| Task completed, tests pass | **Auto** | Commit and continue |
| Task failed 3x | **Human** | Pause, report blocker, wait for input |
| Milestone all tasks done | **Auto** | Run merge gate, merge if green |
| Milestone merge gate fails | **Human** | Report what failed, wait for input |
| Integration tests fail after merge | **Human** | Report failures, suggest fixes, wait |
| New module/domain created | **Human** | Review ARCHITECTURE.md update before continuing |
| PRD acceptance criteria gap found | **Human** | Flag which criteria lack tests, wait for confirmation |
| Dependency conflict detected | **Auto** | Delete and rebuild (Iron Rule 3), log learning |
| File approaching 500 lines | **Auto** | Split immediately (Iron Rule 1), log in learnings |
| Stale doc detected | **Auto** | Update doc, commit, continue |
| Security-sensitive change (auth, payments, crypto) | **Human** | Always request review |

### How agents request human review

When a checkpoint requires human input:
1. Commit all current work (even if incomplete — use `WIP:` prefix)
2. Update progress.json with detailed context about what needs review
3. Write a clear summary in PLAN.md under the task's Notes column
4. Stop execution on this task — pick next unblocked task if available
5. If no unblocked tasks, pause entirely and output a review request

---

## 7. Stale Detection

Documentation and plans rot fast. Agents should proactively detect and fix staleness.

### What goes stale

| Artifact | Stale signal | Action |
|----------|-------------|--------|
| AGENTS.md / CLAUDE.md | Quick start commands don't match actual scripts | Update commands |
| ARCHITECTURE.md | New module exists in src/ but not in doc | Add module to domain map |
| docs/PLAN.md | Task done but status still ⬜ | Mark ✅, update counters |
| docs/PRD.md | Implemented feature deviates from spec | Flag deviation, update PRD or fix code |
| docs/site/ | New feature shipped but no user-facing doc | Create doc page |
| .env.example | New env var in code but not in example | Add to .env.example |
| progress.json | Heartbeat >1 hour old | Mark agent as stale, allow reclaim |
| dependency_graph | Task order changed but graph not updated | Rebuild graph |

### When to run stale checks

1. **Every session init** — before starting work, scan for obvious staleness
2. **Every milestone completion** — full stale audit before merge
3. **Periodically during long sessions** — every ~10 commits, quick scan

### How to fix

- If the fix is mechanical (update a command, add a file to a list) → fix it, commit
- If the fix requires a judgment call (PRD deviation) → flag for human review
- Log the staleness and fix in `learnings` section of progress.json

---

## 8. Agent Learnings Log

When an agent encounters an unexpected problem and solves it, that knowledge must be
captured so future sessions (by the same or different agents) don't repeat the mistake.

### Where learnings live

1. **progress.json `learnings` array** — machine-readable, searchable
2. **docs/learnings.md** — human-readable log, chronological

### Learnings schema (in progress.json)

```json
{
  "date": "2026-03-05",
  "context": "M1-003",
  "category": "dependency",
  "problem": "bcrypt causes build failure on Alpine Docker image",
  "solution": "Use bcryptjs (pure JS) instead of bcrypt (native binding)",
  "affected_files": ["package.json", "src/lib/auth/hash.ts"],
  "prevention": "Prefer pure-JS packages over native bindings for Docker compat"
}
```

Categories: `dependency`, `config`, `architecture`, `testing`, `deploy`, `performance`, `security`, `tooling`

### docs/learnings.md format

```markdown
# Agent Learnings Log

## 2026-03-05 — [M1-003] bcrypt vs bcryptjs
**Problem:** bcrypt native bindings fail to build on Alpine Docker images.
**Solution:** Replaced bcrypt with bcryptjs (pure JS implementation).
**Prevention:** Prefer pure-JS packages over native bindings for Docker compatibility.
**Files:** package.json, src/lib/auth/hash.ts
```

### When to log

- Dependency caused unexpected failure
- Config required non-obvious adjustment
- Test required a specific mock/setup that wasn't obvious
- Architecture decision was wrong and had to be corrected
- Build/deploy failed for environment-specific reasons
- A workaround was needed (and should be removed when upstream fixes)

### Session init reads learnings

During session init (§1), after reading progress.json, scan the `learnings` array.
If any learning is relevant to the current task (matching `affected_files` or `category`),
keep it in context. Otherwise, skip — don't waste context budget on irrelevant history.

---

## 9. Task Dependency Graph

The dependency graph lives in progress.json and determines:
- Which tasks can run in parallel
- Which tasks are blocked
- Which tasks are next when one completes

### Graph structure

```json
{
  "M1-001": { "depends_on": [], "blocks": ["M1-002", "M1-003"], "parallelizable": true },
  "M1-002": { "depends_on": ["M1-001"], "blocks": ["M1-004"], "parallelizable": true },
  "M1-003": { "depends_on": ["M1-001"], "blocks": ["M1-004"], "parallelizable": true },
  "M1-004": { "depends_on": ["M1-002", "M1-003"], "blocks": [], "parallelizable": false }
}
```

- `parallelizable: true` means this task can run at the same time as other parallelizable
  tasks that share no dependencies (relevant for multi-agent setups)
- A task is "ready" when: status is ⬜ AND all `depends_on` tasks are ✅

### Building the graph

When generating PLAN.md, also generate the dependency graph in progress.json:

1. Map each task to its story (from PRD §9)
2. Stories within the same epic are usually sequential
3. Cross-epic dependencies come from the data model and API surface
4. Infrastructure tasks (CI, config) have no dependencies — can run first or in parallel
5. Test tasks depend on their implementation task

### Visual output

When a human or agent wants to see the dependency graph, render it as:

```
M1-001 (Create user model)
├── M1-002 (Signup endpoint) ──┐
└── M1-003 (Password hashing) ─┤
                                └── M1-004 (Signup test)
                                     └── M1-005 (Email confirmation)
                                          └── M1-006 (Confirmation test)
M1-007 (Setup CI) ← independent, can run anytime
```

---

## 10. Integration Testing

Unit tests run per-task. Integration tests run per-milestone-merge.

### When integration tests run

1. After a milestone worktree is merged back to main
2. Before the next milestone's worktree is created from the updated main
3. In CI on every PR to main (not to milestone branches)

### What integration tests cover

- **Cross-module communication**: Does auth module talk to user module correctly?
- **API contract**: Do endpoints return the expected shapes?
- **Database**: Do migrations run cleanly? Do queries return expected data?
- **End-to-end flows**: Can a user complete the core journeys from PRD §3?

### Integration test structure

```
tests/
├── unit/              ← per-task, per-module (run in task loop)
├── integration/       ← cross-module (run at milestone merge)
│   ├── auth-flow.test.ts
│   ├── api-contracts.test.ts
│   └── db-migrations.test.ts
└── e2e/               ← full user journeys (run at milestone merge)
    ├── onboarding.test.ts
    └── core-journey.test.ts
```

### Scripts

Add to package.json:
```json
{
  "scripts": {
    "test": "vitest run",
    "test:integration": "vitest run --project integration",
    "test:e2e": "vitest run --project e2e",
    "validate": "... && npm run test",
    "validate:full": "... && npm run test && npm run test:integration && npm run test:e2e"
  }
}
```

- `validate` (task level): lint + type-check + unit tests
- `validate:full` (milestone merge level): lint + type-check + unit + integration + e2e

### Milestone merge with integration tests

```
Merge gate (updated):
1. Run validate:full in the worktree
2. If green → merge to main
3. After merge, run validate:full on main
4. If main is green → tag milestone complete
5. If main is red → the merge introduced a conflict
   → Fix on main (not in a worktree), commit fix, re-run
```

---

## 11. Milestone Lifecycle — Complete Flow

Putting it all together. This is the end-to-end lifecycle of a single milestone:

```
1. CREATE WORKTREE
   git worktree add ../<project>-M<n> -b milestone/M<n>
   cd ../<project>-M<n>

2. INIT SESSION (§1)
   Read AGENTS.md → progress.json → PLAN.md (current milestone only)

3. CLAIM MILESTONE
   Update progress.json: set current_milestone, add agent to agents list

4. TASK LOOP (§3)
   While tasks remain:
     a. Pick next unblocked task
     b. Load relevant context (respect budget §5)
     c. Execute task
     d. Validate (lint → type → test)
     e. Commit or retry (max 3x)
     f. Update PLAN.md + progress.json
     g. Check for stale docs (§7)
     h. Log learnings if any (§8)
     i. Check quality checkpoints (§6)

5. MILESTONE MERGE GATE
   a. Run validate:full (unit + integration + e2e)
   b. Check no file > 500 lines
   c. Check all acceptance criteria verified
   d. Check docs/site/ updated
   e. Check learnings logged

6. HUMAN REVIEW (if required by §6 checkpoint matrix)
   a. Present summary of changes
   b. Wait for approval

7. MERGE
   cd ../<project>
   git merge milestone/M<n>
   git tag v<version>-M<n>

8. POST-MERGE
   a. Run validate:full on main
   b. Run integration tests
   c. Update progress.json: move milestone to completed_milestones
   d. Move exec-plans/active/ → exec-plans/completed/
   e. Clean up: git worktree remove ../<project>-M<n>

9. NEXT MILESTONE
   Check dependency graph → which milestone is unblocked?
   → Create new worktree, go to step 1
```

---

## 12. Idle Protocol & Adding New Work

### When all milestones are complete

The task loop in §3 ends when: no tasks remain and no milestones are active.
At this point:

1. Run final stale detection (§7) across all docs
2. Fix any stale items, commit
3. Run `validate:full` on main
4. Report completion to user: "All milestones complete. Green. Ready for new work."
5. WAIT — do NOT invent work. Only the user creates new requirements.

### Adding new work (Path A: in Claude Code / Codex)

When the user describes new work directly to the agent:

```
1. READ current PRD.md — understand existing scope
2. ADD new FRs to PRD.md §4:
   - ID: FR-<next number>
   - Acceptance criteria (testable)
   - MoSCoW priority
   - Parent journey (new or existing from §3)
3. ADD new Epic + Stories to PRD.md §9:
   - Story ID: E<n>-S<nn>
   - "As a... I want to... So that..."
   - Acceptance criteria + estimate
4. ADD new Milestone to PLAN.md:
   - M<next number>: <name>
   - Branch: milestone/M<n>
   - Covers: Epic E<n> (FR-xxx, FR-yyy)
   - Depends on: <which completed milestones, if any>
   - Tasks decomposed to ≤ 4h each with "Done When"
5. UPDATE progress.json:
   - Add milestone to current structure (not completed_milestones)
   - Build dependency_graph entries for all new tasks
   - Reset current_milestone to the new one
6. UPDATE ARCHITECTURE.md if new modules needed
7. COMMIT: [docs] add milestone M<n>: <feature name>
8. CREATE worktree: git worktree add ../<project>-M<n> -b milestone/M<n>
9. BEGIN normal Task Execution Loop (§3)
```

### Adding new work (Path B: via claude.ai)

User returns to claude.ai with the harness-engineer skill and uploads:
- AGENTS.md / CLAUDE.md, PRD.md, PLAN.md, progress.json, ARCHITECTURE.md

The skill runs a lighter version of Phase 1-2:
- Skip product type + vision (already established)
- Focused Product Deep Dive on the NEW requirements only
- Optional web search for the new feature domain
- Generate updated PRD, PLAN, progress.json with new milestones appended
- User copies updated files to repo, commits, agent picks up on next session init

### The loop is perpetual

The Task Execution Loop (§3) does not distinguish between initial development
and ongoing feature work. As long as PLAN.md has a milestone with ⬜ tasks and
progress.json has the matching dependency graph, the agent executes identically.

```
Bootstrap → Sprint 1 → All done → Idle
    → User adds work → Sprint 2 → All done → Idle
    → User adds work → Sprint 3 → ...
    → Repeat forever
```

The repo is the single source of truth. The conversation is ephemeral.
