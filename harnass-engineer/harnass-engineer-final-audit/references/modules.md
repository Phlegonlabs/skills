# Final Audit Modules

## Adaptive Selection

Select modules from repo shape, deployed surface, app type, and detected stack.
Always record skipped modules explicitly.
Every applicable module should carry `evidence_refs` that point to validation history, deploy docs, runtime docs, or browser-session artifacts.

## Module Catalog

### frontend-experience
- Use for UI-facing projects.
- Smoke first: homepage, primary route, main CTA, and one real data request.
- Deep audit: console errors, network failures, loading/empty/error states, and critical flows.

### frontend-quality
- Use for UI codebases.
- Run lint, typecheck, build, route reachability, and responsive sanity checks.

### accessibility
- Use for public or user-facing interfaces.
- Check semantics, headings, forms, keyboard reachability, focus, contrast, and alt text.

### backend-runtime
- Use when services, workers, or APIs exist.
- Smoke first: boot, health route, and key entrypoint.
- Deep audit: runtime wiring, env vars, provider bindings, and critical startup failure paths.

### api-contract
- Use when the repo exposes APIs or workers.
- Smoke first: minimal success and error-path requests.
- Deep audit: response shape, status codes, auth gates, and error semantics.

### frontend-backend-integration
- Use when UI depends on backend data.
- Smoke first: one real end-to-end user path.
- Deep audit: field mapping, error fallback, cache/loading behavior, and data freshness assumptions.
- Prefer replaying flows listed in `harnass-os/documents/inventory/current-state.yaml testing.integration_flows`.

### security
- Use for every networked or public release.
- Check secret exposure, unsafe debug flags, auth gaps, dangerous CORS, obvious XSS/CSRF, and public env leakage.

### content-quality
- Use for public pages, product UI, or marketing content.
- Smoke first: page content skeleton is present.
- Deep audit: placeholder copy, broken hierarchy, missing CTAs, empty states, and factual inconsistency.

### content-safety
- Use when the release contains user-visible text, AI-generated copy, or policy-sensitive messaging.
- Check misleading claims, harmful content, sensitive leakage, brand mismatch, and unsafe instructions.

### seo
- Use for public web surfaces.
- Smoke first: homepage and primary public pages expose title and metadata.
- Deep audit: title, description, canonical, robots, sitemap, Open Graph, headings, and crawlability.

### performance-observability
- Use for release-affecting work.
- Smoke first: key page and key endpoint latency plus log scan.
- Deep audit: production errors, tracing/logging presence, and rollback confidence.

### deploy-runtime-consistency
- Use for all production deploys.
- Smoke first: production URL, health route, and recorded smoke command refs.
- Deep audit: release docs, deploy docs, runtime docs, revision, domain, and rollback alignment.

### ci-cd-release-hygiene
- Use for all release-affecting work.
- Audit build/test/deploy commands, CI assumptions, release state, and doc pointers.

### documentation-signoff
- Use for every final audit.
- Check plan, status, handoffs, release, deploy, and audit docs for consistency.

### blockchain-contract-audit
- Enable only when blockchain tooling is detected from repo reality.
- Smoke first:
  - EVM: prefer `forge test`, `npx hardhat test`, or an equivalent local simulation command.
  - Anchor/Solana: prefer `anchor test` or the repo's own simulation flow.
  - If no runnable contract command exists, record a blocking manual gap.
- Deep audit:
  - verify contract logic matches product behavior
  - inspect auth, ownership, pausing, upgrades, settlement, and fund movement
  - inspect reentrancy, arithmetic edge cases, init flow, state machine correctness, oracle dependence, and signature validation
  - verify frontend transaction shaping matches contract expectations
