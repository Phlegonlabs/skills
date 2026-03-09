# Phlegonlabs Skills

Installable agent skills for Claude Code and Codex. This repository focuses on project bootstrap, harness engineering, and long-running execution workflows that are meant to live in-source with the code they govern.

Each top-level directory is an installable skill.

## Install

Install the full collection:

```bash
npx skills add Phlegonlabs/skills
```

Install a single skill:

```bash
npx skills add Phlegonlabs/skills/<skill-name>
```

Examples:

```bash
npx skills add Phlegonlabs/skills/harness-engineer
npx skills add Phlegonlabs/skills/harness-engineer-cli
npx skills add Phlegonlabs/skills/project-long-task
npx skills add Phlegonlabs/skills/anicenttwo-proj-init
```

## Skills

| Skill | Use it for | Notes |
| --- | --- | --- |
| [harness-engineer](./harness-engineer/) | Bootstrapping a new repo or retrofitting an existing one with harness docs, plans, and automation | Generates AGENTS/CLAUDE docs, architecture docs, plans, schemas, hooks, and supporting scripts |
| [harness-engineer-cli](./harness-engineer-cli/) | CLI-first harness setup for agent-driven development on Windows, macOS, and Linux | Cross-platform variant with a unified `harness` workflow and deeper runtime references |
| [project-long-task](./project-long-task/) | Creating or updating a long-running milestone-based project workflow | Best when the main need is disciplined planning and execution docs rather than full repo scaffolding |
| [anicenttwo-proj-init](./anicenttwo-proj-init/) | Cross-agent project initialization, migration, and workflow repair | Includes question-pack driven setup, plan presets, and template assembly scripts |

## Which One To Pick

- Choose `harness-engineer` when you want the standard harness setup for a new or existing codebase.
- Choose `harness-engineer-cli` when you want the CLI-centric harness model with explicit task-loop commands and cross-platform runtime guidance.
- Choose `project-long-task` when the job is mostly about getting the docs, milestones, and execution discipline right for a complex build.
- Choose `anicenttwo-proj-init` when you need scaffold assembly, migration helpers, or repair flows for Claude/Codex-oriented project setup.

## Repository Layout

```text
skills/
├── harness-engineer/
├── harness-engineer-cli/
├── project-long-task/
├── anicenttwo-proj-init/
└── skills-lock.json
```

## Notes

- Skill behavior lives in each directory's `SKILL.md`.
- Some skills also ship supporting `README.md`, `references/`, `assets/`, and `scripts/` files used during generation.
- The root README is only the catalog; the per-skill docs are the source of truth for workflow details.
