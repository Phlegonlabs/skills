# Harness CLI — Modular Structure

Single entry point for all harness automation. Replaces 7 separate scripts + manual
JSON editing. Agent runs commands, CLI handles state.

**The CLI itself follows the 500-line rule.** No single module exceeds 500 lines.
The entry point is a thin router; all logic lives in focused sub-modules under
`scripts/harness/`.

**Dependency:** `tsx` (dev dependency, zero-config TS executor)

**Package.json scripts:**
```json
{
  "scripts": {
    "harness": "tsx scripts/harness.ts",
    "lint": "eslint . --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:integration": "vitest run --project integration",
    "test:e2e": "vitest run --project e2e",
    "prepare": "husky"
  }
}
```

Agent uses: `<pkg-mgr> run harness <command>`

---

## Commands

```
harness init              Session boot: sync plans, stale check, register agent, print status
harness init --auto-start Session boot + auto-claim first available task (used by worktree:start)
harness status            Print current milestone, task, blockers, progress
harness next              Find and print the next unblocked task (must be in worktree)
harness start <id>        Claim a task → 🟡 (must be in worktree)
harness validate          Run lint:fix → lint → type-check → test
harness validate:full     + integration + e2e + file-guard
harness done <id>         Complete a task → ✅ + git checkout . (must be in worktree)
harness block <id> <reason>   Mark task blocked → 🚫
harness reset <id>        Revert task to ⬜ (undo start or unblock)
harness learn <cat> <msg>  Log a learning (dependency, config, architecture, etc.)
harness merge-gate        Full gate: validate:full + stale + changelog
harness worktree:start <M-id>   Create branch + worktree + install + init + auto-start
harness worktree:finish <M-id>  Dep check + rebase + merge + push + cleanup (from main root)
harness worktree:rebase          Rebase current worktree onto latest main
harness worktree:status          Show all worktrees, agents, merge readiness
harness stale-check       Detect stale docs, env, plans
harness file-guard        Check 500-line limit (--staged for hooks)
harness changelog [from] [to]  Generate release notes
harness schema            Validate progress.json against schema
harness recover           Auto-detect and fix milestone board inconsistencies
```

---

## Modular File Structure

```
scripts/
├── harness.ts                  # Entry point: imports + command router (~85 lines)
├── check-commit-msg.ts         # Commit message validator (standalone — needs msg file path)
└── harness/
    ├── config.ts               # Constants, paths, colors, output helpers (~40 lines)
    ├── types.ts                # All interfaces: Progress, AgentEntry, WorktreeInfo (~60 lines)
    ├── state.ts                # loadProgress, saveProgress, loadPlan, savePlan (~35 lines)
    ├── plan-utils.ts           # Row-level PLAN.md table parser — shared by tasks/quality/recovery (~330 lines)
    ├── recovery.ts             # installWithRetry + recoverMilestoneBoard (~150 lines)
    ├── worktree.ts             # Worktree detection, enforcement, agent lifecycle, worktree:* commands (~410 lines)
    ├── tasks.ts                # init, status, next, start, done, block, reset (~480 lines)
    ├── validate.ts             # validate, validate:full, file-guard (~120 lines)
    └── quality.ts              # merge-gate, stale-check, sync-plans, schema, changelog (~270 lines)
```

Every module stays well under 500 lines. When any module approaches ~300 lines,
proactively split again. This is the same principle the CLI enforces on project code.

---

## Implementation — Module by Module

### scripts/harness/config.ts

```typescript
// Shared constants and output helpers — imported by every other module.
import process from 'node:process';

export const PKG = process.env.PKG_MGR ?? 'pnpm';
export const PROGRESS_FILE = 'docs/progress.json';
export const PLAN_FILE = 'docs/PLAN.md';
export const SCHEMA_FILE = 'schemas/progress.schema.json';
export const PLANS_DIR = 'docs/exec-plans/active';
export const FILE_LIMIT = 500;
export const SOURCE_EXTS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.vue', '.svelte']);
export const IGNORE_DIRS = new Set(['node_modules', 'dist', 'build', '.next', 'out', 'coverage', '.git']);
export const STALE_AGENT_MS = 2 * 60 * 60 * 1000; // 2 hours

// ─── Colors ──────────────────────────────────────────────────────────────────
export const R = '\x1b[31m', G = '\x1b[32m', Y = '\x1b[33m', B = '\x1b[34m', D = '\x1b[2m', N = '\x1b[0m';
export const ok = (m: string) => console.log(`${G}✓${N} ${m}`);
export const warn = (m: string) => console.warn(`${Y}⚠${N} ${m}`);
export const fail = (m: string) => { console.error(`${R}✗${N} ${m}`); process.exit(1); };
export const step = (m: string) => console.log(`${Y}▶${N} ${m}`);
export const info = (m: string) => console.log(`${B}ℹ${N} ${m}`);
```

### scripts/harness/types.ts

```typescript
// All shared interfaces. No runtime code — types only.

export interface Progress {
  project: string;
  last_updated: string;
  last_agent: string;
  current_milestone: {
    id: string; name: string; branch: string; worktree: string;
    status: string; tasks_total: number; tasks_done: number;
    tasks_in_progress: number; tasks_blocked: number; tasks_remaining: number;
  } | null;
  current_task: {
    id: string; story: string; description: string;
    status: string; started_at: string; files_touched: string[]; notes: string;
  } | null;
  active_milestones: ActiveMilestone[];
  completed_milestones: Array<{ id: string; name: string; completed_at: string; tag?: string }>;
  blockers: Array<{ task_id: string; description: string; error?: string; added_at: string }>;
  learnings: Array<Record<string, unknown>>;
  dependency_graph: Record<string, { depends_on: string[]; blocks: string[] }>;
  synced_plans: string[];
  agents: AgentEntry[];
  [key: string]: unknown;
}

export interface ActiveMilestone {
  id: string;
  title: string;
  status?: string;
  branch?: string;
  worktree?: string;
  depends_on?: string[];
  started_at?: string;
  completed_at?: string | null;
  tasks?: Array<Record<string, unknown>>;
  [k: string]: unknown;
}

export interface AgentEntry {
  id: string;
  milestone: string | null;
  worktree: string;
  branch: string;
  started_at: string;
  heartbeat: string;
}

export interface WorktreeInfo {
  isWorktree: boolean;
  cwd: string;
  mainRoot: string;
  currentBranch: string;
  milestoneId: string | null;  // e.g. "milestone/m1" → "M1"
}
```

### scripts/harness/state.ts

```typescript
// Read/write progress.json and PLAN.md — thin wrappers, no business logic.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { PROGRESS_FILE, PLAN_FILE, fail } from './config.js';
import type { Progress } from './types.js';

export function loadProgress(): Progress {
  if (!existsSync(PROGRESS_FILE)) fail(`${PROGRESS_FILE} not found`);
  return JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
}

export function saveProgress(p: Progress): void {
  p.last_updated = new Date().toISOString();
  writeFileSync(PROGRESS_FILE, JSON.stringify(p, null, 2) + '\n');
}

export function loadPlan(): string {
  if (!existsSync(PLAN_FILE)) fail(`${PLAN_FILE} not found`);
  return readFileSync(PLAN_FILE, 'utf-8');
}

export function savePlan(content: string): void {
  writeFileSync(PLAN_FILE, content);
}
```

### scripts/harness/plan-utils.ts

```typescript
// Row-level PLAN.md table parser.
// Detects Status/Commit column positions from the header row,
// then operates on the correct column — never scans across the whole row.

// ─── Types ───────────────────────────────────────────────────────────────────

export interface TableLayout {
  /** Index in the raw parts[] array (line.split('|')) for Status column. */
  statusIdx: number;
  /** Index in the raw parts[] array for Commit column (null if absent). */
  commitIdx: number | null;
  /** Index in the raw parts[] array for Task/Description column. */
  descIdx: number | null;
}

export interface TaskRow {
  lineIndex: number;
  taskId: string;
  statusEmoji: string;      // ⬜ | 🟡 | ✅ | 🚫
  statusText: string;       // full cell text, e.g. "⬜ Todo"
  description: string;
  rawLine: string;
}

// ─── STATUS_EMOJIS ───────────────────────────────────────────────────────────

export const STATUS = {
  TODO:    '⬜',
  WIP:     '🟡',
  DONE:    '✅',
  BLOCKED: '🚫',
} as const;

export type StatusEmoji = typeof STATUS[keyof typeof STATUS];

// ─── Layout detection ────────────────────────────────────────────────────────
// Scans the plan text for the first header row containing "Status" and caches
// the column positions. All task tables in a single PLAN.md use the same layout.

let cachedLayout: TableLayout | null = null;
let cachedPlanHash = '';

function hashPlan(plan: string): string {
  return `${String(plan.length)}:${plan.slice(0, 200)}`;
}

export function detectLayout(plan: string): TableLayout {
  const h = hashPlan(plan);
  if (cachedLayout && cachedPlanHash === h) return cachedLayout;

  const lines = plan.split('\n');
  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    const parts = line.split('|');
    const lower = parts.map((p) => p.trim().toLowerCase());

    const statusIdx = lower.findIndex((c) => c === 'status');
    if (statusIdx === -1) continue;

    cachedLayout = {
      statusIdx,
      commitIdx: lower.findIndex((c) => c === 'commit') > 0
        ? lower.findIndex((c) => c === 'commit')
        : null,
      descIdx: lower.findIndex((c) => c === 'task' || c === 'description') > 0
        ? lower.findIndex((c) => c === 'task' || c === 'description')
        : null,
    };
    cachedPlanHash = h;
    return cachedLayout;
  }

  // Fallback: harness default
  // | Task ID(1) | Story(2) | Task(3) | Done When(4) | Status(5) | Commit(6) |
  cachedLayout = { statusIdx: 5, commitIdx: 6, descIdx: 3 };
  cachedPlanHash = h;
  return cachedLayout;
}

export function invalidateLayoutCache(): void {
  cachedLayout = null;
  cachedPlanHash = '';
}

// ─── Row parsing ─────────────────────────────────────────────────────────────

/**
 * Parse all task rows from PLAN.md.
 * @param milestoneFilter  e.g. "M1" — only return tasks starting with "M1-"
 */
export function parsePlanTaskRows(plan: string, milestoneFilter?: string): TaskRow[] {
  const layout = detectLayout(plan);
  const lines = plan.split('\n');
  const rows: TaskRow[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.startsWith('|')) continue;

    const parts = line.split('|');
    if (parts.length < layout.statusIdx + 1) continue;

    // parts[1] = first column = Task ID
    const taskId = (parts[1] ?? '').trim();
    if (!/^M\d+-\d+$/.test(taskId)) continue;

    if (milestoneFilter && !taskId.startsWith(`${milestoneFilter}-`)) continue;

    const statusCell = (parts[layout.statusIdx] ?? '').trim();
    const emojiMatch = statusCell.match(/^(⬜|🟡|✅|🚫)/);

    const desc = layout.descIdx !== null
      ? (parts[layout.descIdx] ?? '').trim()
      : '';

    rows.push({
      lineIndex: i,
      taskId,
      statusEmoji: (emojiMatch?.[1] ?? '') as string,
      statusText: statusCell,
      description: desc,
      rawLine: line,
    });
  }

  return rows;
}

// ─── Status replacement ─────────────────────────────────────────────────────

export interface ReplaceResult {
  plan: string;
  changed: boolean;
}

/**
 * Replace the status emoji for a specific task in PLAN.md.
 *
 * @param plan         Full PLAN.md content
 * @param taskId       e.g. "M1-003"
 * @param fromEmoji    Emoji to replace (or null = match any)
 * @param toEmoji      Emoji to set
 * @param commitHash   Optional — fills the Commit column if present
 */
export function replaceTaskStatus(
  plan: string,
  taskId: string,
  fromEmoji: StatusEmoji | null,
  toEmoji: StatusEmoji,
  commitHash?: string,
): ReplaceResult {
  const layout = detectLayout(plan);
  const lines = plan.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.startsWith('|')) continue;

    const parts = line.split('|');
    if (parts.length < layout.statusIdx + 1) continue;

    const cellTaskId = (parts[1] ?? '').trim();
    if (cellTaskId !== taskId) continue;

    // Found the row — check status column
    const statusCell = (parts[layout.statusIdx] ?? '').trim();

    if (fromEmoji !== null && !statusCell.startsWith(fromEmoji)) {
      // Status doesn't match — don't change
      return { plan, changed: false };
    }

    // Replace emoji in the status cell, preserving any suffix text
    const newStatus = fromEmoji !== null
      ? statusCell.replace(fromEmoji, toEmoji)
      : toEmoji;

    parts[layout.statusIdx] = preservePadding(parts[layout.statusIdx], newStatus);

    // Optionally fill commit column
    if (commitHash && layout.commitIdx !== null && layout.commitIdx < parts.length) {
      const commitCell = (parts[layout.commitIdx] ?? '').trim();
      if (commitCell === '—' || commitCell === '-' || commitCell === '') {
        parts[layout.commitIdx] = preservePadding(
          parts[layout.commitIdx],
          `\`${commitHash}\``,
        );
      }
    }

    lines[i] = parts.join('|');
    return { plan: lines.join('\n'), changed: true };
  }

  return { plan, changed: false };
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function preservePadding(rawCell: string, newContent: string): string {
  const leadMatch = rawCell.match(/^(\s+)/);
  const trailMatch = rawCell.match(/(\s+)$/);
  const lead = leadMatch ? leadMatch[1] : ' ';
  const trail = trailMatch ? trailMatch[1] : ' ';
  return `${lead}${newContent}${trail}`;
}

