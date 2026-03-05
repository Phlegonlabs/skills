## File: `docs/documentation.md`

User-facing documentation — a living document kept in sync with reality.

Structure:
```markdown
# {Project Name} Documentation

## What {Project Name} Is
- {1-2 sentence description}

## Status
- Milestone 01: pending
- Milestone 02: pending
...

## Local Setup
- Prerequisites: {runtime version}
- Install: `{pm} install`
- Start: `{pm} run dev`

## Environment Variables / API Keys
- Use `.env.example` as the template for required env vars (API keys/IDs)
- Create `.env` locally and fill values; never commit `.env`
- Production: set env vars in your hosting provider / secrets manager

## Verification Commands
- Lint: `{pm} run lint`
- Typecheck: `{pm} run typecheck`
- Tests: `{pm} run test`
- Build: `{pm} run build`

## Repo Structure Overview
_To be updated as implementation progresses._

## Troubleshooting
_To be updated as issues are discovered._
```
