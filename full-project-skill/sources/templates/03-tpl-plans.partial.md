## File: `docs/plans.md`

The execution plan — a living document updated as milestones are completed.

Structure:
```markdown
# {Project Name} Implementation Plan

## Project Metadata
- **Project**: {Project Name}
- **Platform**: {Web app / Desktop app / Mobile app / CLI / Hybrid}
- **Tech stack**: {runtime, framework, styling, database}
- **UI framework**: {e.g., shadcn/ui, Radix, Ant Design} (GUI projects only)
- **Deployment**: {e.g., Vercel, Cloudflare Pages, Electron installer}
- **Analytics**: {none / GA4 / GTM / other} (Web projects only)
- **Created**: {date}
- **Status**: In Progress

## Guiding Principles
- {2-3 principles derived from the project's nature}

## Verification Checklist (kept current)
- [ ] `{pm} run lint`
- [ ] `{pm} run typecheck`
- [ ] `{pm} run test`
- Last verified: not started

## Milestones

### Milestone 01 - Repo scaffold + tooling [ ]
Scope:
- Initialize {tech stack}
- Add testing, linting, type checking tooling
- Establish folder structure

Sub-tasks:
- 1.1 — {Atomic action, e.g., "Initialize project with {pm} init"}
- 1.2 — {e.g., "Install and configure linter (ESLint)"}
- 1.3 — {e.g., "Install and configure formatter (Prettier)"}
- 1.4 — {e.g., "Set up TypeScript config (tsconfig.json)"}
- 1.5 — {e.g., "Create folder structure per architecture.md"}
- 1.6 — {e.g., "Add test framework and verify with a smoke test"}
- 1.7 — {e.g., "Add dev/build/test/lint/typecheck scripts to package.json"}

Key files/modules:
- {list key files}

Acceptance criteria:
- {list criteria}

Trade-offs considered:
- {Alternative approach vs chosen approach: why chosen approach wins}
- {Constraint that ruled out a simpler path}
{Omit if no meaningful trade-offs for this milestone.}

Verification:
- {commands to run}

### Milestone 02 - {Next logical step} [ ]
...

{Generate milestone count based on the complexity tier assigned during Phase 1:
- Standard tier: 7-10 milestones
- Complex tier: 10-14 milestones
Each feature should map to 1-3 milestones depending on complexity.
Always start with scaffold and end with the **Production Readiness Gate** (Milestone PR, see below).
For web apps: if analytics/tracking is in scope (GA4/GTM), include an Analytics milestone (after core navigation/auth is stable, before Production Readiness Gate).
For CLI tools: place CLI Foundation (CC) as Milestone 02, right after repo scaffold.
The second-to-last milestone should be polish/verification. The LAST milestone is ALWAYS the Production Readiness Gate.}

{Sub-task generation rules:
- Every milestone MUST have a "Sub-tasks" section with numbered items (no checkboxes)
- Each sub-task is ONE atomic action that can be completed and verified independently
- Use format: "- N.M — {verb phrase describing a single action}"
- Target 3-8 sub-tasks per milestone depending on milestone scope
- Sub-tasks should follow a logical implementation order within the milestone
- Each sub-task should be small enough to complete in a single focused session
- For milestones with non-obvious implementation choices, document trade-offs considered.
- Common sub-task patterns per milestone type:
  - UI feature: create component → add styling → wire up state → handle edge states → add tests
  - API/data: define schema/types → implement data layer → add validation → add error handling → add tests
  - Integration: set up client/SDK → implement core integration → add error handling → add tests
  - Polish: audit UX flows → fix edge cases → optimize performance → final verification
 - Track sub-task execution progress in `tasks/todo.md` (Current Sprint / Completed)
 - After all sub-tasks for a milestone are complete in `tasks/todo.md`, mark the milestone itself as complete in `docs/plans.md`}

### Milestone CC - CLI Foundation [ ] (CLI projects only)
Set up the CLI entry point, argument parsing, help system, and output formatting infrastructure.

Scope:
- Set up CLI entry point with argument parser (e.g., `commander`, `yargs`, `citty`)
- Implement all subcommands as stubs with `--help` text and usage examples
- Implement global flags: `--help`, `--version`, `--verbose`, `--quiet`, `--json`, `--no-color`
- Set up output formatting layer (human-readable default, JSON with `--json`)
- Set up error handling: stderr for errors, correct exit codes (0/1/2)
- Respect `NO_COLOR` env var
- Detect piped stdin for non-interactive mode
- Set up config file loading if applicable (discovery, parsing, validation)
- Add graceful shutdown handler (SIGINT/SIGTERM)

Key files/modules:
- CLI entry point (e.g., `src/cli.ts` or `src/index.ts`)
- Command definitions (e.g., `src/commands/`)
- Output formatter (e.g., `src/utils/output.ts`)
- Config loader (e.g., `src/config.ts`)
- `bin` field in package.json

Acceptance criteria:
- `mytool --help` shows all commands with descriptions
- `mytool <cmd> --help` shows command-specific usage with examples
- `mytool --version` outputs version from package.json
- `mytool --json <cmd>` outputs valid JSON
- `NO_COLOR=1 mytool <cmd>` produces uncolored output
- Invalid command/args exits with code 2 and helpful error message to stderr
- Config file is loaded from expected location (if applicable)

Verification:
- `{pm} run build && ./dist/mytool --help` — verify help output
- `{pm} run build && ./dist/mytool --version` — verify version
- `{pm} run build && ./dist/mytool invalid-cmd 2>&1; echo $?` — verify exit code 2
- `NO_COLOR=1 {pm} run build && ./dist/mytool --help` — verify no ANSI codes

### Milestone WA - Web Analytics / Tracking [ ] (Web projects only, if analytics is in scope)
Instrument analytics (e.g., GA4/GTM) with consent and a typed event layer.

Scope:
- Decide analytics provider (GA4 via gtag, GTM, or other) and consent requirements
- Create a single analytics adapter module (avoid scattered direct SDK calls)
- Instrument page views + 3-10 key events derived from the user journeys
- Ensure analytics is disabled in dev/test by default (env-gated)
- Add tests for event payload building (and enforce "no PII" in analytics payloads)

Key files/modules:
- Analytics adapter (e.g., `src/analytics/`)
- Event schema/types (e.g., `src/analytics/events.ts`)
- Consent handling (if applicable)

Acceptance criteria:
- Analytics can be toggled via env/config (off in dev/test by default)
- Page view + key events are emitted through the adapter
- Consent requirements are respected (if applicable)
- No PII is sent in analytics payloads (explicitly documented)

Verification:
- `{pm} run test` — tests cover event payload builder
- `{pm} run build` — production build includes analytics only when enabled

### Milestone PR - Production Readiness Gate [ ] (MANDATORY — always the final milestone)
Verify the entire project is production-ready, not just functional. This milestone is the final
quality gate before the project can be considered complete.

Scope:
- Full audit of all code for production quality
- Verify no demo/prototype artifacts remain
- Confirm all features work end-to-end with real (non-mock) data paths
- Security, performance, and error handling review

Sub-tasks:
- PR.1 — Run full verification suite (`{pm} run lint`, `{pm} run typecheck`, `{pm} run test`) — zero failures
- PR.2 — Audit for hardcoded values: no hardcoded URLs, ports, API keys, user IDs, or env-specific values in source code
- PR.3 — Audit for prototype leftovers: no `// TODO`, no `console.log` debugging, no commented-out code blocks, no `any` types, no `@ts-ignore` without justification
- PR.4 — Audit for mock/placeholder data: no mock data in production code paths (only allowed in test files and dev seed scripts)
- PR.5 — Verify error handling: every async operation has error handling, every user-facing error has a meaningful message, no empty catch blocks
- PR.6 — Verify `{pm} run build` produces a clean production build with no warnings
- PR.7 — Verify `{pm} run dev` starts cleanly and all features work end-to-end
- PR.8 — Verify all environment variables are documented in `.env.example` and validated at startup
- PR.9 — Review file sizes: flag any source file over 500 lines and verify it's justified
- PR.10 — Final documentation sync: ensure `docs/documentation.md` accurately reflects the implemented state (setup, commands, structure, troubleshooting)
- PR.11 — Dependency security audit: run `{pm} audit` (or equivalent) and remediate high/critical vulnerabilities
- PR.12 — (Web/GUI projects) Accessibility check: verify keyboard navigation, ARIA labels on interactive elements, sufficient color contrast
- PR.13 — License audit: verify all production dependencies use permissive licenses (MIT/Apache/BSD) compatible with this project's distribution model

Key files/modules:
- All source files
- `.env.example`
- `docs/documentation.md`
- `package.json` (scripts section)

Acceptance criteria:
- All verification commands pass with zero errors and zero warnings
- No hardcoded secrets, URLs, ports, or environment-specific values in source code
- No TODO comments, console.log debugging, or commented-out code blocks
- No mock/placeholder data in production code paths
- Every async operation has proper error handling
- Production build succeeds cleanly
- Dev server starts and all features are functional end-to-end
- `.env.example` is complete and all env vars are validated at startup
- `docs/documentation.md` is accurate and up-to-date
- The project is ready to deploy — not a demo, not a prototype

Verification:
- `{pm} run lint` — zero errors
- `{pm} run typecheck` — zero errors
- `{pm} run test` — all tests pass
- `{pm} run build` — clean build, no warnings
- `{pm} run dev` — starts cleanly, manual smoke test of all features

## Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| {risk} | {impact} | {mitigation} |

## Implementation Notes & Lessons Learned
{Empty section — dual purpose:}
{1. Record bug fixes, workarounds, and unexpected discoveries during implementation}
{2. Capture lessons learned that should inform future work (also add to CLAUDE.md "Lessons & Prevention Rules")}
```
