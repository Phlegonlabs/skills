# Harness CLI — scripts/harness.ts

Single entry point for all harness automation. Replaces 7 separate scripts + manual
JSON editing. Agent runs commands, CLI handles state.

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
harness init            Session boot: sync plans, stale check, print status
harness status          Print current milestone, task, blockers, progress
harness next            Find and print the next unblocked task
harness start <id>      Claim a task: update progress.json + PLAN.md → 🟡
harness validate        Run lint:fix → lint → type-check → test
harness validate:full   + integration + e2e + file-guard
harness done <id>       Complete a task: update progress.json + PLAN.md → ✅
harness block <id> <reason>   Mark task as blocked, add to blockers
harness merge-gate      Full gate: validate:full + stale + changelog
harness stale-check     Detect stale docs, env, plans
harness file-guard      Check 500-line limit (--staged for hooks)
harness changelog [from] [to]  Generate release notes
harness schema          Validate progress.json against schema
```

---

## Full Implementation

```typescript
// Run via: npx tsx scripts/harness.ts <command>
import { execSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';
import process from 'node:process';

// ─── Config ───────────────────────────────────────────────────────────────────
const PKG = process.env.PKG_MGR ?? 'pnpm';
const PROGRESS_FILE = 'docs/progress.json';
const PLAN_FILE = 'docs/PLAN.md';
const SCHEMA_FILE = 'schemas/progress.schema.json';
const PLANS_DIR = 'docs/exec-plans/active';
const FILE_LIMIT = 500;
const SOURCE_EXTS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.vue', '.svelte']);
const IGNORE_DIRS = new Set(['node_modules', 'dist', 'build', '.next', 'out', 'coverage', '.git']);

// ─── Colors ───────────────────────────────────────────────────────────────────
const R = '\x1b[31m', G = '\x1b[32m', Y = '\x1b[33m', B = '\x1b[34m', D = '\x1b[2m', N = '\x1b[0m';
const ok = (m: string) => console.log(`${G}✓${N} ${m}`);
const warn = (m: string) => console.warn(`${Y}⚠${N} ${m}`);
const fail = (m: string) => { console.error(`${R}✗${N} ${m}`); process.exit(1); };
const step = (m: string) => console.log(`${Y}▶${N} ${m}`);
const info = (m: string) => console.log(`${B}ℹ${N} ${m}`);

// ─── Progress helpers ─────────────────────────────────────────────────────────
interface Progress {
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
  completed_milestones: Array<{ id: string; name: string; completed_at: string; tag: string }>;
  blockers: Array<{ task_id: string; description: string; error?: string; added_at: string }>;
  learnings: Array<Record<string, unknown>>;
  dependency_graph: Record<string, { depends_on: string[]; blocks: string[] }>;
  synced_plans: string[];
  agents: Array<Record<string, unknown>>;
  [key: string]: unknown;
}

function loadProgress(): Progress {
  if (!existsSync(PROGRESS_FILE)) fail(`${PROGRESS_FILE} not found`);
  return JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
}

function saveProgress(p: Progress): void {
  p.last_updated = new Date().toISOString();
  writeFileSync(PROGRESS_FILE, JSON.stringify(p, null, 2) + '\n');
}

function loadPlan(): string {
  if (!existsSync(PLAN_FILE)) fail(`${PLAN_FILE} not found`);
  return readFileSync(PLAN_FILE, 'utf-8');
}

function savePlan(content: string): void {
  writeFileSync(PLAN_FILE, content);
}

// ─── Commands ─────────────────────────────────────────────────────────────────

function cmdInit(): void {
  console.log(`\n${B}═══ Harness Init ═══${N}\n`);

  // 1. Sync plans
  step('Checking for new plan files...');
  cmdSyncPlans(true);

  // 2. Stale check
  step('Running stale check...');
  cmdStaleCheck(true);

  // 3. Status
  cmdStatus();

  // 4. Check for in-progress task with dirty working tree
  const p = loadProgress();
  if (p.current_task?.status === 'in_progress') {
    warn(`Task ${p.current_task.id} was in progress. Check for uncommitted changes.`);
  }
}

function cmdStatus(): void {
  const p = loadProgress();
  console.log(`\n${B}═══ Project: ${p.project} ═══${N}`);
  console.log(`Last updated: ${D}${p.last_updated}${N}`);

  if (p.current_milestone) {
    const m = p.current_milestone;
    const pct = m.tasks_total > 0 ? Math.round((m.tasks_done / m.tasks_total) * 100) : 0;
    console.log(`\nMilestone: ${B}${m.id}${N} — ${m.name}`);
    console.log(`  Status: ${m.status} | Progress: ${m.tasks_done}/${m.tasks_total} (${pct}%)`);
    console.log(`  Done: ${m.tasks_done} | In Progress: ${m.tasks_in_progress} | Blocked: ${m.tasks_blocked} | Remaining: ${m.tasks_remaining}`);
    console.log(`  Branch: ${m.branch}`);
  } else {
    info('No active milestone. Ready for new work.');
  }

  if (p.current_task) {
    console.log(`\nCurrent task: ${Y}${p.current_task.id}${N} — ${p.current_task.description}`);
  }

  if (p.blockers.length > 0) {
    console.log(`\n${R}Blockers (${p.blockers.length}):${N}`);
    p.blockers.forEach((b) => console.log(`  ${R}•${N} ${b.task_id}: ${b.description}`));
  }

  if (p.completed_milestones.length > 0) {
    console.log(`\nCompleted: ${p.completed_milestones.map((m) => m.id).join(', ')}`);
  }
  console.log('');
}

function cmdNext(): void {
  const p = loadProgress();
  const graph = p.dependency_graph;
  const plan = loadPlan();

  // Find all task statuses from PLAN.md
  const donePattern = /\|\s*(M\d+-\d+)\s*\|.*?\|\s*✅/g;
  const doneSet = new Set<string>();
  let match;
  while ((match = donePattern.exec(plan)) !== null) doneSet.add(match[1]);

  const wipPattern = /\|\s*(M\d+-\d+)\s*\|.*?\|\s*🟡/g;
  const wipSet = new Set<string>();
  while ((match = wipPattern.exec(plan)) !== null) wipSet.add(match[1]);

  const todoPattern = /\|\s*(M\d+-\d+)\s*\|.*?\|\s*⬜/g;
  const todoTasks: string[] = [];
  while ((match = todoPattern.exec(plan)) !== null) todoTasks.push(match[1]);

  // Find first unblocked task
  const blockedIds = new Set(p.blockers.map((b) => b.task_id));

  for (const taskId of todoTasks) {
    if (blockedIds.has(taskId)) continue;

    const deps = graph[taskId]?.depends_on ?? [];
    const allDepsDone = deps.every((d) => doneSet.has(d));

    if (allDepsDone) {
      // Extract description from PLAN.md
      const descMatch = plan.match(new RegExp(`\\|\\s*${taskId}\\s*\\|[^|]*\\|\\s*([^|]+?)\\s*\\|`));
      const desc = descMatch?.[1]?.trim() ?? '';
      console.log(`\n${G}Next task:${N} ${Y}${taskId}${N} — ${desc}`);
      console.log(`\nRun: ${D}${PKG} run harness start ${taskId}${N}`);
      return;
    }
  }

  if (todoTasks.length === 0 && wipSet.size === 0) {
    ok('All tasks complete! Run: ' + PKG + ' run harness merge-gate');
  } else if (todoTasks.length > 0) {
    warn('All remaining tasks are blocked. Requires human input.');
    p.blockers.forEach((b) => console.log(`  ${R}•${N} ${b.task_id}: ${b.description}`));
  } else {
    info('Tasks in progress: ' + [...wipSet].join(', '));
  }
}

function cmdStart(taskId: string): void {
  if (!taskId) fail('Usage: harness start <task-id>  (e.g., harness start M1-003)');

  const p = loadProgress();
  let plan = loadPlan();

  // Verify task exists and is ⬜
  if (!plan.includes(`| ${taskId} `) && !plan.includes(`| ${taskId}\t`)) {
    // Try looser match
    if (!plan.includes(taskId)) fail(`Task ${taskId} not found in PLAN.md`);
  }

  // Update PLAN.md: ⬜ → 🟡
  const updated = plan.replace(
    new RegExp(`(\\|\\s*${taskId}\\s*\\|[^]*?)⬜`),
    '$1🟡',
  );
  if (updated === plan) warn(`Could not find ⬜ status for ${taskId} in PLAN.md`);
  else savePlan(updated);

  // Extract description
  const descMatch = plan.match(new RegExp(`\\|\\s*${taskId}\\s*\\|[^|]*\\|\\s*([^|]+?)\\s*\\|`));
  const desc = descMatch?.[1]?.trim() ?? taskId;

  // Update progress.json
  p.current_task = {
    id: taskId,
    story: '',
    description: desc,
    status: 'in_progress',
    started_at: new Date().toISOString(),
    files_touched: [],
    notes: '',
  };
  if (p.current_milestone) p.current_milestone.tasks_in_progress++;
  saveProgress(p);

  ok(`Started: ${taskId} — ${desc}`);
  info(`Write code, then run: ${PKG} run harness validate`);
}

function cmdValidate(full = false): void {
  const run = (cmd: string, label: string): void => {
    step(label);
    try {
      execSync(cmd, { stdio: 'inherit', shell: true });
      ok(label);
    } catch {
      fail(`${label} failed`);
    }
  };

  console.log(`\n${Y}═══ ${full ? 'Full Validation' : 'Validation'} ═══${N}\n`);

  // Lint auto-fix (allowed to partially fail)
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
    cmdStaleCheck();
  }

  console.log(`\n${G}═══ ${full ? 'Full validation' : 'Validation'} passed ═══${N}`);
}

