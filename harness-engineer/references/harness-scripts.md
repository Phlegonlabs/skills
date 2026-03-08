# Harness Scripts & Automation (TypeScript / Cross-Platform)

All scripts are TypeScript, run with `tsx` (zero-config TS executor).
They work identically on Windows, macOS, and Linux — no bash dependency.

Add `tsx` as a dev dependency: `<pkg-mgr> add -D tsx`

Scripts live in `scripts/` and are wired into package.json.

---

## scripts/validate.ts

The single gate command. Runs lint:fix → lint → type-check → test.

```typescript
import { execSync } from 'node:child_process';
import process from 'node:process';

const PKG = process.env.PKG_MGR ?? 'pnpm';

const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const NC = '\x1b[0m';

function step(msg: string): void {
  console.log(`${YELLOW}▶ ${msg}${NC}`);
}

function pass(msg: string): void {
  console.log(`${GREEN}✓ ${msg}${NC}`);
}

function fail(msg: string): never {
  console.error(`${RED}✗ ${msg}${NC}`);
  process.exit(1);
}

function run(cmd: string, label: string): void {
  step(label);
  try {
    execSync(cmd, { stdio: 'inherit', shell: true });
    pass(label);
  } catch {
    fail(`${label} failed — fix errors above`);
  }
}

// Lint auto-fix (allowed to partially fail)
step('Lint auto-fix');
try {
  execSync(`${PKG} run lint:fix`, { stdio: 'inherit', shell: true });
} catch {
  // auto-fix may exit non-zero if it couldn't fix everything — that's OK
}
pass('Lint auto-fix complete');

run(`${PKG} run lint`, 'Lint check (strict)');
run(`${PKG} run type-check`, 'Type check');
run(`${PKG} run test`, 'Tests');

console.log(`\n${GREEN}═══ All gates passed ═══${NC}`);
```

---

## scripts/validate-full.ts

Extended gate for milestone merges. Adds integration + e2e + file-guard.

```typescript
import { execSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import process from 'node:process';

const PKG = process.env.PKG_MGR ?? 'pnpm';

const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';
const NC = '\x1b[0m';

function step(msg: string): void {
  console.log(`${YELLOW}▶ ${msg}${NC}`);
}

function run(cmd: string, label: string): void {
  step(label);
  try {
    execSync(cmd, { stdio: 'inherit', shell: true });
    console.log(`${GREEN}✓ ${label}${NC}`);
  } catch {
    console.error(`${RED}✗ ${label} failed${NC}`);
    process.exit(1);
  }
}

// Run base validate
run(`${PKG} run validate`, 'Base validation');

// Integration tests
if (existsSync('tests/integration') && readdirSync('tests/integration').length > 0) {
  run(`${PKG} run test:integration`, 'Integration tests');
}

// E2E tests
if (existsSync('tests/e2e') && readdirSync('tests/e2e').length > 0) {
  run(`${PKG} run test:e2e`, 'E2E tests');
}

// File size guard
run(`${PKG} run file-guard`, 'File size check (500-line limit)');

// Stale check
run(`${PKG} run stale-check`, 'Stale detection');

console.log(`\n${GREEN}═══ Full validation passed — ready to merge ═══${NC}`);
```

---

## scripts/file-guard.ts

Enforces Iron Rule 1: no file over 500 lines.

```typescript
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';
import process from 'node:process';

const LIMIT = 500;
const SOURCE_EXTENSIONS = new Set([
  '.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.vue', '.svelte',
]);
const IGNORE_DIRS = new Set(['node_modules', 'dist', 'build', '.next', 'out', 'coverage', '.git']);

function walk(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walk(fullPath));
    } else if (SOURCE_EXTENSIONS.has(extname(entry.name))) {
      results.push(fullPath);
    }
  }
  return results;
}

const violations: string[] = [];

for (const file of walk('src').concat(walk('tests'))) {
  const content = readFileSync(file, 'utf-8');
  const lines = content.split('\n').length;
  if (lines > LIMIT) {
    violations.push(`  OVER ${LIMIT} lines (${lines}): ${file}`);
  }
}

if (violations.length > 0) {
  console.error(`\n✗ ${violations.length} file(s) exceed the ${LIMIT}-line limit:\n`);
  violations.forEach((v) => console.error(v));
  console.error(`\nSplit them before committing. (Iron Rule 1)`);
  process.exit(1);
} else {
  console.log(`✓ All source files are within the ${LIMIT}-line limit.`);
}
```

