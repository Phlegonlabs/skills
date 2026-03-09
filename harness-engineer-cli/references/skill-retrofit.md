## Retrofit Workflow

For existing projects. The goal is NOT to rewrite or re-scaffold the project. The goal
is to add the harness layer — the docs, scripts, hooks, configs, and conventions that
let agents work autonomously on future tasks.

### Retrofit Step 1: Analyze the Existing Project

Ask the user to upload or describe their project. Key files to request:

- `package.json` / `pyproject.toml` / `go.mod` (to understand stack + deps)
- Source directory structure (`ls src/` or equivalent)
- Any existing README, docs, or config files
- `.gitignore` (to see what's already there)
- Any existing CI workflows (`.github/workflows/`)
- Any existing linter/formatter configs (eslint, prettier, tsconfig, etc.)

If the user has uploaded files, read them directly.
If the user describes verbally, ask clarifying questions about:

**ask_user_input:**
1. **Tech stack** (multi_select): What does this project use?
   - Adapt options based on what you can see from uploaded files
   - Example: `TypeScript`, `React / Next.js`, `Node.js API`, `Python`, `Go`

2. **Package manager** (single_select, JS/TS only):
   - Options: `pnpm`, `bun`, `npm`
   - Auto-detect from lockfile if uploaded

Then analyze:
- What framework and runtime? (detect from deps)
- What's the source directory structure? (detect module/domain boundaries)
- What tests exist? (detect test framework, test directory)
- What CI exists? (detect workflows)
- What linting/formatting exists? (detect configs)
- What's the dependency layer structure? (detect import patterns)

### Retrofit Step 2: Generate Harness Layer

Based on the analysis, generate ONLY the harness files. Do NOT touch existing source code,
tests, or configs unless they conflict with the harness.

**Always generate (regardless of what exists):**

```
Files to ADD to the existing project:
├── AGENTS.md                    ← dynamically generated from analysis
├── CLAUDE.md                    ← identical to AGENTS.md
├── ARCHITECTURE.md              ← generated from actual source structure
├── docs/
│   ├── PRD.md                   ← lightweight — document what EXISTS, not what to build
│   ├── PLAN.md                  ← empty milestones section, ready for new work
│   ├── progress.json            ← initialized with project state
│   ├── learnings.md             ← empty, ready for agent learnings
│   ├── frontend-design.md       ← if project has frontend
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   ├── tech-debt/
│   │   └── .gitkeep
│   └── site/                    ← doc site skeleton
│       ├── SUMMARY.md
│       └── README.md
├── scripts/
│   ├── harness.ts               ← entry point router (~50 lines)
│   ├── check-commit-msg.ts      ← commit-msg hook helper
│   └── harness/                 ← CLI modules (config, types, state, worktree, tasks, validate, quality)
├── schemas/
│   └── progress.schema.json
├── .claude/
│   └── settings.json
└── .codex/
    └── config.toml
```

**Conditionally generate (only if not already present):**

| File | Generate if... | Skip if... |
|------|---------------|-----------|
| `.gitignore` | Missing or doesn't have .env patterns | Already comprehensive |
| `.env.example` | Missing | Already exists |
| `eslint.config.js` | No ESLint config exists | Already has ESLint (preserve theirs) |
| `.prettierrc` | No Prettier config exists | Already has Prettier (preserve theirs) |
| `tsconfig.json` | No tsconfig exists | Already has one (preserve theirs) |
| `.husky/` hooks | No husky setup exists | Already has hooks (merge, don't replace) |
| CI workflows | No CI exists | Already has CI (augment, don't replace) |
| `Dockerfile` | No Docker setup exists | Already has Docker (preserve theirs) |
| `docker-compose.yml` | No compose exists | Already has one (preserve theirs) |

**Rule: NEVER overwrite existing configs.** If the project already has ESLint, tsconfig,
Prettier, CI, Docker — keep theirs. Only add the harness-specific files that don't exist.

If an existing config conflicts with Iron Rules (e.g., ESLint is on `warn` instead of
`error` for `no-explicit-any`), note it in a `docs/tech-debt/harness-alignment.md` file
as a suggestion, but do NOT force the change.

### Retrofit Step 3: Adapt AGENTS.md / CLAUDE.md to the Existing Project

The Iron Rules template is copied verbatim (same as greenfield).

Everything else is generated from what ACTUALLY exists:

- **Project overview** — describe what this project does based on README/package.json/source
- **Quick start** — the REAL commands this project uses (detect from existing scripts)
- **Repository map** — point to the actual directories and files that exist
- **Architecture rules** — derive from the actual import patterns and module structure
- **Dev environment tips** — based on the actual dev workflow (existing scripts, Docker, etc.)
- **Testing instructions** — whatever test framework and commands they already use
  + add the new harness scripts (`validate`, `stale-check`, etc.)
- **Session Init / Task Loop / Merge Gate / Stale Detection** — standard templates,
  with commands adapted to the existing package manager and test runner
- **Plan File Convention** — standard, pointing to `docs/exec-plans/active/`

### Retrofit Step 4: Generate Lightweight PRD

For a retrofit, the PRD is a **snapshot of what exists**, not a design document.
It's shorter than a greenfield PRD.

```markdown
# Product Requirements Document: <Project Name>

## 1. Overview
What this product currently does, based on analysis of the codebase.

## 2. Current State
- Tech stack: <detected>
- Key modules/domains: <detected from src/>
- Test coverage: <detected — what exists>
- CI/CD: <detected — what's set up>
- Deploy target: <detected or ask user>

## 3. Existing Features (as-is)
Brief inventory of what's already built, organized by module/domain.
Not a design doc — just a map of what exists for agent context.

| Module | Description | Has Tests? |
|--------|------------|-----------|
| auth   | JWT-based authentication | Yes (12 tests) |
| users  | User CRUD + profiles | Partial (3 tests) |
| ...    | ... | ... |

## 4. Tech Debt (detected)
Issues found during analysis:
- Files over 500 lines: <list>
- Missing test coverage: <modules without tests>
- Missing .env.example entries: <vars in code but not in example>
- Stale docs: <any detected>

## 5. Future Work
(Empty — to be filled via plan mode when user adds new work)

## 6. Tech Stack
| Layer | Choice | Detected From |
|-------|--------|--------------|
```

### Retrofit Step 5: Initialize progress.json

```json
{
  "project": "<detected project name>",
  "last_updated": "<now>",
  "last_agent": "human",
  "current_milestone": null,
  "current_task": null,
  "completed_milestones": [],
  "blockers": [],
  "learnings": [],
  "dependency_graph": {},
  "synced_plans": [],
  "agents": [],
  "finish_jobs": [],
  "learnings": [],
  "blockers": []
}
```

No milestones, no tasks, no dependency graph — the project already exists.
All future work enters through plan mode → progress-sync → Task Execution Loop.

### Retrofit Step 6: Wire CLI into Existing package.json

**For JS/TS projects:** Add the harness CLI to the EXISTING package.json. Do NOT replace existing scripts.

```
Merge into existing "scripts":
  "harness": "tsx scripts/harness.ts"

Add to devDependencies:
  "tsx": "^4.0.0"

If "prepare" script exists → append husky to it
If "prepare" doesn't exist → add "prepare": "husky"
```

The CLI calls `<pkg-mgr> run test`, which runs whatever `test` script is defined in
your package.json. If your project uses `jest`, make sure `"test": "jest"` is in
package.json scripts. Same for `mocha`, `ava`, or any other runner. The harness CLI
delegates to your existing scripts — it doesn't auto-detect frameworks.

**For non-JS/TS projects (Python, Go, Rust):** Two options:

1. **Recommended:** Install Node.js alongside the project's toolchain. Add `scripts/harness.ts`
   + `scripts/harness/` as-is. Wire into the existing Makefile:
   ```makefile
   harness: npx tsx scripts/harness.ts $(ARGS)
   ```

2. **No Node.js:** Use `references/harness-native.md` to generate `scripts/harness.sh`.
   Ensure the existing Makefile has a `validate` target. Add pre-commit hooks using the
   language-appropriate framework (see harness-native.md). Note the feature tradeoffs in
   AGENTS.md / CLAUDE.md.

### Retrofit Step 7: Present and Review

Present to the user:
1. File tree of what will be ADDED (not what exists)
2. List of existing configs that were PRESERVED (not overwritten)
3. Tech debt items detected
4. The generated AGENTS.md / CLAUDE.md for review
5. Ask: "Does this look right? Should I adjust anything?"

After confirmation, the user:
1. Copies the generated files into their existing project
2. Runs `<pkg-mgr> install` (to pick up tsx + husky)
3. Commits: `[scaffold] add harness framework`
4. Opens Claude Code / Codex → agent reads AGENTS.md / CLAUDE.md → ready

### After Retrofit: How It Works

The project now has the full harness layer but NO pending milestones.
The flow is entirely plan-mode-driven:

```
User opens Claude Code / Codex
  → Agent reads AGENTS.md / CLAUDE.md (Session Init)
  → Reads progress.json (no active milestones)
  → Runs stale-check (flags any issues)
  → Reports: "Harness active. No pending work. Ready for new tasks."

User enters plan mode
  → Describes new feature / fix / refactor
  → Plan file saved to docs/exec-plans/active/
  → Switch to normal mode

Agent detects new plan (progress-sync)
  → Parses plan into PRD update + new Milestone in PLAN.md
  → Updates progress.json with dependency graph
  → Creates worktree → Task Execution Loop
  → Same iron rules, same testing, same atomic commits
  → Milestone done → merge gate → auto-finish → optional release tag or new plan → repeat

Repeat.
```

No long-task bootstrap. No initial milestone grind. The project is already built.
The harness just gives agents the rails to do future work safely.

---