function cmdDone(taskId: string): void {
  if (!taskId) fail('Usage: harness done <task-id>');

  const p = loadProgress();
  let plan = loadPlan();

  // Get latest commit hash
  let commitHash = '—';
  try {
    commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8', shell: true }).trim();
  } catch { /* no git */ }

  // Update PLAN.md: 🟡 → ✅ and fill commit column
  plan = plan.replace(
    new RegExp(`(\\|\\s*${taskId}\\s*\\|[^]*?)🟡([^]*?\\|)\\s*—\\s*\\|`),
    `$1✅$2 \`${commitHash}\` |`,
  );
  // Fallback: just change status if commit column pattern doesn't match
  plan = plan.replace(
    new RegExp(`(\\|\\s*${taskId}\\s*\\|[^]*?)🟡`),
    `$1✅`,
  );
  savePlan(plan);

  // Update progress.json
  p.current_task = null;
  if (p.current_milestone) {
    p.current_milestone.tasks_done++;
    p.current_milestone.tasks_in_progress = Math.max(0, p.current_milestone.tasks_in_progress - 1);
    p.current_milestone.tasks_remaining = Math.max(0, p.current_milestone.tasks_remaining - 1);
  }
  saveProgress(p);

  ok(`Completed: ${taskId} (commit: ${commitHash})`);
  info(`Run: ${PKG} run harness next`);
}

