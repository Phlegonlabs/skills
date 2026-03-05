## File: `docs/secrets.md`

Guidance for handling secrets and API keys (both integration keys and user-issued keys).

Structure:
```markdown
# Secrets & API Keys

## Principles
- Never commit secrets (API keys, tokens, private keys) to git
- Prefer environment variables for local dev and a secrets manager in production
- Redact secrets from logs, errors, and any user-facing output by default

## Local Development Setup
- Copy `.env.example` → `.env`
- Fill in required keys/IDs (never paste real secrets into docs)
- Never commit `.env`

## Integration Keys (3rd-party services)
- Store secrets in server-side env vars only (never ship secrets in client bundles)
- Validate required env vars at startup and fail fast with an actionable error (do not print secret values)
- Decide rotation strategy (how to rotate without downtime) and document it

## If This Product Issues API Keys to Users (optional)
- Generate high-entropy keys with a prefix (e.g., `sk_live_...`)
- Store only a hash (plus metadata); never store plaintext keys
- Show the full key only once at creation; afterwards show masked + last 4
- Support revoke/rotate; add audit logging, scopes/permissions, and rate limits

## Secret Scanning (recommended)
- Consider adding a pre-commit hook (e.g., `detect-secrets`, `git-secrets`, or GitHub secret scanning)
  to catch accidental secret commits before they reach the remote

## Output/Display Guidance
- Never print full keys by default (CLI/UI)
- If showing a key is required, make it explicit (e.g., "Reveal" / `--show-key`) and warn the user
- Ensure keys never appear in URLs, crash reports, or analytics events
```