/**
 * Get the status emoji of a specific task. Returns null if not found.
 */
export function getTaskStatus(plan: string, taskId: string): StatusEmoji | null {
  const layout = detectLayout(plan);
  const lines = plan.split('\n');

  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    const parts = line.split('|');
    if (parts.length < layout.statusIdx + 1) continue;
    if ((parts[1] ?? '').trim() !== taskId) continue;

    const statusCell = (parts[layout.statusIdx] ?? '').trim();
    const m = statusCell.match(/^(⬜|🟡|✅|🚫)/);
    return (m?.[1] ?? null) as StatusEmoji | null;
  }

  return null;
}

/**
 * Count tasks by status for a given milestone.
 */
export function countTaskStatuses(plan: string, milestoneId: string): {
  todo: number; wip: number; done: number; blocked: number; total: number;
} {
  const rows = parsePlanTaskRows(plan, milestoneId);
  const result = { todo: 0, wip: 0, done: 0, blocked: 0, total: rows.length };

  for (const row of rows) {
    switch (row.statusEmoji) {
      case STATUS.TODO:    result.todo++; break;
      case STATUS.WIP:     result.wip++; break;
      case STATUS.DONE:    result.done++; break;
      case STATUS.BLOCKED: result.blocked++; break;
    }
  }

  return result;
}

/**
 * Check if a task exists in PLAN.md (by Task ID in column 1).
 */
export function taskExistsInPlan(plan: string, taskId: string): boolean {
  const lines = plan.split('\n');
  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    const parts = line.split('|');
    if ((parts[1] ?? '').trim() === taskId) return true;
  }
  return false;
}

// ─── Milestone header parsing ────────────────────────────────────────────────
// Scans PLAN.md for `### M<n>: <title>` blocks and extracts metadata.
// Used by worktree:start to backfill missing active_milestones.

export interface MilestoneHeader {
  id: string;           // e.g. "M1"
  title: string;        // e.g. "Foundation"
  status: string;       // e.g. "🟡 In Progress" or "⬜ Not Started"
  branch: string;       // e.g. "milestone/m1"
  dependsOn: string[];  // e.g. ["M1"]
}

/**
 * Parse milestone header blocks from PLAN.md.
 *
 * Expected format:
 * ```
 * ### M1: Foundation (Target: Week 1-2)
 * **Status:** 🟡 In Progress
 * **Branch:** `milestone/m1`
 * **Depends on:** M1, M2
 * ```
 */
export function parseMilestoneHeaders(plan: string): MilestoneHeader[] {
  const results: MilestoneHeader[] = [];
  const lines = plan.split('\n');

  for (let i = 0; i < lines.length; i++) {
    // Match: ### M1: Foundation (Target: ...)
    const headerMatch = lines[i].match(/^###\s+(M\d+):\s*(.+?)(?:\s*\(.*\))?\s*$/);
    if (!headerMatch) continue;

    const id = headerMatch[1];
    const title = headerMatch[2].trim();
    let status = '';
    let branch = `milestone/${id.toLowerCase()}`;
    const dependsOn: string[] = [];

    // Scan the next ~10 lines for metadata fields
    for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
      const line = lines[j];
      // Stop at next heading or task table
      if (line.startsWith('###') || line.startsWith('| Task')) break;

      const statusMatch = line.match(/\*\*Status:\*\*\s*(.+)/);
      if (statusMatch) status = statusMatch[1].trim();

      const branchMatch = line.match(/\*\*Branch:\*\*\s*`?([^`\s]+)`?/);
      if (branchMatch) branch = branchMatch[1];

      const depsMatch = line.match(/\*\*Depends\s+on:\*\*\s*(.+)/i);
      if (depsMatch) {
        const depsText = depsMatch[1].trim();
        if (depsText.toLowerCase() !== 'none' && depsText !== '—') {
          dependsOn.push(
            ...depsText.split(/[,\s]+/).filter((d) => /^M\d+$/.test(d))
          );
        }
      }
    }

    results.push({ id, title, status, branch, dependsOn });
  }

  return results;
}

```

### scripts/harness/recovery.ts

```typescript
// Milestone board recovery and install retry logic.
// Split from worktree.ts to keep both modules under 500 lines.
import { execSync } from 'node:child_process';
import process from 'node:process';
import { PKG, ok, warn, step, info } from './config.js';
import type { Progress } from './types.js';
import { loadProgress, saveProgress, loadPlan, savePlan } from './state.js';
import { STATUS, parsePlanTaskRows } from './plan-utils.js';

// ─── Install with retry (Windows EBUSY fix) ─────────────────────────────────

export function installWithRetry(cwd: string, maxAttempts = 3): boolean {
  const isWindows = process.platform === 'win32';
  const delayMs = isWindows ? 5000 : 2000;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const useForce = attempt > 1;
    const cmd = `${PKG} install${useForce ? ' --force' : ''}`;

    step(`Installing dependencies (attempt ${String(attempt)}/${String(maxAttempts)})...`);
    try {
      execSync(cmd, { cwd, shell: true, stdio: 'inherit' });
      ok('Dependencies installed successfully.');
      return true;
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      const isEBUSY = errMsg.includes('EBUSY') || errMsg.includes('resource busy');
      const isLock = errMsg.includes('EPERM') || errMsg.includes('lock') || errMsg.includes('EACCES');

      if (attempt < maxAttempts && (isEBUSY || isLock || isWindows)) {
        warn(
          `Install attempt ${String(attempt)} failed` +
          `${isEBUSY ? ' (EBUSY — file locked by another process)' : ''}` +
          `${isLock ? ' (EPERM/lock — permission or lock conflict)' : ''}.\n` +
          `  Waiting ${String(delayMs / 1000)}s before retry with --force...`
        );

        try {
          if (isWindows) {
            execSync(`ping -n ${String(Math.ceil(delayMs / 1000) + 1)} 127.0.0.1 >nul`, { shell: true, stdio: 'pipe' });
          } else {
            execSync(`sleep ${String(delayMs / 1000)}`, { shell: true, stdio: 'pipe' });
          }
        } catch { /* sleep failed, continue anyway */ }
      } else if (attempt < maxAttempts) {
        warn(`Install attempt ${String(attempt)} failed. Retrying with --force...`);
      } else {
        warn(
          `Install failed after ${String(maxAttempts)} attempts.\n` +
          `  Try manually:\n` +
          `    cd "${cwd}"\n` +
          `    ${PKG} install --force\n` +
          (isWindows
            ? `\n  Windows tips:\n` +
              `    • Close VS Code / editors that may lock node_modules\n` +
              `    • Close any terminal sessions in the worktree directory\n` +
              `    • Run: taskkill /im node.exe /f (kill stale node processes)\n` +
              `    • Then retry: ${PKG} install --force`
            : '')
        );
        return false;
      }
    }
  }
  return false;
}

// ─── Milestone board recovery ───────────────────────────────────────────────
// Scans PLAN.md + progress.json for inconsistencies.
// If all tasks in a milestone are ✅ but it's still in active_milestones,
// auto-move it to completed_milestones.

export function recoverMilestoneBoard(p: Progress): { recovered: number; ids: string[] } {
  const result = { recovered: 0, ids: [] as string[] };

  let plan: string;
  try { plan = loadPlan(); } catch { return result; }

  const completedIds = new Set(p.completed_milestones.map((m) => m.id));
  const toRecover: number[] = [];

  for (let i = 0; i < p.active_milestones.length; i++) {
    const ms = p.active_milestones[i];
    if (completedIds.has(ms.id)) continue;

    // Row-level: parse tasks for this milestone by Status column
    const rows = parsePlanTaskRows(plan, ms.id);
    if (rows.length === 0) continue;

    const allDone = rows.every((r) => r.statusEmoji === STATUS.DONE);
    if (!allDone) continue;

    // Verify git branch is merged or gone
    let branchExists = false;
    const branch = ms.branch ?? `milestone/${ms.id.toLowerCase()}`;
    try {
      execSync(`git rev-parse --verify "${branch}" 2>/dev/null`, { shell: true, stdio: 'pipe' });
      branchExists = true;
    } catch { /* branch doesn't exist — already merged/deleted */ }

    let branchMerged = false;
    if (branchExists) {
      try {
        const merged = execSync('git branch --merged main', { encoding: 'utf-8', shell: true });
        branchMerged = merged.includes(branch);
      } catch { /* can't check */ }
    }

    if (!branchExists || branchMerged) {
      toRecover.push(i);
      step(`Auto-recovering ${ms.id}: all ${String(rows.length)} tasks ✅, branch ${branchExists ? 'merged' : 'removed'}`);
    } else {
      info(
        `${ms.id} has all tasks ✅ but branch '${branch}' exists and is not merged.\n` +
        `  Run: ${PKG} run harness worktree:finish ${ms.id}`
      );
    }
  }

  // Move recovered milestones from active → completed (reverse to preserve indices)
  for (const idx of toRecover.reverse()) {
    const ms = p.active_milestones.splice(idx, 1)[0];
    p.completed_milestones.push({
      id: ms.id,
      name: ms.title,
      completed_at: new Date().toISOString(),
    });
    result.recovered++;
    result.ids.push(ms.id);

    // Update PLAN.md milestone header status
    try {
      let currentPlan = loadPlan();
      const statusRe = new RegExp(
        `(### ${ms.id}:[^\\n]*\\n\\*\\*Status:\\*\\*\\s*)(?:⬜[^\\n]*|🟡[^\\n]*)`,
      );
      const updated = currentPlan.replace(statusRe, `$1✅ Complete (auto-recovered)`);
      if (updated !== currentPlan) savePlan(updated);
    } catch { /* best effort */ }
  }

  if (result.recovered > 0) {
    p.current_milestone = p.active_milestones[0] ? { ...p.active_milestones[0] } as any : null;
    saveProgress(p);
  }

  return result;
}
```

### scripts/harness/worktree.ts

```typescript
// Worktree detection, enforcement, agent lifecycle, and all worktree:* commands.
import { execSync } from 'node:child_process';
import { resolve } from 'node:path';
import { hostname } from 'node:os';
import process from 'node:process';
import { PKG, STALE_AGENT_MS, ok, warn, fail, step, info, R, G, Y, B, N } from './config.js';
import type { Progress, ActiveMilestone, WorktreeInfo } from './types.js';
import { loadProgress, saveProgress, loadPlan, savePlan } from './state.js';
import { installWithRetry, recoverMilestoneBoard } from './recovery.js';
import { parseMilestoneHeaders, countTaskStatuses } from './plan-utils.js';