---

## scripts/stale-check.ts

Detects stale docs, env vars, plan sync, and modules.

```typescript
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, basename } from 'node:path';
import process from 'node:process';

let staleCount = 0;

function warn(msg: string): void {
  console.warn(`⚠ STALE: ${msg}`);
  staleCount++;
}

// --- .env.example vs source code env usage ---
if (existsSync('.env.example') && existsSync('src')) {
  const example = readFileSync('.env.example', 'utf-8');
  const exampleVars = new Set(
    example.split('\n')
      .map((line) => line.split('=')[0]?.trim())
      .filter((v) => v && !v.startsWith('#')),
  );

  function scanForEnvVars(dir: string): Set<string> {
    const vars = new Set<string>();
    const envPatterns = [
      /process\.env\.(\w+)/g,
      /Bun\.env\.(\w+)/g,
      /env\(['"](\w+)['"]\)/g,
    ];
    for (const entry of readdirSync(dir, { withFileTypes: true, recursive: true })) {
      if (!entry.isFile()) continue;
      if (entry.name.endsWith('.d.ts')) continue;
      const ext = entry.name.split('.').pop();
      if (!['ts', 'tsx', 'js', 'jsx'].includes(ext ?? '')) continue;
      const fullPath = join(entry.parentPath ?? dir, entry.name);
      const content = readFileSync(fullPath, 'utf-8');
      for (const pattern of envPatterns) {
        let match;
        while ((match = pattern.exec(content)) !== null) {
          vars.add(match[1]);
        }
      }
    }
    return vars;
  }

  const usedVars = scanForEnvVars('src');
  for (const v of usedVars) {
    if (!exampleVars.has(v)) {
      warn(`.env.example missing: ${v} (used in source code)`);
    }
  }
}

// --- PLAN.md vs progress.json sync ---
if (existsSync('docs/progress.json') && existsSync('docs/PLAN.md')) {
  const plan = readFileSync('docs/PLAN.md', 'utf-8');
  const planDone = (plan.match(/✅/g) ?? []).length;

  const progress = JSON.parse(readFileSync('docs/progress.json', 'utf-8'));
  const progressDone = progress.current_milestone?.tasks_done ?? 0;

  if (planDone !== progressDone) {
    warn(`PLAN.md shows ${planDone} done tasks, progress.json shows ${progressDone} — out of sync`);
  }
}

// --- New modules not in ARCHITECTURE.md ---
if (existsSync('ARCHITECTURE.md') && existsSync('src/modules')) {
  const arch = readFileSync('ARCHITECTURE.md', 'utf-8').toLowerCase();
  for (const dir of readdirSync('src/modules', { withFileTypes: true })) {
    if (dir.isDirectory() && !arch.includes(dir.name.toLowerCase())) {
      warn(`Module '${dir.name}' exists in src/modules/ but not in ARCHITECTURE.md`);
    }
  }
}

// --- New plan files not synced ---
if (existsSync('docs/exec-plans/active') && existsSync('docs/progress.json')) {
  const progress = JSON.parse(readFileSync('docs/progress.json', 'utf-8'));
  const synced = new Set(progress.synced_plans ?? []);
  for (const file of readdirSync('docs/exec-plans/active')) {
    if (file.endsWith('.md') && !synced.has(file) && file !== '.gitkeep') {
      warn(`Plan file '${file}' not synced to progress.json`);
    }
  }
}

// --- docs/site/ dead links ---
if (existsSync('docs/site/SUMMARY.md')) {
  const summary = readFileSync('docs/site/SUMMARY.md', 'utf-8');
  const links = [...summary.matchAll(/\(([^)]+\.md)\)/g)].map((m) => m[1]);
  for (const link of links) {
    if (!existsSync(join('docs/site', link))) {
      warn(`SUMMARY.md references '${link}' but file doesn't exist`);
    }
  }
}