function cmdBlock(taskId: string, reason: string): void {
  if (!taskId || !reason) fail('Usage: harness block <task-id> <reason>');

  const p = loadProgress();

  p.blockers.push({
    task_id: taskId,
    description: reason,
    added_at: new Date().toISOString(),
  });

  if (p.current_task?.id === taskId) {
    p.current_task = null;
    if (p.current_milestone) {
      p.current_milestone.tasks_in_progress = Math.max(0, p.current_milestone.tasks_in_progress - 1);
      p.current_milestone.tasks_blocked++;
    }
  }
  saveProgress(p);

  warn(`Blocked: ${taskId} — ${reason}`);
  info(`Run: ${PKG} run harness next`);
}

function cmdMergeGate(): void {
  console.log(`\n${B}═══ Milestone Merge Gate ═══${N}\n`);

  cmdValidate(true);

  step('Generating changelog...');
  cmdChangelog();

  const p = loadProgress();
  console.log(`\n${G}═══ Merge gate passed ═══${N}`);
  console.log(`\nNext steps:`);
  console.log(`  1. cd ../<project-root>`);
  console.log(`  2. git merge ${p.current_milestone?.branch ?? 'milestone/M<n>'}`);
  console.log(`  3. git tag v<version>-${p.current_milestone?.id ?? 'M<n>'}`);
  console.log(`  4. ${PKG} run harness validate:full  (on main)`);
  console.log(`  5. git worktree remove <worktree-path>`);
}

function cmdFileGuard(stagedOnly = false): void {
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
    files = [...walk('src'), ...walk('tests')];
  }

  const violations: string[] = [];
  for (const file of files) {
    if (!existsSync(file)) continue;
    const lines = readFileSync(file, 'utf-8').split('\n').length;
    if (lines > FILE_LIMIT) violations.push(`  ${lines} lines: ${file}`);
  }

  if (violations.length > 0) {
    console.error(`\n${R}✗ ${violations.length} file(s) exceed ${FILE_LIMIT} lines:${N}\n`);
    violations.forEach((v) => console.error(v));
    fail('Split files before committing. (Iron Rule 1)');
  }
  ok(`All files within ${FILE_LIMIT}-line limit.`);
}

function cmdStaleCheck(quiet = false): void {
  let count = 0;
  const w = (msg: string) => { warn(msg); count++; };

  // .env.example vs source
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
            if (!exampleVars.has(m[1])) w(`.env.example missing: ${m[1]}`);
          }
        }
      }
    };
    scanDir('src');
  }

  // PLAN vs progress sync
  if (existsSync(PROGRESS_FILE) && existsSync(PLAN_FILE)) {
    const plan = loadPlan();
    const planDone = (plan.match(/✅/g) ?? []).length;
    const p = loadProgress();
    const progDone = p.current_milestone?.tasks_done ?? 0;
    if (planDone !== progDone) w(`PLAN.md: ${planDone} done vs progress.json: ${progDone}`);
  }

  // New modules not in ARCHITECTURE.md
  if (existsSync('ARCHITECTURE.md') && existsSync('src/modules')) {
    const arch = readFileSync('ARCHITECTURE.md', 'utf-8').toLowerCase();
    for (const d of readdirSync('src/modules', { withFileTypes: true })) {
      if (d.isDirectory() && !arch.includes(d.name.toLowerCase())) {
        w(`Module '${d.name}' not in ARCHITECTURE.md`);
      }
    }
  }

  // Unsynced plans
  cmdSyncPlans(quiet);

  if (count === 0) { if (!quiet) ok('No stale items.'); }
  else if (!quiet) console.error(`\n${count} stale item(s) found.`);
}

