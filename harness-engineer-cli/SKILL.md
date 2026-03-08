---
name: harness-engineer-cli
description: >
  Bootstrap a complete agent-first project OR retrofit an existing project with the harness
  framework — AGENTS.md, CLAUDE.md, execution plans, PRD, and automation scripts, all based
  on Harness Engineering principles. Use this skill whenever the user wants to start a new
  project, initialize a codebase, create a project scaffold, set up a monorepo, or says
  anything like "new project", "bootstrap", "init", "scaffold", "start building", "project setup",
  "create an app", "set up a repo". ALSO trigger when the user wants to add harness to an
  existing project, says "retrofit", "add AGENTS.md to my project", "set up harness for my repo",
  "convert my project", or mentions AGENTS.md, harness engineering, agent-first development.
  Even if the user just describes an idea and wants to "get started", this is the skill to use.
---

# Harness Engineer

This skill creates a complete, agent-first project foundation based on Harness Engineering
principles. It works in TWO modes:

- **Greenfield** — New project from scratch. Full product discovery, PRD, scaffold, everything.
- **Retrofit** — Existing project. Analyze the codebase, add harness layer on top. No scaffold
  generation, no long-task bootstrap. Future work flows through plan mode.

The philosophy: AGENTS.md is a **table of contents, not an encyclopedia**. Keep it concise,
pointing to deeper sources of truth. All project knowledge lives in the repo as versioned,
discoverable artifacts — because if an agent can't see it, it doesn't exist.

---

## How This Skill Is Structured (Read This First)

This skill is split into focused reference files to avoid loading everything upfront.
**Read only the file(s) relevant to the current task. Do NOT pre-load all files.**

| File | When to read |
|------|-------------|
| `references/skill-retrofit.md` | User wants to add harness to an existing project |
| `references/skill-greenfield.md` | User wants a new project (Phases 1–3: discovery, PRD, scaffold) |
| `references/skill-artifacts.md` | During generation — all artifact templates (AGENTS.md, ARCHITECTURE.md, PLAN.md, configs) |
| `references/skill-execution.md` | After scaffold — execution runtime, task loop, git workflow, doc site (Phases 4–6) |
| `references/skill-mobile.md` | Project type is Mobile (Expo/React Native) — architecture, EAS build, iOS/Android deploy |
| `references/skill-auth.md` | Project includes authentication — Better Auth setup, env vars, OAuth, mobile auth |

**Load order:**
- Retrofit path: `skill-retrofit.md` → then `skill-artifacts.md` when generating files
- Greenfield path: `skill-greenfield.md` → then `skill-artifacts.md` → then `skill-execution.md`
- Mobile projects: also read `skill-mobile.md` before generating scaffold
- Desktop projects (Electron/Tauri): no dedicated skill file — run web search for
  `<chosen framework> project structure best practices` and adapt the web app scaffold.
  Key differences: main process + renderer split, IPC patterns, platform-specific build
- Any project with auth: also read `skill-auth.md` before generating auth code
- Frontend projects: `docs/frontend-design.md` is generated from the `frontend-design`
  skill at `/mnt/skills/public/frontend-design/SKILL.md`. If that skill is not available,
  generate a minimal fallback with: color palette, typography scale, spacing system,
  component naming conventions, and "no generic AI aesthetics" principle.

---

## Mode Selection

First, determine which mode to use. If the user uploads files or mentions an existing
project, use Retrofit. If they describe something new, use Greenfield.

If unclear, ask:

**ask_user_input:**
1. **Mode** (single_select): What's the starting point?
   - Options: `New project from scratch`, `Add harness to an existing project`

If **New project from scratch** → read `references/skill-greenfield.md` and follow it
If **Add harness to existing project** → read `references/skill-retrofit.md` and follow it
