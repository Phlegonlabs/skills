# Phlegonlabs Skills

Reusable agent skills for Claude Code and Codex, designed to be installed per-repo and executed in-source.

This collection focuses on:

- project bootstrap and migration
- long-running execution and milestone tracking
- cross-agent and CLI-friendly task orchestration

Each top-level folder is an installable skill package.

---

## Quick Install

Install the full collection:

```bash
npx skills add Phlegonlabs/skills
```

Install one skill only:

```bash
npx skills add Phlegonlabs/skills/<skill-name>
```

Examples:

```bash
npx skills add Phlegonlabs/skills/harness-engineer-cli
npx skills add Phlegonlabs/skills/project-long-task
npx skills add Phlegonlabs/skills/anicenttwo-proj-init
```

---

## Skills

| Skill | Purpose | Use this when |
| --- | --- | --- |
| [harness-engineer-cli](./harness-engineer-cli/) | CLI-centric harness workflow | You need the same harness model with Windows/macOS/Linux command guidance and script-first flow |
| [project-long-task](./project-long-task/) | Long-run task planning and tracking | Your work is milestone-heavy and needs disciplined execution checklists and pacing |
| [anicenttwo-proj-init](./anicenttwo-proj-init/) | Project initialization and migration support | You need migration helpers, question-driven setup, and template assembly for Claude/Codex |

---

## Repository Layout

```text
skills/
├── anicenttwo-proj-init/
├── harness-engineer-cli/
├── project-long-task/
└── skills-lock.json
```

Each skill directory typically includes:

- `SKILL.md` for runtime instructions
- optional `README.md` for user-facing usage notes
- optional `references/`, `assets/`, and `scripts/`

---

## How to choose

- Use `harness-engineer-cli` when you want a CLI-oriented harness workflow on top of existing or new repos.
- Use `project-long-task` when planning, milestones, and execution control are the top priority.
- Use `anicenttwo-proj-init` for migration, repair, or re-init flows.

---

## Contributing

Contributions should target the relevant skill folder and keep each `SKILL.md` as the canonical source of truth.

Prefer small, focused diffs:

1. Update `SKILL.md` first.
2. Keep scripts, references, and templates close to the skill they support.
3. Keep cross-skill behavior explicit and avoid hidden assumptions.
