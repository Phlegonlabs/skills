## Engineering Layer

Keep the workflow above as the source of truth, and use a machine-readable contract layer to make it testable.

### Contract Files

- `assets/workflow-map.v1.json` — Mode detection, tier defaults, init/update/convert phase order, type/profile ranges, output doc list
- `assets/interview-question-pack.v1.json` — Init/update/convert interview round registry and round-level constraints
- `assets/quality-gates.v1.json` — Required references, required SKILL sections, and release gate checklist
- `assets/doc-build-map.v1.json` — Source module directories, assembly order files, and generated doc targets

These files **must not change the workflow semantics**. Their purpose is enforcement and consistency checks.

### Source Of Truth

- `sources/*` is the canonical editable source for generated docs.
- `SKILL.md` and `references/*.md` in this skill are generated artifacts from `sources/*`.
- Do not hand-edit generated artifacts. Edit source partials first, then run docs build.

### Script Entry Points

- `scripts/verify-skill.ts` — Runs contract validation and fails fast on drift
- `scripts/skill-contract.ts` — Shared loaders + validators used by scripts and tests
- `scripts/build-docs.ts` — Assembles source partials into generated docs (write/check modes)
- `scripts/build-docs.sh` — Shell wrapper for `scripts/build-docs.ts`

### Quality Gates

Before publishing changes to this skill, run:

1. `bun run contract:check`
2. `bun run typecheck`
3. `bun run test`

If any check fails, fix the issue before considering the skill update complete.

Doc assembly commands:
- `bun run docs:build` — Regenerate `SKILL.md` + `references/*.md` from `sources/*`
- `bun run docs:check` — Check source/artifact drift without writing