function cmdSyncPlans(quiet = false): void {
  if (!existsSync(PLANS_DIR) || !existsSync(PROGRESS_FILE)) return;
  const p = loadProgress();
  const synced = new Set(p.synced_plans ?? []);
  let count = 0;
  for (const file of readdirSync(PLANS_DIR)) {
    if (!file.endsWith('.md') || file === '.gitkeep' || synced.has(file)) continue;
    count++;
    if (!quiet) {
      console.log(`\n${Y}New plan:${N} ${file}`);
      console.log(readFileSync(join(PLANS_DIR, file), 'utf-8').slice(0, 500));
      if (readFileSync(join(PLANS_DIR, file), 'utf-8').length > 500) console.log('...(truncated)');
      info('Parse this plan → add milestone to PLAN.md → update progress.json');
      info(`Then run: add '${file}' to synced_plans in progress.json`);
    }
  }
  if (count === 0 && !quiet) ok('All plans synced.');
  else if (count > 0) warn(`${count} unsynced plan(s).`);
}

function cmdSchema(): void {
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

function cmdChangelog(): void {
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
    if (tm) { group = tm[1]; entry = `- \`${tm[1]}-${tm[2]}\` ${tm[3]} (\`${hash}\`)`; }
    else if (dm) { group = 'Docs'; entry = `- ${dm[1]} (\`${hash}\`)`; }
    else if (om) { group = om[1][0].toUpperCase() + om[1].slice(1); entry = `- ${om[2]} (\`${hash}\`)`; }
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

// ─── Router ───────────────────────────────────────────────────────────────────
const cmd = process.argv[2];
const arg1 = process.argv[3] ?? '';
const argRest = process.argv.slice(4).join(' ');

switch (cmd) {
  case 'init':           cmdInit(); break;
  case 'status':         cmdStatus(); break;
  case 'next':           cmdNext(); break;
  case 'start':          cmdStart(arg1); break;
  case 'validate':       cmdValidate(false); break;
  case 'validate:full':  cmdValidate(true); break;
  case 'done':           cmdDone(arg1); break;
  case 'block':          cmdBlock(arg1, argRest); break;
  case 'merge-gate':     cmdMergeGate(); break;
  case 'stale-check':    cmdStaleCheck(); break;
  case 'file-guard':     cmdFileGuard(process.argv.includes('--staged')); break;
  case 'changelog':      cmdChangelog(); break;
  case 'schema':         cmdSchema(); break;
  default:
    console.log(`
${B}harness${N} — project automation CLI

${Y}Session:${N}
  init              Boot session: sync plans, stale check, status
  status            Print current state

${Y}Task loop:${N}
  next              Find next unblocked task
  start <id>        Claim task → 🟡
  done <id>         Complete task → ✅
  block <id> <msg>  Mark task blocked

${Y}Validation:${N}
  validate          Lint → type-check → test
  validate:full     + integration + e2e + file-guard

${Y}Quality:${N}
  merge-gate        Full gate for milestone merge
  stale-check       Detect stale docs/env/plans
  file-guard        500-line limit check (--staged)
  schema            Validate progress.json
  changelog [from]  Generate release notes
`);
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

Note: add a `check-commit-msg` case to the CLI router, or keep the standalone
`scripts/check-commit-msg.ts` as the ONE exception (it needs the msg file path).

### .husky/pre-push
```bash
npx tsx scripts/harness.ts validate
```

---

## What this replaces

| Before (7 scripts + prose) | After (1 CLI) |
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
    "agents": { "type": "array" }
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

---

## Assembly Checklist

1. Generate `scripts/harness.ts` (the CLI) + `scripts/check-commit-msg.ts`
2. Generate `schemas/progress.schema.json`
3. Generate `.husky/pre-commit`, `.husky/commit-msg`, `.husky/pre-push`
4. Add `"harness": "tsx scripts/harness.ts"` + `"prepare": "husky"` to package.json
5. Add `tsx` as dev dependency
6. Wire lint-staged to call `harness schema` on progress.json changes
7. **Agents run commands, not edit JSON.** The CLI is the only writer of progress.json.
