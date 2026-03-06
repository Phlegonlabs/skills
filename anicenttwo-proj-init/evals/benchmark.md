# Skill Benchmark Report

Latest iteration: `iteration-20260306-074023`

Workspace root: `C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init-workspace`

Generated: 2026-03-06T12:40:29.171Z

## Command Matrix

| Agent | Profile | Command |
| --- | --- | --- |
| claude | with_skill | `claude -p --output-format text --no-session-persistence --permission-mode bypassPermissions --add-dir 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init' 'Initialize a new B2B internal tool with Vite, TanStack Router, tasks-first workflow files, and concise CLAUDE.md/AGENTS.md for both Claude and Codex.'` |
| claude | without_skill | `claude -p --output-format text --no-session-persistence --permission-mode bypassPermissions --disable-slash-commands 'Initialize a new B2B internal tool with Vite, TanStack Router, tasks-first workflow files, and concise CLAUDE.md/AGENTS.md for both Claude and Codex.'` |
| codex | with_skill | `codex exec -C 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init-workspace\iteration-20260306-074023\codex\with_skill\initialize-new-project' --dangerously-bypass-approvals-and-sandbox -o 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init-workspace\iteration-20260306-074023\codex\with_skill\initialize-new-project\final-response.md' --add-dir 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init' 'Initialize a new B2B internal tool with Vite, TanStack Router, tasks-first workflow files, and concise CLAUDE.md/AGENTS.md for both Claude and Codex.'` |
| codex | without_skill | `codex exec -C 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init-workspace\iteration-20260306-074023\codex\without_skill\initialize-new-project' --dangerously-bypass-approvals-and-sandbox -o 'C:\Users\mps19\Documents\Github\skills\anicenttwo-proj-init-workspace\iteration-20260306-074023\codex\without_skill\initialize-new-project\final-response.md' 'Initialize a new B2B internal tool with Vite, TanStack Router, tasks-first workflow files, and concise CLAUDE.md/AGENTS.md for both Claude and Codex.'` |

## claude / with_skill

| Eval | Status | Exit | Duration | Changed Files | Raw Artifacts |
| --- | --- | --- | ---: | ---: | --- |
| initialize-new-project | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/initialize-new-project) |
| repair-agents-task-sync | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/repair-agents-task-sync) |
| migrate-legacy-repo | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/migrate-legacy-repo) |
| audit-workflow-drift | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/audit-workflow-drift) |

### initialize-new-project

- Eval: `1`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/initialize-new-project](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/initialize-new-project)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Chooses a plausible core plan and explains the stack choice.
  - Includes tasks/todo.md, tasks/lessons.md, tasks/research.md, and tasks/contracts/ in the generated workflow.
  - Treats docs/PROGRESS.md as milestone-only instead of the active execution log.

### repair-agents-task-sync

- Eval: `2`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/repair-agents-task-sync](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/repair-agents-task-sync)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Calls out repo-local task sync as the primary enforcement mechanism.
  - Updates the final response contract to mention changed tasks files.
  - Avoids treating hooks as the only source of enforcement.

### migrate-legacy-repo

- Eval: `3`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/migrate-legacy-repo](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/migrate-legacy-repo)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Replaces docs/TODO.md with tasks/todo.md as the primary task contract.
  - Adds repo-local task-sync enforcement such as scripts/check-task-sync.sh.
  - Updates migration guidance and scripts rather than only editing prose.

### audit-workflow-drift

- Eval: `4`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/audit-workflow-drift](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/with_skill/audit-workflow-drift)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Checks both Claude-specific hooks and cross-agent repo-local contracts.
  - Flags docs/PROGRESS.md misuse if it is acting as an execution log.
  - Mentions migration or template updates when current files are out of sync with the skill.

## claude / without_skill

| Eval | Status | Exit | Duration | Changed Files | Raw Artifacts |
| --- | --- | --- | ---: | ---: | --- |
| initialize-new-project | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/initialize-new-project) |
| repair-agents-task-sync | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/repair-agents-task-sync) |
| migrate-legacy-repo | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/migrate-legacy-repo) |
| audit-workflow-drift | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/audit-workflow-drift) |

### initialize-new-project

- Eval: `1`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/initialize-new-project](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/initialize-new-project)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Chooses a plausible core plan and explains the stack choice.
  - Includes tasks/todo.md, tasks/lessons.md, tasks/research.md, and tasks/contracts/ in the generated workflow.
  - Treats docs/PROGRESS.md as milestone-only instead of the active execution log.

### repair-agents-task-sync

