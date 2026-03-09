---
name: harness-engineer-cli
version: 2026.03.10
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
| `references/skill-desktop.md` | Project type is Desktop (Electron/Tauri) — shell split, IPC/commands, updater, packaging, testing |
| `references/skill-mobile.md` | Project type is Mobile (Expo/React Native) — architecture, EAS build, iOS/Android deploy |
| `references/skill-auth.md` | Project includes authentication — Better Auth setup, env vars, OAuth, mobile auth |
| `references/harness-native.md` | Project is non-JS/TS AND user does not want Node.js — shell-based CLI, Makefile integration, pre-commit hooks |
| `references/project-configs.md` | During Phase 3 scaffold generation — tsconfig, pyproject.toml, go.mod, Cargo.toml, CI workflows, Docker |
| `references/harness-cli.md` | During Phase 3 scaffold generation — CLI source code, schema, git hooks (TypeScript version) |
| `references/scaffold-templates.md` | During Phase 3 if project needs scaffold commands — MCP, SKILL.md, Cloudflare, agent capability templates |
| `references/eslint-configs.md` | During Phase 3 for JS/TS projects — ESLint flat config templates |
| `references/gitignore-templates.md` | During Phase 3 — .gitignore templates per stack |
| `references/execution-runtime.md` | During Phase 3 — agent guidelines: context budget, parallel coordination, quality gates |
| `references/execution-advanced.md` | Only when needed — release automation, docs site, memory system |

**Load order:**
- Retrofit path: `skill-retrofit.md` → then `skill-artifacts.md` when generating files
- Greenfield path: `skill-greenfield.md` → then `skill-artifacts.md` → Phase 3 exit gate in
  `skill-greenfield.md` → then `skill-execution.md`
- Mobile projects: also read `skill-mobile.md` before generating scaffold
- Desktop projects: also read `skill-desktop.md` before generating scaffold. Use targeted web
  search only for version-sensitive packaging, signing, notarization, updater, or plugin details
  that are not already covered by the desktop reference.
- Non-JS/TS projects without Node.js: also read `harness-native.md` before generating the
  harness layer. This provides the shell-based CLI, Makefile integration, and pre-commit hooks
  that replace the TypeScript CLI and husky.
- Agent Tool / MCP Server projects: `skill-greenfield.md` → `skill-artifacts.md` (includes
  SKILL.md template for agent discovery) → `skill-execution.md`. The generated project will
  include a `SKILL.md` at the root that describes tools, connection methods, and env vars
  so other AI agents can discover and use the MCP server.
- Any project with auth: also read `skill-auth.md` before generating auth code
- Mixed-language monorepos: keep `skill-greenfield.md` as the primary workflow, then use
  `project-configs.md` for Python / Go / Rust manifests. Do not force JS-only workspace rules onto
  non-JS apps.
- Frontend projects: `docs/frontend-design.md` must be bundled into every project that has
  a frontend so Claude Code and Codex (which cannot access claude.ai skill paths) can read it.
  Generation strategy — try in order until one succeeds:
  1. If the `frontend-design` skill is already active in this claude.ai session, read its
     full content and write it verbatim to `docs/frontend-design.md`.
  2. If a local copy exists on the machine (common paths: `~/.agents/skills/frontend-design/SKILL.md`,
     `C:\Users\<user>\.agents\skills\frontend-design\SKILL.md`, `/mnt/skills/public/frontend-design/SKILL.md`),
     read it and write it verbatim.
  3. If neither source is reachable, generate a minimal fallback containing: brand color
     palette, typography scale (font families + size steps), 4-point spacing system,
     component naming conventions, and the "no generic AI aesthetics" principle.
  Log which strategy was used as a note in `docs/learnings.md`.

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
