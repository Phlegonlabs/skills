# Schemas & Git Hooks

Mechanical enforcement of rules that were previously prose.
These are generated into the output project during scaffold.

---

## schemas/progress.schema.json

Validate progress.json on every commit. Prevents format rot.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Project Progress",
  "type": "object",
  "required": ["project", "last_updated", "last_agent", "current_milestone"],
  "properties": {
    "project": { "type": "string", "minLength": 1 },
    "last_updated": { "type": "string", "format": "date-time" },
    "last_agent": { "type": "string", "enum": ["claude-code", "codex", "human"] },
    "current_milestone": {
      "type": ["object", "null"],
      "properties": {
        "id": { "type": "string", "pattern": "^M[0-9]+$" },
        "name": { "type": "string" },
        "branch": { "type": "string", "pattern": "^milestone/M[0-9]+$" },
        "worktree": { "type": "string" },
        "status": { "type": "string", "enum": ["not_started", "in_progress", "complete"] },
        "started_at": { "type": ["string", "null"], "format": "date-time" },
        "tasks_total": { "type": "integer", "minimum": 0 },
        "tasks_done": { "type": "integer", "minimum": 0 },
        "tasks_in_progress": { "type": "integer", "minimum": 0 },
        "tasks_blocked": { "type": "integer", "minimum": 0 },
        "tasks_remaining": { "type": "integer", "minimum": 0 }
      },
      "required": ["id", "name", "status", "tasks_total", "tasks_done"]
    },
    "current_task": {
      "type": ["object", "null"],
      "properties": {
        "id": { "type": "string", "pattern": "^M[0-9]+-[0-9]+$" },
        "story": { "type": "string" },
        "description": { "type": "string" },
        "status": { "type": "string", "enum": ["in_progress", "blocked"] },
        "started_at": { "type": "string", "format": "date-time" },
        "files_touched": { "type": "array", "items": { "type": "string" } },
        "notes": { "type": "string" }
      },
      "required": ["id", "description", "status"]
    },
    "completed_milestones": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "completed_at"],
        "properties": {
          "id": { "type": "string", "pattern": "^M[0-9]+$" },
          "name": { "type": "string" },
          "completed_at": { "type": "string", "format": "date-time" },
          "tag": { "type": "string" }
        }
      }
    },
    "blockers": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["task_id", "description"],
        "properties": {
          "task_id": { "type": "string" },
          "description": { "type": "string" },
          "error": { "type": "string" },
          "added_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "learnings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["date", "context", "problem", "solution"],
        "properties": {
          "date": { "type": "string" },
          "context": { "type": "string" },
          "category": { "type": "string", "enum": [
            "dependency", "config", "architecture", "testing",
            "deploy", "performance", "security", "tooling"
          ]},
          "problem": { "type": "string" },
          "solution": { "type": "string" },
          "affected_files": { "type": "array", "items": { "type": "string" } },
          "prevention": { "type": "string" }
        }
      }
    },
    "dependency_graph": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["depends_on", "blocks"],
        "properties": {
          "depends_on": { "type": "array", "items": { "type": "string" } },
          "blocks": { "type": "array", "items": { "type": "string" } },
          "parallelizable": { "type": "boolean" }
        }
      }
    },
    "synced_plans": {
      "type": "array",
      "items": { "type": "string" }
    },
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "milestone"],
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string", "enum": ["claude-code", "codex"] },
          "milestone": { "type": "string" },
          "worktree": { "type": "string" },
          "started_at": { "type": "string", "format": "date-time" },
          "last_heartbeat": { "type": "string", "format": "date-time" }
        }
      }
    },
    "stale_check": {
      "type": "object",
      "properties": {
        "last_run": { "type": "string", "format": "date-time" },
        "stale_files": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## scripts/validate-schema.ts

See `references/harness-scripts.md` for the full TypeScript implementation.
It validates progress.json against the schema using only `node:` built-ins — no
external dependencies. Run via `<pkg-mgr> run validate-schema` or `npx tsx scripts/validate-schema.ts`.

---

## Git Hooks — .husky/

All hooks use `node` or `tsx` — no bash dependency. Cross-platform.

### .husky/pre-commit

```bash
npx lint-staged
npx tsx scripts/file-guard.ts --staged
npx tsx scripts/validate-schema.ts
```

Note: this is a minimal shell wrapper that delegates to Node scripts.
husky requires the hook file itself to be a shell script, but the actual
logic runs in Node.js/TypeScript via `npx tsx`.

### scripts/file-guard.ts --staged mode

Add to file-guard.ts — when called with `--staged`, only check staged files:

```typescript
// Add at the top of file-guard.ts:
import { execSync } from 'node:child_process';

const stagedOnly = process.argv.includes('--staged');

function getFiles(): string[] {
  if (stagedOnly) {
    const staged = execSync('git diff --cached --name-only --diff-filter=ACM', {
      encoding: 'utf-8',
    }).trim();
    return staged
      .split('\n')
      .filter((f) => f && SOURCE_EXTENSIONS.has(extname(f)));
  }
  // ... existing walk() logic for full scan
}
```

### .husky/commit-msg

```bash
npx tsx scripts/check-commit-msg.ts "$1"
```

### scripts/check-commit-msg.ts

```typescript
import { readFileSync } from 'node:fs';
import process from 'node:process';

const msgFile = process.argv[2];
if (!msgFile) {
  console.error('Usage: check-commit-msg.ts <msg-file>');
  process.exit(1);
}

const msg = readFileSync(msgFile, 'utf-8').split('\n')[0].trim();

// Allowed patterns:
// [M1-001] description
// [docs] description
// [scaffold] description
// [fix] description
// [refactor] description
// [ci] description
// [WIP: M1-001] description
// Merge commits (auto-generated by git)
const PATTERN = /^(\[(M\d+-\d+|docs|scaffold|fix|refactor|ci|WIP: M\d+-\d+)\] .+|Merge .+)$/;

if (!PATTERN.test(msg)) {
  console.error('');
  console.error('BLOCKED: Invalid commit message format.');
  console.error('');
  console.error(`  Your message:  ${msg}`);
  console.error('');
  console.error('  Expected formats:');
  console.error('    [M1-001] add user auth middleware');
  console.error('    [docs] update getting-started guide');
  console.error('    [scaffold] initial project setup');
  console.error('    [fix] resolve bcrypt build failure');
  console.error('    [refactor] extract email service module');
  console.error('    [ci] add integration test workflow');
  console.error('    [WIP: M1-003] partial email confirmation');
  console.error('');
  process.exit(1);
}
```

### .husky/pre-push

```bash
npx tsx scripts/validate.ts
```

---

## lint-staged config (package.json)

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ],
    "docs/progress.json": [
      "npx tsx scripts/validate-schema.ts"
    ]
  }
}
```

---

## Assembly Rules

1. Generate `schemas/` directory with `progress.schema.json`
2. Generate all scripts in `scripts/` as `.ts` files (no chmod needed — run via `tsx`)
3. Generate all three husky hooks: `pre-commit`, `commit-msg`, `pre-push`
4. Wire lint-staged to include progress.json schema validation
5. Add `validate-schema` to package.json scripts
6. The commit-msg hook is the enforcement mechanism for the [Mn-id] format —
   agents don't need to "remember" the format, the hook rejects bad messages
7. The pre-commit hook is the enforcement mechanism for the 500-line limit —
   agents don't need to count lines, the hook blocks oversized files
8. The pre-push hook runs full validate — even if an agent somehow skips
   the task-level validate, push catches it
