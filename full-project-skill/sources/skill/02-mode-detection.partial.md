## Mode Detection

At the start, detect which mode to use:

1. Check if `docs/architecture.md` and `docs/plans.md` already exist in the project
2. If **both exist** → **Update mode** (the project was previously initialized with this skill)
3. If **neither exists**, scan for existing codebase signals:
   - code roots: `src/`, `app/`, `apps/*/src`, `apps/*/app`, `packages/*/src`, `packages/*/app`, `services/*/src`
   - project manifests/configs: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`
4. If docs are missing **and** codebase signals exist → **Convert/Upgrade mode** (bootstrap this existing codebase
   into the structured docs + hooks/HK workflow)
5. If docs are missing and no codebase signals exist → **Init mode** (new project)
6. If **only one** required doc exists → Potentially partial/corrupted state. Inform the user which file is missing
   and ask whether to:
   - convert/upgrade from current code reality (recommended)
   - attempt update with incomplete docs
   - init from scratch (overwrite docs)
7. If ambiguous for other reasons, ask the user whether they are modifying the existing project, converting an
   existing codebase, or starting fresh
