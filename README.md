# Skills

A collection of agent skills for Claude Code and other AI coding tools.

## Installation

```bash
# Install all skills
npx skills add Phlegonlabs/skills

# Install a specific skill
npx skills add Phlegonlabs/skills -s project-long-task

# Install globally (available across all projects)
npx skills add Phlegonlabs/skills -g
```

## Available Skills

### project-long-task

A structured project initialization workflow for long-running, milestone-based builds. Collects requirements through an interactive interview, then generates a complete documentation scaffold that guides autonomous execution.

**When to use:** Starting a new project, kicking off a long-running build, or setting up a milestone-based plan.

**What it generates:**
- `docs/architecture.md` — Project spec, user journeys, technical architecture
- `docs/plans.md` — Milestones with sub-tasks and acceptance criteria
- `docs/implement.md` — Execution rules for disciplined autonomous work
- `docs/documentation.md` — User-facing docs
- `CLAUDE.md` + `AGENT.md` — Quick-reference for AI coding tools

## Updating

```bash
# Check for updates
npx skills check

# Update all installed skills
npx skills update
```