// --- Report ---
console.log('');
if (staleCount === 0) {
  console.log('✓ No stale docs detected.');
} else {
  console.error(`Found ${staleCount} stale item(s). Fix and commit.`);
  process.exit(1);
}
```

---

## scripts/progress-sync.ts

Detects new plan files in exec-plans/active/ that haven't been synced.

```typescript
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import process from 'node:process';

const PLANS_DIR = 'docs/exec-plans/active';
const PROGRESS_FILE = 'docs/progress.json';

if (!existsSync(PLANS_DIR)) {
  console.log('No exec-plans/active/ directory found.');
  process.exit(0);
}

if (!existsSync(PROGRESS_FILE)) {
  console.log('No progress.json found. Create it first.');
  process.exit(1);
}

const progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
const synced = new Set<string>(progress.synced_plans ?? []);

let unsynced = 0;

for (const file of readdirSync(PLANS_DIR)) {
  if (!file.endsWith('.md') || file === '.gitkeep') continue;
  if (synced.has(file)) continue;

  unsynced++;
  console.log(`\nNew plan detected: ${file}`);
  console.log('---');
  console.log(readFileSync(`${PLANS_DIR}/${file}`, 'utf-8'));
  console.log('---');
  console.log('ACTION REQUIRED: Parse this plan and add as new milestone to PLAN.md + progress.json');
  console.log(`Then add '${file}' to the synced_plans array in progress.json.\n`);
}

if (unsynced === 0) {
  console.log('✓ All plans synced.');
} else {
  console.error(`${unsynced} plan(s) need syncing.`);
  process.exit(1);
}
```

---

## scripts/validate-schema.ts

Validates progress.json against the JSON Schema.

```typescript
import { existsSync, readFileSync } from 'node:fs';
import process from 'node:process';

const PROGRESS = 'docs/progress.json';
const SCHEMA = 'schemas/progress.schema.json';

if (!existsSync(PROGRESS)) {
  console.log('✓ No progress.json to validate (skip).');
  process.exit(0);
}

if (!existsSync(SCHEMA)) {
  console.log('⚠ Schema not found — skip validation.');
  process.exit(0);
}

// Lightweight validation without external deps — check required fields and types
const data = JSON.parse(readFileSync(PROGRESS, 'utf-8'));
const schema = JSON.parse(readFileSync(SCHEMA, 'utf-8'));

const errors: string[] = [];

function checkRequired(obj: unknown, required: string[], path: string): void {
  if (typeof obj !== 'object' || obj === null) {
    errors.push(`${path}: expected object, got ${typeof obj}`);
    return;
  }
  for (const key of required) {
    if (!(key in (obj as Record<string, unknown>))) {
      errors.push(`${path}: missing required field '${key}'`);
    }
  }
}

// Top-level required fields
checkRequired(data, schema.required ?? [], 'root');

// Milestone ID pattern
if (data.current_milestone?.id && !/^M\d+$/.test(data.current_milestone.id)) {
  errors.push(`current_milestone.id: '${data.current_milestone.id}' doesn't match pattern ^M[0-9]+$`);
}

// Task ID pattern
if (data.current_task?.id && !/^M\d+-\d+$/.test(data.current_task.id)) {
  errors.push(`current_task.id: '${data.current_task.id}' doesn't match pattern ^M[0-9]+-[0-9]+$`);
}

// Dependency graph keys pattern
if (data.dependency_graph) {
  for (const key of Object.keys(data.dependency_graph)) {
    if (!/^M\d+-\d+$/.test(key)) {
      errors.push(`dependency_graph: key '${key}' doesn't match pattern ^M[0-9]+-[0-9]+$`);
    }
  }
}

// Agent type enum
if (data.agents) {
  for (const agent of data.agents) {
    if (!['claude-code', 'codex'].includes(agent.type)) {
      errors.push(`agents: type '${agent.type}' must be 'claude-code' or 'codex'`);
    }
  }
}