// ─── Cross-platform path normalization ──────────────────────────────────────
// Windows resolve() → "C:\Users\foo\project"
// Git for Windows worktree list → "C:/Users/foo/project"
// Git Bash/MSYS worktree list → "/c/Users/foo/project"

function normalizePath(p: string): string {
  let s = resolve(p);
  s = s.replace(/\\/g, '/');
  s = s.replace(/\/$/, '');
  s = s.replace(/^([A-Z]):\//, (_, d) => `${(d as string).toLowerCase()}:/`);
  s = s.replace(/^\/([a-z])\//, (_, d) => `${d as string}:/`);
  return s;
}

// ─── Worktree detection ──────────────────────────────────────────────────────

export function getMainRoot(): string {
  const wtList = execSync('git worktree list --porcelain', { encoding: 'utf-8', shell: true });
  return wtList.split('\n')[0].replace('worktree ', '').trim();
}

export function getWorktreeInfo(): WorktreeInfo {
  const cwd = process.cwd();
  const mainRoot = getMainRoot();
  const isWorktree = normalizePath(cwd) !== normalizePath(mainRoot);

  let currentBranch = '';
  try {
    currentBranch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf-8', shell: true }).trim();
  } catch { /* detached HEAD */ }

  let milestoneId: string | null = null;
  const branchMatch = currentBranch.match(/^milestone\/(m\d+)$/i);
  if (branchMatch) milestoneId = branchMatch[1].toUpperCase();

  return { isWorktree, cwd, mainRoot, currentBranch, milestoneId };
}

export function enforceWorktree(command: string): WorktreeInfo {
  const wt = getWorktreeInfo();
  if (!wt.isWorktree) {
    fail(
      `'${command}' must run inside a milestone worktree, not on main.\n\n` +
      `  You are in: ${wt.cwd} (main repo root)\n\n` +
      `  To start a milestone worktree:\n` +
      `    ${PKG} run harness worktree:start <M-id>\n` +
      `    cd ../<project>-<m-id>\n` +
      `    ${PKG} install\n` +
      `    ${PKG} run harness init`
    );
  }
  return wt;
}

// ─── Agent lifecycle ─────────────────────────────────────────────────────────

export function getAgentId(): string {
  if (process.env.HARNESS_AGENT_ID) return process.env.HARNESS_AGENT_ID;
  return `agent-${hostname().slice(0, 12)}-${String(process.pid)}`;
}

export function registerAgent(p: Progress, wt: WorktreeInfo): void {
  const agentId = getAgentId();
  const now = new Date().toISOString();
  p.agents = p.agents.filter((a) => a.id !== agentId && a.worktree !== wt.cwd);
  p.agents.push({
    id: agentId, milestone: wt.milestoneId, worktree: wt.cwd,
    branch: wt.currentBranch, started_at: now, heartbeat: now,
  });
}

export function updateHeartbeat(p: Progress): void {
  const agent = p.agents.find((a) => a.id === getAgentId());
  if (agent) agent.heartbeat = new Date().toISOString();
}

export function deregisterAgent(p: Progress, worktreePath: string): void {
  p.agents = p.agents.filter((a) => a.worktree !== worktreePath);
}

// ─── PLAN.md milestone backfill ─────────────────────────────────────────────

function backfillMilestone(p: Progress, milestoneId: string): ActiveMilestone | null {
  let plan: string;
  try { plan = loadPlan(); } catch { return null; }

  const headers = parseMilestoneHeaders(plan);
  const header = headers.find((h) => h.id === milestoneId);
  if (!header) return null;

  const counts = countTaskStatuses(plan, milestoneId);
  if (counts.total === 0) return null;

  const ms: ActiveMilestone = {
    id: milestoneId, title: header.title,
    status: header.status || '🟡 In Progress',
    branch: header.branch,
    depends_on: header.dependsOn.length > 0 ? header.dependsOn : undefined,
    started_at: new Date().toISOString(),
  };

  p.active_milestones = p.active_milestones ?? [];
  p.active_milestones.push(ms);
  p.current_milestone = {
    id: milestoneId, name: header.title, branch: header.branch, worktree: '',
    status: header.status || '🟡 In Progress',
    tasks_total: counts.total, tasks_done: counts.done,
    tasks_in_progress: counts.wip, tasks_blocked: counts.blocked,
    tasks_remaining: counts.total - counts.done,
  };
  saveProgress(p);
  ok(`Backfilled ${milestoneId} from PLAN.md (${String(counts.total)} tasks, ${String(counts.done)} done)`);
  return ms;
}

// ─── worktree:start ──────────────────────────────────────────────────────────

export function cmdWorktreeStart(milestoneId: string): void {
  if (!milestoneId) { fail('Usage: harness worktree:start <milestone-id>  (e.g. M1)'); return; }

  const p = loadProgress();

  const recoveryResult = recoverMilestoneBoard(p);
  if (recoveryResult.recovered > 0) {
    ok(`Auto-recovered ${String(recoveryResult.recovered)} milestone(s): ${recoveryResult.ids.join(', ')}`);
  }

  // Find or backfill milestone
  let ms = (p.active_milestones ?? []).find((m) => m.id === milestoneId);
  if (!ms) {
    if (p.completed_milestones.some((m) => m.id === milestoneId)) {
      fail(`Milestone ${milestoneId} is already completed.`); return;
    }
    step(`${milestoneId} not in progress.json. Scanning PLAN.md...`);
    ms = backfillMilestone(p, milestoneId) ?? undefined;
    if (!ms) {
      fail(
        `Milestone ${milestoneId} not found in progress.json or PLAN.md.\n` +
        `  Make sure PLAN.md has a "### ${milestoneId}: <title>" section with tasks.`
      );
      return;
    }
  }

  // Agent claim check
  const now = Date.now();
  const existingAgent = p.agents.find(
    (a) => a.milestone === milestoneId && (now - new Date(a.heartbeat).getTime()) < STALE_AGENT_MS
  );
  if (existingAgent) {
    warn(
      `Milestone ${milestoneId} is already claimed by agent ${existingAgent.id}\n` +
      `  Worktree: ${existingAgent.worktree}\n` +
      `  Last heartbeat: ${existingAgent.heartbeat}\n\n` +
      `  If that agent is dead, wait for heartbeat to expire (>2h) or remove from progress.json.`
    );
    process.exit(1); return;
  }

  const branch = ms.branch ?? `milestone/${milestoneId.toLowerCase()}`;
  const rootDir = getMainRoot();
  const worktreeDir = `${rootDir}/../${p.project ?? 'project'}-${milestoneId.toLowerCase()}`;
  const absWorktree = resolve(worktreeDir);
  const normalAbs = normalizePath(absWorktree);

  // Check if worktree already exists (normalized comparison)
  const existingList = execSync('git worktree list', { encoding: 'utf-8', shell: true });
  const wtAlreadyExists = existingList.split('\n')
    .some((line) => normalizePath(line.split(/\s+/)[0] ?? '') === normalAbs);

  if (wtAlreadyExists) {
    info(`Worktree already exists: ${absWorktree}`);
    ms.branch = branch;
    ms.worktree = absWorktree;
    saveProgress(p);
    ok(`Restored milestone context for ${milestoneId}`);

    step('Auto-initializing in existing worktree...');
    try {
      execSync(`${PKG} run harness init --auto-start`, {
        cwd: absWorktree, shell: true, stdio: 'inherit',
      });
    } catch {
      warn(`Auto-init failed. Run manually:\n  cd "${absWorktree}"\n  ${PKG} run harness init`);
    }
    return;
  }

  step(`Creating branch ${branch}...`);
  try { execSync(`git branch ${branch} 2>/dev/null || true`, { shell: true, stdio: 'inherit' }); }
  catch { /* branch may already exist */ }

  step(`Adding worktree at ${absWorktree}...`);
  execSync(`git worktree add "${absWorktree}" "${branch}"`, { shell: true, stdio: 'inherit' });

  ms.branch = branch;
  ms.worktree = absWorktree;
  saveProgress(p);
  ok(`Worktree ready: ${absWorktree}`);

  const installOk = installWithRetry(absWorktree);

  if (installOk) {
    step('Auto-initializing harness session...');
    try {
      execSync(`${PKG} run harness init --auto-start`, {
        cwd: absWorktree, shell: true, stdio: 'inherit',
      });
    } catch {
      warn(`Auto-init failed. Run manually:\n  cd "${absWorktree}"\n  ${PKG} run harness init`);
    }
  } else {
    console.log(`\nNext:\n  cd "${absWorktree}"\n  ${PKG} install --force\n  ${PKG} run harness init`);
  }
}

// ─── worktree:finish ─────────────────────────────────────────────────────────

export function cmdWorktreeFinish(milestoneId: string, validateFn: (full: boolean) => void): void {
  if (!milestoneId) { fail('Usage: harness worktree:finish <milestone-id>  (e.g. M1)'); return; }

  const p = loadProgress();
  const ms = (p.active_milestones ?? []).find((m) => m.id === milestoneId);
  if (!ms) { fail(`Milestone ${milestoneId} not found in active_milestones`); return; }

  const branch = ms.branch ?? `milestone/${milestoneId.toLowerCase()}`;
  const worktreeDir = ms.worktree ?? '';
  const rootDir = getMainRoot();

  if (normalizePath(process.cwd()) !== normalizePath(rootDir)) {
    fail(`Run worktree:finish from the main repo root:\n  cd "${rootDir}"\n  ${PKG} run harness worktree:finish ${milestoneId}`);
    return;
  }

  // Dependency order check
  const completedIds = new Set(p.completed_milestones.map((m) => m.id));
  const milestoneDeps = ms.depends_on ?? [];
  const graph = p.dependency_graph ?? {};
  const crossMilestoneDeps = new Set<string>();

  for (const [taskId, deps] of Object.entries(graph)) {
    if (!taskId.startsWith(`${milestoneId}-`)) continue;
    for (const depId of deps.depends_on) {
      const depMs = depId.match(/^(M\d+)-/)?.[1];
      if (depMs && depMs !== milestoneId) crossMilestoneDeps.add(depMs);
    }
  }

  const allDeps = [...new Set([...milestoneDeps, ...crossMilestoneDeps])];
  let unmergedDeps = allDeps.filter((d) => !completedIds.has(d));

  if (unmergedDeps.length > 0) {
    const recovery = recoverMilestoneBoard(p);
    if (recovery.recovered > 0) {
      ok(`Auto-recovered ${String(recovery.recovered)} milestone(s): ${recovery.ids.join(', ')}`);
      const nowCompleted = new Set(p.completed_milestones.map((m) => m.id));
      unmergedDeps = allDeps.filter((d) => !nowCompleted.has(d));
    }
    if (unmergedDeps.length > 0) {
      fail(
        `Cannot merge ${milestoneId} — dependent milestone(s) not yet merged:\n` +
        unmergedDeps.map((d) => `  ${R}•${N} ${d} must be merged first`).join('\n') +
        `\n\nMerge order must follow dependency order.`
      );
      return;
    }
    ok('Dependencies resolved after auto-recovery. Continuing...');
  }

  // Rebase
  step(`Rebasing ${branch} onto latest main...`);
  try {
    try { execSync('git fetch origin main 2>/dev/null', { shell: true, stdio: 'pipe' }); } catch { /* offline */ }
    execSync(`git rebase main "${branch}" 2>&1`, { shell: true, stdio: 'pipe' });
    ok(`${branch} rebased onto main — no conflicts.`);
  } catch {
    try { execSync('git rebase --abort', { shell: true, stdio: 'pipe' }); } catch { /* clean */ }
    warn(`Rebase of ${branch} onto main has conflicts.`);
    try {
      const mt = execSync(`git merge-tree $(git merge-base main "${branch}") main "${branch}"`, { encoding: 'utf-8', shell: true });
      if (mt.includes('changed in both')) {
        console.log(`\n${Y}Conflicting files:${N}`);
        mt.split('\n').filter((l: string) => l.includes('changed in both')).forEach((l: string) => console.log(`  ${R}•${N} ${l.trim()}`));
      }
    } catch { /* merge-tree may not work */ }
    warn(`\nAutomatic rebase failed. Options:\n\n  Option A — Manual rebase:\n    cd "${worktreeDir}"\n    git rebase main\n    # resolve conflicts, then: git rebase --continue\n\n  Option B — Force merge:\n    ${PKG} run harness worktree:finish ${milestoneId} --force\n`);
    if (!process.argv.includes('--force')) { process.exit(1); return; }
    warn('--force flag detected. Proceeding with merge...');
  }

  // Merge
  step(`Merging ${branch} into main...`);
  try {
    execSync(`git merge --no-ff "${branch}" -m "merge: ${milestoneId} complete"`, { shell: true, stdio: 'inherit' });
  } catch {
    fail(`Merge conflict. Resolve manually:\n  git status → edit conflicts → git add -A → git commit\n  ${PKG} run harness validate:full`);
    return;
  }

  step('Running full validation on main...');
  validateFn(true);

  // Update PLAN.md
  step('Updating PLAN.md milestone status...');
  try {
    let plan = loadPlan();
    const statusRe = new RegExp(`(### ${milestoneId}:[^\\n]*\\n\\*\\*Status:\\*\\*\\s*)(?:⬜[^\\n]*|🟡[^\\n]*|In Progress|Not Started)`);
    const updated = plan.replace(statusRe, `$1✅ Complete`);
    if (updated !== plan) { savePlan(updated); ok(`PLAN.md: ${milestoneId} marked ✅ Complete`); }
  } catch { /* best-effort */ }

  // Cleanup
  deregisterAgent(p, worktreeDir);
  step('Removing worktree...');
  if (worktreeDir) {
    try { execSync(`git worktree remove "${worktreeDir}" --force`, { shell: true, stdio: 'inherit' }); }
    catch { warn(`Could not remove worktree at ${worktreeDir} — remove manually`); }
  }
  step('Deleting milestone branch...');
  try { execSync(`git branch -d "${branch}"`, { shell: true, stdio: 'inherit' }); }
  catch { warn(`Branch ${branch} not deleted`); }

  const idx = p.active_milestones.findIndex((m) => m.id === milestoneId);
  if (idx !== -1) {
    const completed = p.active_milestones.splice(idx, 1)[0];
    p.completed_milestones.push({ id: completed.id, name: completed.title, completed_at: new Date().toISOString() });
    p.current_milestone = p.active_milestones[0] ? { ...p.active_milestones[0] } as any : null;
    saveProgress(p);
  }

  ok(`${milestoneId} merged, worktree removed, progress updated.`);

  step('Pushing main to remote...');
  try { execSync('git push origin main', { shell: true, stdio: 'inherit' }); ok('Pushed to remote.'); }
  catch { warn('Could not push to remote. Push manually: git push origin main'); }

  if (p.active_milestones.length > 0) {
    const nextMs = p.active_milestones[0];
    console.log(`\n${G}Next milestone:${N} ${nextMs.id} — ${nextMs.title}`);
    console.log(`  ${PKG} run harness worktree:start ${nextMs.id}`);
    info('worktree:start will auto-install, init, and start the first task.');
  } else {
    info('All milestones complete! Next: git tag v<version> && git push --tags');
  }
}

// ─── worktree:rebase ─────────────────────────────────────────────────────────

export function cmdWorktreeRebase(): void {
  const wt = enforceWorktree('worktree:rebase');
  step('Fetching latest main...');
  try { execSync('git fetch origin main 2>/dev/null', { shell: true, stdio: 'pipe' }); } catch { /* offline */ }
  step(`Rebasing ${wt.currentBranch} onto main...`);
  try {
    execSync('git rebase main', { shell: true, stdio: 'inherit' });
    ok('Rebase successful — no conflicts.');
    info(`Run: ${PKG} run harness validate`);
  } catch {
    warn(`Rebase has conflicts. Resolve:\n  git status → edit → git add → git rebase --continue\n  Or abort: git rebase --abort\n  After resolving: ${PKG} run harness validate`);
    process.exit(1);
  }
}

// ─── worktree:status ─────────────────────────────────────────────────────────

export function cmdWorktreeList(): void {
  console.log(`\n${B}═══ Worktree Status ═══${N}\n`);
  const wtList = execSync('git worktree list', { encoding: 'utf-8', shell: true }).trim();
  step('Git worktrees:');
  console.log(wtList.split('\n').map((l: string) => `  ${l}`).join('\n'));

  const p = loadProgress();
  const now = Date.now();
  if (p.agents.length > 0) {
    console.log(`\n${Y}Registered agents:${N}`);
    for (const a of p.agents) {
      const age = now - new Date(a.heartbeat).getTime();
      const stale = age > STALE_AGENT_MS;
      const ageStr = age < 60000 ? '<1m' : age < 3600000 ? `${String(Math.floor(age / 60000))}m` : `${String(Math.floor(age / 3600000))}h`;
      const status = stale ? `${R}STALE${N}` : `${G}ACTIVE${N}`;
      console.log(`  ${status} ${a.id} → ${a.milestone ?? '?'} (heartbeat: ${ageStr} ago)`);
    }
  } else { info('No agents registered.'); }

  const completedIds = new Set(p.completed_milestones.map((m) => m.id));
  if (p.active_milestones.length > 0) {
    console.log(`\n${Y}Milestone merge readiness:${N}`);
    for (const ms of p.active_milestones) {
      const deps = ms.depends_on ?? [];
      const unmerged = deps.filter((d) => !completedIds.has(d));
      if (unmerged.length === 0) console.log(`  ${G}●${N} ${ms.id} — ready to merge`);
      else console.log(`  ${R}●${N} ${ms.id} — blocked by: ${unmerged.join(', ')}`);
    }
  }
  console.log('');
}
```

### scripts/harness/tasks.ts

```typescript
// Session init, status display, and the task execution loop: next, start, done, block.
import { execSync } from 'node:child_process';
import process from 'node:process';
import { PKG, STALE_AGENT_MS, ok, warn, fail, step, info, R, G, Y, B, D, N } from './config.js';
import type { Progress } from './types.js';
import { loadProgress, saveProgress, loadPlan, savePlan } from './state.js';
import { getWorktreeInfo, enforceWorktree, getAgentId, registerAgent, updateHeartbeat } from './worktree.js';
import { recoverMilestoneBoard } from './recovery.js';
import { cmdStaleCheck, cmdSyncPlans } from './quality.js';
import {
  STATUS, parsePlanTaskRows, replaceTaskStatus, getTaskStatus,
  taskExistsInPlan,
  type StatusEmoji, type TaskRow,
} from './plan-utils.js';

// ─── init ────────────────────────────────────────────────────────────────────
// Supports --auto-start flag for automatic task pickup after worktree:start.

export function cmdInit(): void {
  console.log(`\n${B}═══ Harness Init ═══${N}\n`);

  const autoStart = process.argv.includes('--auto-start');
  const wt = getWorktreeInfo();

  step('Checking for new plan files...');
  cmdSyncPlans(true);

  step('Running stale check...');
  cmdStaleCheck(true);

  // ── Milestone board recovery ──────────────────────────────────────────
  step('Validating milestone board...');
  const p = loadProgress();
  const recovery = recoverMilestoneBoard(p);
  if (recovery.recovered > 0) {
    ok(`Auto-recovered ${String(recovery.recovered)} milestone(s): ${recovery.ids.join(', ')}`);
  }

  // Agent registration (worktree only)
  if (wt.isWorktree) {
    step('Registering agent...');
    const p2 = loadProgress(); // reload after recovery
    registerAgent(p2, wt);
    saveProgress(p2);
    ok(`Agent registered: ${getAgentId()} on ${wt.milestoneId ?? wt.currentBranch}`);

    const now = Date.now();
    const staleAgents = p2.agents.filter(
      (a) => (now - new Date(a.heartbeat).getTime()) > STALE_AGENT_MS && a.id !== getAgentId()
    );
    if (staleAgents.length > 0) {
      warn('Stale agents detected (heartbeat >2h):');
      staleAgents.forEach((a) => console.log(`  ${Y}•${N} ${a.id} on ${a.milestone} — last seen ${a.heartbeat}`));
      info('These milestones may be reclaimable.');
    }
  } else {
    info('Running from main repo root. Task commands (next/start/done) require a worktree.');
    info(`Start a milestone: ${PKG} run harness worktree:start <M-id>`);
  }

  cmdStatus();

  const p3 = loadProgress();

  // ── Clear stale current_task if it doesn't belong to this worktree's milestone
  if (p3.current_task && wt.isWorktree && wt.milestoneId) {
    const taskMs = p3.current_task.id.match(/^(M\d+)-/)?.[1];
    if (taskMs && taskMs !== wt.milestoneId) {
      warn(
        `current_task ${p3.current_task.id} belongs to ${taskMs}, ` +
        `but this worktree is for ${wt.milestoneId}. Clearing stale task.`
      );
      p3.current_task = null;
      saveProgress(p3);
    }
  }

  if (p3.current_task?.status === 'in_progress') {
    const taskId = p3.current_task.id;
    warn(`Task ${taskId} was in progress from a previous session.`);

    let dirty = false;
    try {
      const status = execSync('git status --porcelain', { encoding: 'utf-8', shell: true }).trim();
      dirty = status.length > 0;
    } catch { /* not a git repo */ }

    if (dirty) {
      info(`Uncommitted changes detected. Options:`);
      console.log(`  1. Continue working: ${PKG} run harness validate → git commit → harness done ${taskId}`);
      console.log(`  2. Discard and reset: git checkout . && ${PKG} run harness reset ${taskId}`);
    } else {
      info(`No uncommitted changes. The task may have been committed but not marked done.`);
      console.log(`  • If committed: ${PKG} run harness done ${taskId}`);
      console.log(`  • If not started yet: ${PKG} run harness reset ${taskId}`);
    }

    if (autoStart) {
      info('--auto-start skipped: a task is already in progress. Resolve it first.');
    }
    return;
  }

  // ── Auto-start — find next task and claim it ──────────────────────────
  if (autoStart && wt.isWorktree) {
    console.log(`\n${Y}▶${N} Auto-start: looking for first available task...`);
    const nextTaskId = findNextTaskId(wt.milestoneId);
    if (nextTaskId) {
      console.log(`${G}▶${N} Auto-starting task: ${Y}${nextTaskId}${N}`);
      cmdStart(nextTaskId);
    } else {
      info('No available tasks found for auto-start. All tasks may be done or blocked.');
    }
  }
}

// ── Helper — find next task without exiting process ─────────────────────────
// Uses row-level parsing. Returns task ID or null.

function findNextTaskId(milestonePrefix: string | null): string | null {
  if (!milestonePrefix) return null;

  const p = loadProgress();
  const graph = p.dependency_graph;
  let plan: string;
  try { plan = loadPlan(); } catch { return null; }

  const rows = parsePlanTaskRows(plan, milestonePrefix);
  const doneSet = new Set(
    rows.filter((r) => r.statusEmoji === STATUS.DONE).map((r) => r.taskId),
  );
  // Also collect done tasks from OTHER milestones (for cross-milestone deps)
  const allRows = parsePlanTaskRows(plan);
  for (const r of allRows) {
    if (r.statusEmoji === STATUS.DONE) doneSet.add(r.taskId);
  }

  const blockedIds = new Set(p.blockers.map((b) => b.task_id));

  for (const row of rows) {
    if (row.statusEmoji !== STATUS.TODO) continue;
    if (blockedIds.has(row.taskId)) continue;

    const deps = graph[row.taskId]?.depends_on ?? [];
    const allDepsDone = deps.every((d) => doneSet.has(d));
    if (allDepsDone) return row.taskId;
  }

  return null;
}

// ─── status ──────────────────────────────────────────────────────────────────

export function cmdStatus(): void {
  const p = loadProgress();
  console.log(`\n${B}═══ Project: ${p.project} ═══${N}`);
  console.log(`Last updated: ${D}${p.last_updated}${N}`);

  if (p.current_milestone) {
    const m = p.current_milestone;
    const pct = m.tasks_total > 0 ? Math.round((m.tasks_done / m.tasks_total) * 100) : 0;
    console.log(`\nMilestone: ${B}${m.id}${N} — ${m.name}`);
    console.log(`  Status: ${m.status} | Progress: ${String(m.tasks_done)}/${String(m.tasks_total)} (${String(pct)}%)`);
    console.log(`  Done: ${String(m.tasks_done)} | In Progress: ${String(m.tasks_in_progress)} | Blocked: ${String(m.tasks_blocked)} | Remaining: ${String(m.tasks_remaining)}`);
    console.log(`  Branch: ${m.branch}`);
  } else {
    info('No active milestone. Ready for new work.');
  }

  if (p.current_task) {
    console.log(`\nCurrent task: ${Y}${p.current_task.id}${N} — ${p.current_task.description}`);
  }

  if (p.blockers.length > 0) {
    console.log(`\n${R}Blockers (${String(p.blockers.length)}):${N}`);
    p.blockers.forEach((b) => console.log(`  ${R}•${N} ${b.task_id}: ${b.description}`));
  }

  if (p.completed_milestones.length > 0) {
    console.log(`\nCompleted: ${p.completed_milestones.map((m) => m.id).join(', ')}`);
  }
  console.log('');
}

// ─── next ────────────────────────────────────────────────────────────────────

export function cmdNext(): void {
  const wt = enforceWorktree('next');

  const p = loadProgress();
  updateHeartbeat(p);
  saveProgress(p);

  const graph = p.dependency_graph;
  const plan = loadPlan();

  const milestonePrefix = wt.milestoneId;
  if (!milestonePrefix) {
    fail(
      `Cannot determine milestone from branch '${wt.currentBranch}'.\n` +
      `  Expected branch format: milestone/m<n> (e.g. milestone/m1)`
    );
    return;
  }

  // Row-level parsing — status comes from the Status column only
  const msRows = parsePlanTaskRows(plan, milestonePrefix);
  const allRows = parsePlanTaskRows(plan);

  const doneSet = new Set<string>();
  for (const r of allRows) {
    if (r.statusEmoji === STATUS.DONE) doneSet.add(r.taskId);
  }

  const wipSet = new Set<string>();
  const todoTasks: TaskRow[] = [];

  for (const row of msRows) {
    if (row.statusEmoji === STATUS.WIP) wipSet.add(row.taskId);
    if (row.statusEmoji === STATUS.TODO) todoTasks.push(row);
  }

  const blockedIds = new Set(p.blockers.map((b) => b.task_id));

  for (const row of todoTasks) {
    if (blockedIds.has(row.taskId)) continue;
    const deps = graph[row.taskId]?.depends_on ?? [];
    const allDepsDone = deps.every((d) => doneSet.has(d));
    if (allDepsDone) {
      console.log(`\n${G}Next task:${N} ${Y}${row.taskId}${N} — ${row.description}`);
      console.log(`\nRun: ${D}${PKG} run harness start ${row.taskId}${N}`);
      return;
    }
  }

  const allDone = msRows.length > 0 && msRows.every((r) => r.statusEmoji === STATUS.DONE);

  if (allDone) {
    ok(`All ${milestonePrefix} tasks complete! Run: ${PKG} run harness merge-gate`);
  } else if (todoTasks.length === 0 && wipSet.size === 0) {
    ok('All tasks complete! Run: ' + PKG + ' run harness merge-gate');
  } else if (todoTasks.length > 0) {
    warn('All remaining tasks are blocked. Requires human input.');
    p.blockers.forEach((b) => console.log(`  ${R}•${N} ${b.task_id}: ${b.description}`));
  } else {
    const milestoneWip = [...wipSet];
    info('Tasks in progress: ' + milestoneWip.join(', '));
  }
}

// ─── start ───────────────────────────────────────────────────────────────────
// Row-level: match task ID in column 1, check/replace status in Status column.
// Preserves "resume 不重複累加 in_progress" behaviour.

export function cmdStart(taskId: string): void {
  if (!taskId) fail('Usage: harness start <task-id>  (e.g., harness start M1-003)');

  const wt = enforceWorktree('start');

  const taskMilestone = taskId.match(/^(M\d+)-/)?.[1];
  if (wt.milestoneId && taskMilestone && taskMilestone !== wt.milestoneId) {
    fail(
      `Task ${taskId} belongs to ${taskMilestone}, but this worktree is for ${wt.milestoneId}.\n` +
      `  Switch to the correct worktree or create one:\n` +
      `  ${PKG} run harness worktree:start ${taskMilestone}`
    );
  }

  const p = loadProgress();
  updateHeartbeat(p);
  let plan = loadPlan();

  if (!taskExistsInPlan(plan, taskId)) {
    fail(`Task ${taskId} not found in PLAN.md`);
  }

  // Check current status via column-level lookup
  const currentStatus = getTaskStatus(plan, taskId);
  let freshStart = false;

  if (currentStatus === STATUS.TODO) {
    // Normal flow: ⬜ → 🟡
    const result = replaceTaskStatus(plan, taskId, STATUS.TODO, STATUS.WIP);
    if (result.changed) {
      savePlan(result.plan);
      freshStart = true;
    } else {
      warn(`Could not update ⬜ status for ${taskId} in PLAN.md. Check formatting.`);
    }
  } else if (currentStatus === STATUS.WIP) {
    // Resume — already 🟡, don't touch PLAN.md, don't increment counter
    info(`${taskId} is already in progress (🟡). Resuming.`);
  } else if (currentStatus === STATUS.DONE) {
    fail(`${taskId} is already marked done (✅). Use 'harness next' to pick a new task.`);
    return;
  } else {
    warn(`Unexpected status '${currentStatus ?? 'unknown'}' for ${taskId} in PLAN.md.`);
  }

  // Read description from parsed row
  const rows = parsePlanTaskRows(plan);
  const row = rows.find((r) => r.taskId === taskId);
  const desc = row?.description ?? taskId;

  p.current_task = {
    id: taskId, story: '', description: desc,
    status: 'in_progress', started_at: new Date().toISOString(),
    files_touched: [], notes: '',
  };
  // Only increment counter on fresh start (⬜→🟡), not on resume (already 🟡)
  if (freshStart && p.current_milestone) p.current_milestone.tasks_in_progress++;
  saveProgress(p);

  ok(`Started: ${taskId} — ${desc}`);
  info(`Write code, then run: ${PKG} run harness validate`);
}

// ─── done ────────────────────────────────────────────────────────────────────
// Row-level: match task ID in column 1, replace Status column, fill Commit column.

export function cmdDone(taskId: string): void {
  if (!taskId) fail('Usage: harness done <task-id>');
  enforceWorktree('done');

  const p = loadProgress();
  updateHeartbeat(p);
  let plan = loadPlan();

  let commitHash = '—';
  try { commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8', shell: true }).trim(); }
  catch { /* no git */ }

  const currentStatus = getTaskStatus(plan, taskId);
  let wasInProgress = false;
  let planUpdated = false;

  if (currentStatus === STATUS.WIP) {
    // Normal flow: 🟡 → ✅
    const result = replaceTaskStatus(plan, taskId, STATUS.WIP, STATUS.DONE, commitHash);
    if (result.changed) {
      savePlan(result.plan);
      wasInProgress = true;
      planUpdated = true;
    } else {
      warn(`Could not update 🟡 status for ${taskId}. Check PLAN.md formatting.`);
    }
  } else if (currentStatus === STATUS.TODO) {
    // Start was missed — skip directly ⬜ → ✅
    warn(`${taskId} was still ⬜ (start may have failed). Marking ✅ directly.`);
    const result = replaceTaskStatus(plan, taskId, STATUS.TODO, STATUS.DONE, commitHash);
    if (result.changed) {
      savePlan(result.plan);
      wasInProgress = false;
      planUpdated = true;
    }
  } else if (currentStatus === STATUS.DONE) {
    warn(`${taskId} is already marked ✅. Skipping PLAN.md update and counter increment.`);
  } else if (currentStatus === STATUS.BLOCKED) {
    // Unblock + complete in one step
    warn(`${taskId} was 🚫 blocked. Marking ✅ directly.`);
    const result = replaceTaskStatus(plan, taskId, STATUS.BLOCKED, STATUS.DONE, commitHash);
    if (result.changed) {
      savePlan(result.plan);
      planUpdated = true;
    }
  } else {
    warn(`Could not find or update status for ${taskId} in PLAN.md. Check table formatting.`);
  }

  // Update progress.json counters — only if PLAN.md was actually updated
  const taskMilestone = taskId.match(/^(M\d+)-/)?.[1];
  const isCurrentMilestone = p.current_milestone && taskMilestone === p.current_milestone.id;

  p.current_task = null;
  if (planUpdated && isCurrentMilestone && p.current_milestone) {
    p.current_milestone.tasks_done++;
    if (wasInProgress) {
      p.current_milestone.tasks_in_progress = Math.max(0, p.current_milestone.tasks_in_progress - 1);
    }
    p.current_milestone.tasks_remaining = Math.max(0, p.current_milestone.tasks_remaining - 1);
  } else if (planUpdated && taskMilestone && !isCurrentMilestone) {
    warn(
      `${taskId} belongs to ${taskMilestone}, but current_milestone is ${p.current_milestone?.id ?? 'null'}.\n` +
      `  Counter NOT incremented for ${p.current_milestone?.id ?? '?'}. Fix progress.json manually if needed.`
    );
  }
  saveProgress(p);

  ok(`Completed: ${taskId} (commit: ${commitHash})`);

  // Task is committed — clean working tree for the next task.
  // "done = committed" contract: no lingering changes should remain.
  step('Cleaning working tree (git checkout .)...');
  try {
    execSync('git checkout .', { shell: true, stdio: 'pipe' });
    ok('Working tree clean.');
  } catch {
    warn('git checkout . failed — check for untracked files or conflicts.');
  }

  info(`Run: ${PKG} run harness next`);
}

// ─── block ───────────────────────────────────────────────────────────────────

export function cmdBlock(taskId: string, reason: string): void {
  if (!taskId || !reason) fail('Usage: harness block <task-id> <reason>');
  enforceWorktree('block');

  const p = loadProgress();
  p.blockers.push({ task_id: taskId, description: reason, added_at: new Date().toISOString() });

  if (p.current_task?.id === taskId) {
    p.current_task = null;
    if (p.current_milestone) {
      p.current_milestone.tasks_in_progress = Math.max(0, p.current_milestone.tasks_in_progress - 1);
      p.current_milestone.tasks_blocked++;
    }
  }

  // Row-level: 🟡 → 🚫 in Status column only
  let plan = loadPlan();
  const result = replaceTaskStatus(plan, taskId, STATUS.WIP, STATUS.BLOCKED);
  if (result.changed) savePlan(result.plan);

  saveProgress(p);

  warn(`Blocked: ${taskId} — ${reason}`);
  info(`Run: ${PKG} run harness next`);
}

// ─── reset ───────────────────────────────────────────────────────────────────

export function cmdReset(taskId: string): void {
  if (!taskId) fail('Usage: harness reset <task-id>  (reverts 🟡 or 🚫 back to ⬜)');
  enforceWorktree('reset');

  const p = loadProgress();
  let plan = loadPlan();

  const currentStatus = getTaskStatus(plan, taskId);

  if (currentStatus === STATUS.DONE) {
    fail(`${taskId} is already ✅. Cannot reset completed tasks — create a fix task instead.`);
    return;
  }

  // Try 🟡 → ⬜
  let result = replaceTaskStatus(plan, taskId, STATUS.WIP, STATUS.TODO);
  if (!result.changed) {
    // Try 🚫 → ⬜
    result = replaceTaskStatus(plan, taskId, STATUS.BLOCKED, STATUS.TODO);
  }

  if (result.changed) {
    savePlan(result.plan);
  } else if (currentStatus === STATUS.TODO) {
    warn(`${taskId} is already ⬜.`);
  } else {
    warn(`${taskId} not found or status unrecognised in PLAN.md.`);
  }

  // Clear current_task if it's the one being reset
  if (p.current_task?.id === taskId) {
    p.current_task = null;
    if (p.current_milestone) {
      p.current_milestone.tasks_in_progress = Math.max(0, p.current_milestone.tasks_in_progress - 1);
    }
  }

  // Remove from blockers if it was blocked
  const blockerIdx = p.blockers.findIndex((b) => b.task_id === taskId);
  if (blockerIdx !== -1) {
    p.blockers.splice(blockerIdx, 1);
    if (p.current_milestone) {
      p.current_milestone.tasks_blocked = Math.max(0, p.current_milestone.tasks_blocked - 1);
    }
  }

  saveProgress(p);
  ok(`Reset: ${taskId} → ⬜`);
  info(`Run: ${PKG} run harness next`);
}
```

### scripts/harness/validate.ts

```typescript
// Validation commands: lint → type-check → test, and file-guard (500-line check).
import { execSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, extname } from 'node:path';
import { PKG, FILE_LIMIT, SOURCE_EXTS, IGNORE_DIRS, ok, fail, step, Y, G, N } from './config.js';

export function cmdValidate(full = false): void {
  const run = (cmd: string, label: string): void => {
    step(label);
    try {
      execSync(cmd, { stdio: 'inherit', shell: true });
      ok(label);
    } catch { fail(`${label} failed`); }
  };

  console.log(`\n${Y}═══ ${full ? 'Full Validation' : 'Validation'} ═══${N}\n`);

  step('Lint auto-fix');
  try { execSync(`${PKG} run lint:fix`, { stdio: 'inherit', shell: true }); } catch { /* ok */ }
  ok('Lint auto-fix complete');

  run(`${PKG} run lint`, 'Lint check (strict)');
  run(`${PKG} run type-check`, 'Type check');
  run(`${PKG} run test`, 'Unit tests');

  if (full) {
    if (existsSync('tests/integration') && readdirSync('tests/integration').length > 0) {
      run(`${PKG} run test:integration`, 'Integration tests');
    }
    if (existsSync('tests/e2e') && readdirSync('tests/e2e').length > 0) {
      run(`${PKG} run test:e2e`, 'E2E tests');
    }
    cmdFileGuard();
  }

  console.log(`\n${G}═══ ${full ? 'Full validation' : 'Validation'} passed ═══${N}`);
}

export function cmdFileGuard(stagedOnly = false): void {
  const walk = (dir: string): string[] => {
    if (!existsSync(dir)) return [];
    const results: string[] = [];
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (IGNORE_DIRS.has(entry.name)) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) results.push(...walk(full));
      else if (SOURCE_EXTS.has(extname(entry.name))) results.push(full);
    }
    return results;
  };

  let files: string[];
  if (stagedOnly) {
    const staged = execSync('git diff --cached --name-only --diff-filter=ACM', { encoding: 'utf-8', shell: true }).trim();
    files = staged.split('\n').filter((f) => f && SOURCE_EXTS.has(extname(f)));
  } else {
    files = [...walk('src'), ...walk('tests'), ...walk('scripts')];
  }

  const violations: string[] = [];
  for (const file of files) {
    if (!existsSync(file)) continue;
    const lines = readFileSync(file, 'utf-8').split('\n').length;
    if (lines > FILE_LIMIT) violations.push(`  ${String(lines)} lines: ${file}`);
  }

  if (violations.length > 0) {
    console.error(`\n\x1b[31m✗ ${String(violations.length)} file(s) exceed ${String(FILE_LIMIT)} lines:${N}\n`);
    violations.forEach((v) => console.error(v));
    fail('Split files before committing. (Iron Rule 1)');
  }
  ok(`All files within ${String(FILE_LIMIT)}-line limit.`);
}
```

### scripts/harness/quality.ts

```typescript
// merge-gate, stale-check, sync-plans, schema validation, changelog generation.
import { execSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';
import { PKG, PROGRESS_FILE, PLAN_FILE, SCHEMA_FILE, PLANS_DIR, ok, warn, fail, step, info, R, G, Y, B, N } from './config.js';
import { loadProgress, saveProgress, loadPlan } from './state.js';
import { getWorktreeInfo } from './worktree.js';
import { cmdValidate } from './validate.js';
import {
  STATUS, countTaskStatuses, parsePlanTaskRows,
} from './plan-utils.js';

// ─── merge-gate ──────────────────────────────────────────────────────────────
// PATCHED: uses row-level parsing via countTaskStatuses instead of cross-row regex.

export function cmdMergeGate(): void {
  console.log(`\n${B}═══ Milestone Merge Gate ═══${N}\n`);

  const wt = getWorktreeInfo();

  // ── Check all tasks in this milestone are done ─────────────────────────
  step('Checking all milestone tasks are complete...');
  const p = loadProgress();
  const ms = p.current_milestone;
  if (!ms) { fail('No active milestone found in progress.json'); return; }

  const plan = loadPlan();
  const milestoneId = ms.id;

  // Row-level: count statuses by parsing each row's Status column
  const counts = countTaskStatuses(plan, milestoneId);
  const incomplete = counts.todo + counts.wip + counts.blocked;

  if (incomplete > 0) {
    fail(
      `${milestoneId} has ${String(incomplete)} incomplete task(s) in PLAN.md:\n` +
      `  ⬜ todo: ${String(counts.todo)}  |  🟡 in progress: ${String(counts.wip)}  |  🚫 blocked: ${String(counts.blocked)}\n\n` +
      `  Complete all tasks before running merge-gate.\n` +
      `  Run: ${PKG} run harness next`
    );
    return;
  }

  if (counts.total === 0) {
    fail(`No tasks found for ${milestoneId} in PLAN.md. Check table formatting.`);
    return;
  }

  ok(`All ${milestoneId} tasks are ✅ (${String(counts.done)}/${String(counts.total)})`);

  // ── Full validation ────────────────────────────────────────────────────
  cmdValidate(true);

  step('Generating changelog...');
  cmdChangelog();

  console.log(`\n${G}═══ Merge gate passed ═══${N}\n`);

  if (wt.isWorktree) {
    info(`You are inside worktree: ${wt.cwd}`);
    info(`Main repo root: ${wt.mainRoot}`);
    console.log(`\nNext steps:`);
    console.log(`  cd "${wt.mainRoot}"`);
    console.log(`  ${PKG} run harness worktree:finish ${ms.id}`);
  } else {
    console.log(`Run: ${PKG} run harness worktree:finish ${ms.id}`);
  }
}

// ─── stale-check ─────────────────────────────────────────────────────────────
// PATCHED: uses row-level parsing for task count comparison and WIP detection.

export function cmdStaleCheck(quiet = false): void {
  let count = 0;
  const w = (msg: string) => { warn(msg); count++; };

  if (existsSync('.env.example') && existsSync('src')) {
    const example = readFileSync('.env.example', 'utf-8');
    const exampleVars = new Set(
      example.split('\n').map((l) => l.split('=')[0]?.trim()).filter((v) => v && !v.startsWith('#')),
    );
    const envPat = [/process\.env\.(\w+)/g, /Bun\.env\.(\w+)/g, /env\(['"](\w+)['"]\)/g];
    const scanDir = (dir: string): void => {
      for (const e of readdirSync(dir, { withFileTypes: true, recursive: true })) {
        if (!e.isFile() || e.name.endsWith('.d.ts')) continue;
        const ext = e.name.split('.').pop();
        if (!['ts', 'tsx', 'js', 'jsx'].includes(ext ?? '')) continue;
        const content = readFileSync(join(e.parentPath ?? dir, e.name), 'utf-8');
        for (const pat of envPat) {
          let m; while ((m = pat.exec(content)) !== null) {
            if (!exampleVars.has(m[1])) w(`.env.example missing: ${m[1] ?? ''}`);
          }
        }
      }
    };
    scanDir('src');
  }

  if (existsSync(PROGRESS_FILE) && existsSync(PLAN_FILE)) {
    const plan = loadPlan();
    const p = loadProgress();

    // Row-level: count done tasks for the current milestone by Status column
    const msId = p.current_milestone?.id;
    if (msId) {
      const counts = countTaskStatuses(plan, msId);
      const progDone = p.current_milestone?.tasks_done ?? 0;

      if (counts.done !== progDone) {
        w(`PLAN.md has ${String(counts.done)} tasks ✅ for ${msId} but progress.json says tasks_done=${String(progDone)}`);
      }
    }

    // Row-level: check for 🟡 tasks in PLAN.md vs current_task in progress.json
    const allRows = parsePlanTaskRows(plan);
    const wipRows = allRows.filter((r) => r.statusEmoji === STATUS.WIP);
    for (const row of wipRows) {
      if (!p.current_task || p.current_task.id !== row.taskId) {
        w(`PLAN.md shows ${row.taskId} as 🟡 but progress.json current_task is ${p.current_task?.id ?? 'null'}`);
      }
    }
  }

  if (existsSync('ARCHITECTURE.md') && existsSync('src/modules')) {
    const arch = readFileSync('ARCHITECTURE.md', 'utf-8').toLowerCase();
    for (const d of readdirSync('src/modules', { withFileTypes: true })) {
      if (d.isDirectory() && !arch.includes(d.name.toLowerCase())) {
        w(`Module '${d.name}' not in ARCHITECTURE.md`);
      }
    }
  }

  cmdSyncPlans(quiet);

  if (count === 0) { if (!quiet) ok('No stale items.'); }
  else if (!quiet) console.error(`\n${String(count)} stale item(s) found.`);
}

// ─── sync-plans ──────────────────────────────────────────────────────────────

export function cmdSyncPlans(quiet = false): void {
  if (!existsSync(PLANS_DIR) || !existsSync(PROGRESS_FILE)) return;
  const p = loadProgress();
  const synced = new Set(p.synced_plans ?? []);
  let count = 0;
  for (const file of readdirSync(PLANS_DIR)) {
    if (!file.endsWith('.md') || file === '.gitkeep' || synced.has(file)) continue;
    count++;
    if (!quiet) {
      console.log(`\n${Y}New plan:${N} ${file}`);
      const content = readFileSync(join(PLANS_DIR, file), 'utf-8');
      console.log(content.slice(0, 500));
      if (content.length > 500) console.log('...(truncated)');
      info('Parse this plan → add milestone to PLAN.md → update progress.json');
      info(`Then run: add '${file}' to synced_plans in progress.json`);
    }
  }
  if (count === 0 && !quiet) ok('All plans synced.');
  else if (count > 0) warn(`${String(count)} unsynced plan(s).`);
}

// ─── schema ──────────────────────────────────────────────────────────────────

export function cmdSchema(): void {
  if (!existsSync(PROGRESS_FILE)) { ok('No progress.json (skip).'); return; }
  if (!existsSync(SCHEMA_FILE)) { warn('No schema file (skip).'); return; }
  const data = loadProgress();
  const errors: string[] = [];
  const check = (cond: boolean, msg: string) => { if (!cond) errors.push(msg); };

  check(!!data.project, 'missing: project');
  check(!!data.last_updated, 'missing: last_updated');
  check(!!data.last_agent, 'missing: last_agent');
  if (data.current_milestone) {
    check(/^M\d+$/.test(data.current_milestone.id), `milestone id '${data.current_milestone.id}' invalid`);
  }
  if (data.current_task) {
    check(/^M\d+-\d+$/.test(data.current_task.id), `task id '${data.current_task.id}' invalid`);
  }
  for (const key of Object.keys(data.dependency_graph ?? {})) {
    check(/^M\d+-\d+$/.test(key), `dependency_graph key '${key}' invalid`);
  }

  if (errors.length > 0) {
    errors.forEach((e) => console.error(`  ${R}•${N} ${e}`));
    fail('progress.json validation failed');
  }
  ok('progress.json valid.');
}

// ─── learn ───────────────────────────────────────────────────────────────────

export function cmdLearn(category: string, message: string): void {
  if (!category || !message) {
    fail(
      'Usage: harness learn <category> <message>\n' +
      '  Categories: dependency, config, architecture, testing, deploy, performance, security, tooling'
    );
    return;
  }

  const validCategories = ['dependency', 'config', 'architecture', 'testing', 'deploy', 'performance', 'security', 'tooling'];
  if (!validCategories.includes(category)) {
    warn(`Unknown category '${category}'. Valid: ${validCategories.join(', ')}`);
  }

  const p = loadProgress();
  const taskId = p.current_task?.id ?? 'unknown';

  p.learnings.push({
    date: new Date().toISOString().split('T')[0],
    context: taskId,
    category,
    problem: message,
    solution: '',
    affected_files: [],
    prevention: '',
  });
  saveProgress(p);

  const learningsFile = 'docs/learnings.md';
  if (existsSync(learningsFile)) {
    const entry = `\n### ${new Date().toISOString().split('T')[0]} — ${taskId} (${category})\n${message}\n`;
    const content = readFileSync(learningsFile, 'utf-8');
    writeFileSync(learningsFile, content + entry);
  }

  ok(`Learning logged: [${category}] ${message.slice(0, 80)}${message.length > 80 ? '...' : ''}`);
}

// ─── changelog ───────────────────────────────────────────────────────────────

export function cmdChangelog(): void {
  let from = process.argv[3] ?? '';
  const to = process.argv[4] ?? 'HEAD';

  if (!from) {
    try { from = execSync('git describe --tags --abbrev=0', { encoding: 'utf-8', shell: true }).trim(); } catch { /* no tags */ }
  }

  const range = from ? `${from}..${to}` : to;
  let log: string;
  try { log = execSync(`git log --oneline --pretty=format:"%s|%h" ${range}`, { encoding: 'utf-8', shell: true }).trim(); }
  catch { log = ''; }

  if (!log) { console.log('No commits in range.'); return; }

  const groups = new Map<string, string[]>();
  const order: string[] = [];

  for (const line of log.split('\n')) {
    const [msg, hash] = line.split('|');
    if (!msg) continue;
    let group: string, entry: string;
    const tm = msg.match(/^\[(M\d+)-(\d+)\]\s+(.+)/);
    const dm = msg.match(/^\[docs\]\s+(.+)/);
    const om = msg.match(/^\[(scaffold|fix|refactor|ci)\]\s+(.+)/);
    if (tm) { group = tm[1] ?? ''; entry = `- \`${tm[1] ?? ''}-${tm[2] ?? ''}\` ${tm[3] ?? ''} (\`${hash}\`)`; }
    else if (dm) { group = 'Docs'; entry = `- ${dm[1] ?? ''} (\`${hash}\`)`; }
    else if (om) { group = (om[1] ?? '')[0].toUpperCase() + (om[1] ?? '').slice(1); entry = `- ${om[2] ?? ''} (\`${hash}\`)`; }
    else { group = 'Other'; entry = `- ${msg} (\`${hash}\`)`; }
    if (!groups.has(group)) { groups.set(group, []); order.push(group); }
    groups.get(group)!.push(entry);
  }

  console.log(`# Changelog${from ? ` (${from} → ${to})` : ''}\n`);
  for (const g of order) {
    console.log(`## ${g}\n`);
    groups.get(g)!.forEach((e) => console.log(e));
    console.log('');
  }
}
```

### scripts/harness.ts (Entry Point)

```typescript
#!/usr/bin/env tsx
// Thin router — all logic lives in scripts/harness/ modules.
// This file should stay under 50 lines.
import process from 'node:process';

import { cmdInit, cmdStatus, cmdNext, cmdStart, cmdDone, cmdBlock, cmdReset } from './harness/tasks.js';
import { cmdValidate, cmdFileGuard } from './harness/validate.js';
import { cmdMergeGate, cmdStaleCheck, cmdSchema, cmdChangelog, cmdLearn } from './harness/quality.js';
import { cmdWorktreeStart, cmdWorktreeFinish, cmdWorktreeRebase, cmdWorktreeList } from './harness/worktree.js';
import { recoverMilestoneBoard } from './harness/recovery.js';
import { B, Y, G, N } from './harness/config.js';
import { loadProgress, saveProgress } from './harness/state.js';

const cmd = process.argv[2];
const arg1 = process.argv[3] ?? '';
const argRest = process.argv.slice(4).join(' ');

switch (cmd) {
  case 'init':              cmdInit(); break;
  case 'status':            cmdStatus(); break;
  case 'next':              cmdNext(); break;
  case 'start':             cmdStart(arg1); break;
  case 'validate':          cmdValidate(false); break;
  case 'validate:full':     cmdValidate(true); break;
  case 'done':              cmdDone(arg1); break;
  case 'block':             cmdBlock(arg1, argRest); break;
  case 'reset':             cmdReset(arg1); break;
  case 'learn':             cmdLearn(arg1, argRest); break;
  case 'merge-gate':        cmdMergeGate(); break;
  case 'worktree:start':    cmdWorktreeStart(arg1); break;
  case 'worktree:finish':   cmdWorktreeFinish(arg1, cmdValidate); break;
  case 'worktree:rebase':   cmdWorktreeRebase(); break;
  case 'worktree:status':   cmdWorktreeList(); break;
  case 'stale-check':       cmdStaleCheck(); break;
  case 'file-guard':        cmdFileGuard(process.argv.includes('--staged')); break;
  case 'changelog':         cmdChangelog(); break;
  case 'schema':            cmdSchema(); break;
  // ── PATCH: Manual milestone board recovery command ──────────────────────
  case 'recover': {
    console.log(`\n${B}═══ Milestone Board Recovery ═══${N}\n`);
    const p = loadProgress();
    const result = recoverMilestoneBoard(p);
    if (result.recovered > 0) {
      console.log(`${G}✓${N} Recovered ${String(result.recovered)} milestone(s): ${result.ids.join(', ')}`);
    } else {
      console.log(`${G}✓${N} Milestone board is consistent — nothing to recover.`);
    }
    break;
  }
  default:
    console.log(`
${B}harness${N} — project automation CLI

${Y}Session:${N}
  init                    Boot session: sync plans, stale check, register agent, status
  init --auto-start       Boot + auto-claim first available task (used by worktree:start)
  status                  Print current state

${Y}Worktrees (milestone isolation):${N}
  worktree:start <M-id>   Create branch + worktree + install + init + auto-start
  worktree:finish <M-id>  Rebase + merge + push to remote + cleanup
  worktree:rebase          Rebase current worktree onto latest main (run inside worktree)
  worktree:status          Show all worktrees, agents, and merge readiness

${Y}Task loop (run inside the milestone worktree — enforced):${N}
  next                    Find next unblocked task
  start <id>              Claim task → 🟡
  done <id>               Complete task → ✅
  block <id> <msg>        Mark task blocked → 🚫
  reset <id>              Revert task to ⬜ (undo start or unblock)
  learn <cat> <msg>       Log a learning (dependency, config, architecture, etc.)

${Y}Validation:${N}
  validate                Lint → type-check → test
  validate:full           + integration + e2e + file-guard

${Y}Quality:${N}
  merge-gate              Full gate check before worktree:finish
  stale-check             Detect stale docs/env/plans
  file-guard              500-line limit check (--staged)
  schema                  Validate progress.json
  changelog [from]        Generate release notes
  recover                 Auto-detect and fix milestone board inconsistencies
`);
}
```

---

### scripts/check-commit-msg.ts

```typescript
#!/usr/bin/env tsx
// Commit message format enforcer — called by .husky/commit-msg hook.
// Kept standalone (not in harness/ modules) because it needs the msg file path argument.
import { readFileSync, existsSync } from 'node:fs';
import process from 'node:process';

const R = '\x1b[31m', G = '\x1b[32m', Y = '\x1b[33m', N = '\x1b[0m';

const msgFile = process.argv[2];
if (!msgFile) {
  console.error(`${R}✗${N} Usage: check-commit-msg <commit-msg-file>`);
  process.exit(1);
}

if (!existsSync(msgFile)) {
  console.error(`${R}✗${N} Commit message file not found: ${msgFile}`);
  process.exit(1);
}

const msg = readFileSync(msgFile, 'utf-8').trim().split('\n')[0]; // first line only

// Valid formats:
// [M1-001] description          ← task commit (most common)
// [M1-001-fix] description      ← fix for a completed task
// [docs] description            ← documentation update
// [scaffold] description        ← initial scaffold / setup
// [fix] description             ← hotfix outside a task
// [refactor] description        ← refactor outside a task
// [ci] description              ← CI/CD changes
// [WIP: M1-001] description     ← work in progress (blocked task)
// merge: M1 complete            ← auto-generated by worktree:finish

const validPatterns = [
  /^\[M\d+-\d+\]\s+.+/,              // [M1-001] description
  /^\[M\d+-\d+-fix\]\s+.+/,          // [M1-001-fix] description
  /^\[(docs|scaffold|fix|refactor|ci)\]\s+.+/,  // [docs] description
  /^\[WIP:\s*M\d+-\d+\]\s+.+/,       // [WIP: M1-001] description
  /^merge:\s+M\d+\s+complete$/,      // merge: M1 complete
];

const isValid = validPatterns.some((p) => p.test(msg));

if (!isValid) {
  console.error(`\n${R}✗ Invalid commit message:${N} "${msg}"\n`);
  console.error(`${Y}Valid formats:${N}`);
  console.error(`  ${G}[M1-001] implement login form${N}         ← task commit`);
  console.error(`  ${G}[M1-001-fix] fix email validation${N}     ← fix for completed task`);
  console.error(`  ${G}[docs] update getting-started.md${N}      ← documentation`);
  console.error(`  ${G}[scaffold] initial project setup${N}      ← setup / scaffold`);
  console.error(`  ${G}[fix] patch CORS header${N}               ← hotfix`);
  console.error(`  ${G}[refactor] extract auth module${N}        ← refactor`);
  console.error(`  ${G}[ci] add staging deploy workflow${N}      ← CI/CD`);
  console.error(`  ${G}[WIP: M1-003] partial implementation${N}  ← blocked / in progress`);
  console.error('');
  process.exit(1);
}
```

---

## Git Hooks (use harness commands)

### .husky/pre-commit
```bash
npx lint-staged
npx tsx scripts/harness.ts file-guard --staged
npx tsx scripts/harness.ts schema
```

### .husky/commit-msg
```bash
npx tsx scripts/harness.ts check-commit-msg "$1"
```

Note: `check-commit-msg` can be a separate case in the router, or kept as the standalone
`scripts/check-commit-msg.ts` (it needs the msg file path argument).

### .husky/pre-push
```bash
npx tsx scripts/harness.ts validate
```

---

## What this replaces

| Before (7 scripts + prose) | After (modular CLI) |
|---|---|
| `scripts/validate.ts` | `harness validate` |
| `scripts/validate-full.ts` | `harness validate:full` |
| `scripts/file-guard.ts` | `harness file-guard` |
| `scripts/stale-check.ts` | `harness stale-check` |
| `scripts/progress-sync.ts` | `harness init` (includes sync) |
| `scripts/validate-schema.ts` | `harness schema` |
| `scripts/changelog.ts` | `harness changelog` |
| Manual progress.json editing | `harness start/done/block` |
| Manual PLAN.md status editing | `harness start/done` |
| ~80 lines of prose in AGENTS.md | ~10 lines of commands |

---

## JSON Schema — schemas/progress.schema.json

Validate progress.json on every write. Built into `harness schema` command.

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
      "required": ["id", "name", "status", "tasks_total", "tasks_done"],
      "properties": {
        "id": { "type": "string", "pattern": "^M[0-9]+$" },
        "name": { "type": "string" },
        "branch": { "type": "string", "pattern": "^milestone/M[0-9]+$" },
        "status": { "type": "string", "enum": ["not_started", "in_progress", "complete"] },
        "tasks_total": { "type": "integer", "minimum": 0 },
        "tasks_done": { "type": "integer", "minimum": 0 },
        "tasks_in_progress": { "type": "integer", "minimum": 0 },
        "tasks_blocked": { "type": "integer", "minimum": 0 },
        "tasks_remaining": { "type": "integer", "minimum": 0 }
      }
    },
    "current_task": {
      "type": ["object", "null"],
      "required": ["id", "description", "status"],
      "properties": {
        "id": { "type": "string", "pattern": "^M[0-9]+-[0-9]+$" },
        "description": { "type": "string" },
        "status": { "type": "string", "enum": ["in_progress", "blocked"] }
      }
    },
    "completed_milestones": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "completed_at"],
        "properties": {
          "id": { "type": "string", "pattern": "^M[0-9]+$" },
          "name": { "type": "string" },
          "completed_at": { "type": "string", "format": "date-time" }
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
          "blocks": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "synced_plans": { "type": "array", "items": { "type": "string" } },
    "learnings": { "type": "array" },
    "blockers": { "type": "array" },
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "milestone", "worktree", "branch", "heartbeat"],
        "properties": {
          "id": { "type": "string" },
          "milestone": { "type": ["string", "null"] },
          "worktree": { "type": "string" },
          "branch": { "type": "string" },
          "started_at": { "type": "string", "format": "date-time" },
          "heartbeat": { "type": "string", "format": "date-time" }
        }
      }
    }
  }
}
```

---

## lint-staged config (in package.json)

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"],
    "docs/progress.json": ["npx tsx scripts/harness.ts schema"]
  }
}
```

With the modular structure, all files (including `scripts/`) go through eslint + prettier
normally. No exclusions needed — every module is well under 500 lines and formats cleanly.

---

## Assembly Checklist

1. Generate `scripts/harness.ts` (entry point router) + `scripts/harness/*.ts` (8 modules)
2. Generate `scripts/check-commit-msg.ts`
3. Generate `schemas/progress.schema.json`
4. Generate `.husky/pre-commit`, `.husky/commit-msg`, `.husky/pre-push`
5. Add `"harness": "tsx scripts/harness.ts"` + `"prepare": "husky"` to package.json
6. Add `tsx` as dev dependency
7. Wire lint-staged to call `harness schema` on progress.json changes
8. **No prettierignore needed** — all modules are small enough for standard formatting
9. **No lint-staged exclusions** — `scripts/` participates in lint + format like everything else
10. **Agents run commands, not edit JSON.** The CLI is the only writer of progress.json.