- Eval: `2`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/repair-agents-task-sync](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/repair-agents-task-sync)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Calls out repo-local task sync as the primary enforcement mechanism.
  - Updates the final response contract to mention changed tasks files.
  - Avoids treating hooks as the only source of enforcement.

### migrate-legacy-repo

- Eval: `3`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/migrate-legacy-repo](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/migrate-legacy-repo)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Replaces docs/TODO.md with tasks/todo.md as the primary task contract.
  - Adds repo-local task-sync enforcement such as scripts/check-task-sync.sh.
  - Updates migration guidance and scripts rather than only editing prose.

### audit-workflow-drift

- Eval: `4`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/audit-workflow-drift](../anicenttwo-proj-init-workspace/iteration-20260306-074023/claude/without_skill/audit-workflow-drift)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Checks both Claude-specific hooks and cross-agent repo-local contracts.
  - Flags docs/PROGRESS.md misuse if it is acting as an execution log.
  - Mentions migration or template updates when current files are out of sync with the skill.

## codex / with_skill

| Eval | Status | Exit | Duration | Changed Files | Raw Artifacts |
| --- | --- | --- | ---: | ---: | --- |
| initialize-new-project | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/initialize-new-project) |
| repair-agents-task-sync | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/repair-agents-task-sync) |
| migrate-legacy-repo | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/migrate-legacy-repo) |
| audit-workflow-drift | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/audit-workflow-drift) |

### initialize-new-project

- Eval: `1`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/initialize-new-project](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/initialize-new-project)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Chooses a plausible core plan and explains the stack choice.
  - Includes tasks/todo.md, tasks/lessons.md, tasks/research.md, and tasks/contracts/ in the generated workflow.
  - Treats docs/PROGRESS.md as milestone-only instead of the active execution log.

### repair-agents-task-sync

- Eval: `2`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/repair-agents-task-sync](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/repair-agents-task-sync)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Calls out repo-local task sync as the primary enforcement mechanism.
  - Updates the final response contract to mention changed tasks files.
  - Avoids treating hooks as the only source of enforcement.

### migrate-legacy-repo

- Eval: `3`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/migrate-legacy-repo](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/migrate-legacy-repo)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Replaces docs/TODO.md with tasks/todo.md as the primary task contract.
  - Adds repo-local task-sync enforcement such as scripts/check-task-sync.sh.
  - Updates migration guidance and scripts rather than only editing prose.

### audit-workflow-drift

- Eval: `4`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/audit-workflow-drift](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/with_skill/audit-workflow-drift)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Checks both Claude-specific hooks and cross-agent repo-local contracts.
  - Flags docs/PROGRESS.md misuse if it is acting as an execution log.
  - Mentions migration or template updates when current files are out of sync with the skill.

## codex / without_skill

| Eval | Status | Exit | Duration | Changed Files | Raw Artifacts |
| --- | --- | --- | ---: | ---: | --- |
| initialize-new-project | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/initialize-new-project) |
| repair-agents-task-sync | dry_run | 0 | 2ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/repair-agents-task-sync) |
| migrate-legacy-repo | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/migrate-legacy-repo) |
| audit-workflow-drift | dry_run | 0 | 1ms | 0 | [workspace](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/audit-workflow-drift) |

### initialize-new-project

- Eval: `1`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/initialize-new-project](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/initialize-new-project)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Chooses a plausible core plan and explains the stack choice.
  - Includes tasks/todo.md, tasks/lessons.md, tasks/research.md, and tasks/contracts/ in the generated workflow.
  - Treats docs/PROGRESS.md as milestone-only instead of the active execution log.

### repair-agents-task-sync

- Eval: `2`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/repair-agents-task-sync](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/repair-agents-task-sync)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Calls out repo-local task sync as the primary enforcement mechanism.
  - Updates the final response contract to mention changed tasks files.
  - Avoids treating hooks as the only source of enforcement.

### migrate-legacy-repo

- Eval: `3`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/migrate-legacy-repo](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/migrate-legacy-repo)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Replaces docs/TODO.md with tasks/todo.md as the primary task contract.
  - Adds repo-local task-sync enforcement such as scripts/check-task-sync.sh.
  - Updates migration guidance and scripts rather than only editing prose.

### audit-workflow-drift

- Eval: `4`
- Workspace: [../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/audit-workflow-drift](../anicenttwo-proj-init-workspace/iteration-20260306-074023/codex/without_skill/audit-workflow-drift)
- Changed files: none
- Diff summary: no diff captured
- Final response excerpt: dry-run: no final response captured
- Expectations:
  - Checks both Claude-specific hooks and cross-agent repo-local contracts.
  - Flags docs/PROGRESS.md misuse if it is acting as an execution log.
  - Mentions migration or template updates when current files are out of sync with the skill.
