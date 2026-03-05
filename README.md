# Skills

A collection of agent skills for Claude Code and other AI coding tools.

## Installation

```bash
npx skills add Phlegonlabs/skills
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [project-init](https://skills.sh/Phlegonlabs/skills/project-init) | Initialize a brand-new long-running project with a full docs/tasks/hooks workflow (self-contained skill package) |
| [project-convert](https://skills.sh/Phlegonlabs/skills/project-convert) | Convert an existing codebase into the structured long-running workflow (self-contained skill package) |
| [project-update](https://skills.sh/Phlegonlabs/skills/project-update) | Update an already-initialized long-running project with milestone-driven docs and execution rules (self-contained skill package) |
| [full-project-skill](https://skills.sh/Phlegonlabs/skills/full-project-skill) | Legacy all-in-one workflow (kept for backward compatibility) |

## Notes

- `project-init`, `project-convert`, and `project-update` are now fully split, self-contained skills.
- Each split skill carries its own `references/`, `assets/`, `scripts/`, and `tests/`.
