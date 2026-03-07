# Deploy Route

## release_gate
- Confirm an approved plan exists and the deployment document is up to date.
- Do not deploy production before preview validation passes.

## provider_route
- Default to Cloudflare when the repo uses Cloudflare Pages, Workers, or a stack-equivalent runtime.
- Record runtime details in `harnass-os/documents/runtime/<provider>.yaml`.
- Record the provider, surface, and commands in `harnass-os/documents/deploy/current.yaml`.
- Prefer concrete project commands over placeholders whenever discovery can identify them.

## preview_deploy
- Build the artifact using the recorded build command.
- Deploy to a preview environment using the recorded preview deploy command.

## preview_validation
- Run smoke and browser checks against the preview URL.
- Record preview acceptance and promotion readiness in `harnass-os/documents/release/current.yaml`.

## production_deploy
- Deploy or promote only after preview validation is green, using the recorded production deploy command.
- Record the production URL, revision, and timestamp in deploy and release docs.
- Move `harnass-os/documents/release/current.yaml` to `awaiting-final-audit` after production deploy when post-deploy audit is required.

## rollback_route
- Keep the previous stable revision and rollback command ready before production deploy.

## post_deploy_observability
- Check logs, metrics, and key user flows immediately after release.

## final_audit_handoff
- Hand off to `harnass-os/Audit.md` after production deploy.
- Do not mark the release complete inside Deploy.md; completion happens only after final audit passes.

