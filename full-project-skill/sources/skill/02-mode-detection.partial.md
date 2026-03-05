## Mode Detection

At the start, detect which mode to use:

1. Check if `docs/architecture.md` and `docs/plans.md` already exist in the project
2. If **both exist** → **Update mode** (the project was previously initialized with this skill)
3. If **neither exists** → **Init mode** (new project)
4. If **only one exists** → Potentially corrupted state. Inform the user which file is missing and ask:
   init from scratch (overwrite), or attempt update with incomplete docs?
5. If ambiguous for other reasons, ask the user whether they are modifying the existing project or starting fresh
