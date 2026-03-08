# Deploy Route

> **AGENT STOP — do NOT auto-deploy.**
> Deploy is always manual. The agent prepares deploy documents and then stops.
> The user confirms secrets, fills `.env`, and runs deploy commands themselves.

---

## secrets_gate — REQUIRED before any deploy command is run

The agent MUST stop after implementation and present this checklist to the user.
Do not proceed to any deploy command until the user explicitly confirms all items.

**Checklist for the user:**
- [ ] Copy `.env.example` to `.env` in the project root
- [ ] Fill every `<fill>` value in `.env` with real secrets / API keys
- [ ] Confirm environment-specific values are correct (APP_URL, DATABASE_URL, etc.)
- [ ] Set `secrets_gate.env_file_confirmed: true` in `harnass-os/documents/deploy/current.yaml`
- [ ] Set `secrets_gate.secrets_confirmed: true` and `secrets_gate.status: confirmed`

**Agent action:** Present the checklist above, then stop and wait. Do not run any
build or deploy commands until the user signals that secrets are confirmed.

---

## release_gate
- Confirm an approved plan exists and the deployment document is up to date.
- `secrets_gate.secrets_confirmed` must be `true` before proceeding.
- Do not deploy production before preview validation passes.

## provider_route
- Default to Cloudflare when the repo uses Cloudflare Pages, Workers, or a stack-equivalent runtime.
- Record runtime details in `harnass-os/documents/runtime/<provider>.yaml`.
- Record the provider, surface, and commands in `harnass-os/documents/deploy/current.yaml`.
- Prefer concrete project commands over placeholders whenever discovery can identify them.

## preview_deploy
- **User runs this manually** after secrets are confirmed.
- Build command: from `harnass-os/documents/deploy/current.yaml` → `build_command`
- Deploy command: from `harnass-os/documents/deploy/current.yaml` → `preview_deploy_command`

## preview_validation
- Run smoke and browser checks against the preview URL.
- Record preview acceptance and promotion readiness in `harnass-os/documents/release/current.yaml`.

## production_deploy
- **User runs this manually** after preview validation is green.
- Deploy command: from `harnass-os/documents/deploy/current.yaml` → `production_deploy_command`
- Record the production URL, revision, and timestamp in deploy and release docs.
- Move `harnass-os/documents/release/current.yaml` to `awaiting-final-audit` after production deploy when post-deploy audit is required.

## rollback_route
- Keep the previous stable revision and rollback command ready before production deploy.

## post_deploy_observability
- Check logs, metrics, and key user flows immediately after release.

## final_audit_handoff
- Hand off to `harnass-os/Audit.md` after production deploy.
- Do not mark the release complete inside Deploy.md; completion happens only after final audit passes.