if (errors.length > 0) {
  console.error('✗ progress.json schema validation failed:\n');
  errors.forEach((e) => console.error(`  ${e}`));
  process.exit(1);
} else {
  console.log('✓ progress.json is valid.');
}
```

---

## scripts/changelog.ts

Generates release notes grouped by milestone from commit messages.

```typescript
import { execSync } from 'node:child_process';
import process from 'node:process';

const from = process.argv[2] ?? '';
const to = process.argv[3] ?? 'HEAD';

let range: string;
let header: string;

if (from) {
  range = `${from}..${to}`;
  header = `# Changelog (${from} → ${to})`;
} else {
  // Try to find latest tag
  try {
    const lastTag = execSync('git describe --tags --abbrev=0', { encoding: 'utf-8' }).trim();
    range = `${lastTag}..${to}`;
    header = `# Changelog (${lastTag} → ${to})`;
  } catch {
    range = to;
    header = '# Changelog (all commits)';
  }
}

const log = execSync(`git log --oneline --pretty=format:"%s|%h" ${range}`, {
  encoding: 'utf-8',
  shell: true,
}).trim();

if (!log) {
  console.log(header);
  console.log('\nNo commits in range.');
  process.exit(0);
}

const milestones = new Map<string, string[]>();
const order: string[] = [];

for (const line of log.split('\n')) {
  const [msg, hash] = line.split('|');
  if (!msg) continue;

  const taskMatch = msg.match(/^\[(M\d+)-(\d+)\]\s+(.+)/);
  const docMatch = msg.match(/^\[docs\]\s+(.+)/);
  const otherMatch = msg.match(/^\[(scaffold|fix|refactor|ci)\]\s+(.+)/);

  let group: string;
  let entry: string;

  if (taskMatch) {
    group = taskMatch[1];
    entry = `- \`${taskMatch[1]}-${taskMatch[2]}\` ${taskMatch[3]} (\`${hash}\`)`;
  } else if (docMatch) {
    group = 'Documentation';
    entry = `- ${docMatch[1]} (\`${hash}\`)`;
  } else if (otherMatch) {
    group = otherMatch[1].charAt(0).toUpperCase() + otherMatch[1].slice(1);
    entry = `- ${otherMatch[2]} (\`${hash}\`)`;
  } else {
    group = 'Other';
    entry = `- ${msg} (\`${hash}\`)`;
  }

  if (!milestones.has(group)) {
    milestones.set(group, []);
    order.push(group);
  }
  milestones.get(group)!.push(entry);
}

console.log(header);
console.log('');

for (const group of order) {
  console.log(`## ${group}`);
  console.log('');
  for (const entry of milestones.get(group)!) {
    console.log(entry);
  }
  console.log('');
}
```

---

## package.json scripts

```json
{
  "scripts": {
    "lint": "eslint . --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:integration": "vitest run --project integration",
    "test:e2e": "vitest run --project e2e",
    "test:watch": "vitest",
    "validate": "tsx scripts/validate.ts",
    "validate:full": "tsx scripts/validate-full.ts",
    "file-guard": "tsx scripts/file-guard.ts",
    "stale-check": "tsx scripts/stale-check.ts",
    "progress-sync": "tsx scripts/progress-sync.ts",
    "validate-schema": "tsx scripts/validate-schema.ts",
    "changelog": "tsx scripts/changelog.ts",
    "prepare": "husky"
  }
}
```

---

## Assembly Rules

1. Add `tsx` as a dev dependency: `<pkg-mgr> add -D tsx`
2. Generate ALL scripts into `scripts/` as `.ts` files
3. Set `PKG_MGR` env var in validate.ts to match chosen package manager
4. Adjust `SOURCE_EXTENSIONS` in file-guard.ts to match the project's stack
5. Wire scripts into package.json using `tsx scripts/<name>.ts`
6. All scripts use only `node:` built-in modules — zero external dependencies
7. Scripts work identically on Windows, macOS, and Linux
8. For Python/Go/Rust projects, generate equivalent scripts in the project's language
   or keep the TS versions (they still work if Node.js is available as a dev tool)
