# Project Config Templates

Ready-to-use configs for all supported stacks. Copy and adapt to the project.

---

## TypeScript — tsconfig.json

### Base (strict, all projects)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"],
  "exclude": ["node_modules", "dist", "build"]
}
```

### Next.js additions

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "esModuleInterop": true,
    "allowJs": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Node.js API

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

**Rules:**
- `strict: true` is non-negotiable — never set to false
- `noUncheckedIndexedAccess: true` catches index access bugs at compile time
- Always configure `paths` with `@/*` alias for clean imports
- `verbatimModuleSyntax` enforces `import type` (pairs with ESLint rule)

---

## Prettier — .prettierrc

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf",
  "plugins": []
}
```

### .prettierignore

```
dist/
build/
.next/
out/
node_modules/
pnpm-lock.yaml
bun.lockb
package-lock.json
coverage/
*.min.js
```

**Rules:**
- Single quotes, semicolons, trailing commas — consistent across all projects
- `printWidth: 100` — wider than default 80, reduces unnecessary wrapping
- Add framework-specific plugins as needed (e.g., `prettier-plugin-tailwindcss`)

---

## Vitest — vitest.config.ts

### Base

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.ts', 'tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.*',
        '**/*.d.ts',
        'src/lib/env.ts',
      ],
    },
    setupFiles: [],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### React / Next.js (with jsdom)

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx', 'tests/**/*.test.ts'],
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '.next/',
        '**/*.config.*',
        '**/*.d.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### tests/setup.ts (for React)

```typescript
import '@testing-library/jest-dom/vitest';
```

**Dependencies:**
```json
{
  "vitest": "^3.0.0",
  "@vitest/coverage-v8": "^3.0.0",
  "@testing-library/react": "^16.0.0",
  "@testing-library/jest-dom": "^6.0.0",
  "@testing-library/user-event": "^14.0.0",
  "jsdom": "^25.0.0"
}
```

---

## Docker

### Dockerfile (Node.js multi-stage)

```dockerfile
# === Build stage ===
FROM node:22-alpine AS builder
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build

# === Production stage ===
FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 appgroup \
 && adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

USER appuser
EXPOSE 3000
ENV NODE_ENV=production

CMD ["node", "dist/index.js"]
```

Adapt: replace `pnpm` commands with `bun` or `npm` based on chosen package manager.
Replace `node:22-alpine` with `oven/bun:1-alpine` for Bun projects.

### docker-compose.yml (with PostgreSQL)

```yaml
services:
  app:
    build: .
    ports:
      - '3000:3000'
    env_file: .env
    volumes:
      - ./src:/app/src
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-appdb}
    ports:
      - '5432:5432'
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U postgres']
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  db_data:
```

Swap `postgres:16-alpine` for the chosen DB image (MongoDB, MySQL, etc.).

---

## CI — GitHub Actions

### ci.yml

```yaml
name: CI
on:
  pull_request:
    branches: [main, 'milestone/*']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - run: pnpm install --frozen-lockfile
      - run: pnpm run validate

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - run: pnpm audit --audit-level=high
```

### deploy.yml

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - run: pnpm install --frozen-lockfile
      - run: pnpm run validate
      - run: pnpm run build

      # ── Deploy — uncomment ONE section matching your target ──────────

      # Vercel (managed — usually auto-deploys on push, use this for manual control):
      # - uses: amondnet/vercel-action@v25
      #   with:
      #     vercel-token: ${{ secrets.VERCEL_TOKEN }}
      #     vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
      #     vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
      #     vercel-args: '--prod'

      # Cloudflare Pages:
      # - uses: cloudflare/wrangler-action@v3
      #   with:
      #     apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      #     accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      #     command: pages deploy ./out --project-name=<project-name>

      # Cloudflare Workers:
      # - uses: cloudflare/wrangler-action@v3
      #   with:
      #     apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      #     command: deploy

      # Fly.io:
      # - uses: superfly/flyctl-actions/setup-flyctl@master
      # - run: flyctl deploy --remote-only
      #   env:
      #     FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      # Railway (auto-deploys on push — CI just validates):
      # Railway connects directly to your repo. No deploy step needed here.
      # Just ensure validate passes. Railway triggers on push to main.

      # Render (auto-deploys on push — CI just validates):
      # Render connects directly to your repo. No deploy step needed here.
      # Or use deploy hook:
      # - run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}

      # VPS via SSH + Docker Compose:
      # - uses: appleboy/ssh-action@v1
      #   with:
      #     host: ${{ secrets.VPS_HOST }}
      #     username: ${{ secrets.VPS_USER }}
      #     key: ${{ secrets.VPS_SSH_KEY }}
      #     script: |
      #       cd /opt/<project-name>
      #       git pull origin main
      #       docker compose pull
      #       docker compose up -d --remove-orphans

      # VPS via Kamal (zero-downtime Docker deploy):
      # - uses: ruby/setup-ruby@v1
      #   with:
      #     ruby-version: '3.3'
      # - run: gem install kamal
      # - run: kamal deploy
      #   env:
      #     KAMAL_REGISTRY_PASSWORD: ${{ secrets.KAMAL_REGISTRY_PASSWORD }}

      # AWS ECS (Docker → ECR → ECS):
      # - uses: aws-actions/configure-aws-credentials@v4
      #   with:
      #     aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      #     aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      #     aws-region: us-east-1
      # - uses: aws-actions/amazon-ecr-login@v2
      # - run: |
      #     docker build -t $ECR_REGISTRY/<project-name>:${{ github.sha }} .
      #     docker push $ECR_REGISTRY/<project-name>:${{ github.sha }}
      # - run: |
      #     aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment

      # Google Cloud Run:
      # - uses: google-github-actions/auth@v2
      #   with:
      #     credentials_json: ${{ secrets.GCP_SA_KEY }}
      # - uses: google-github-actions/deploy-cloudrun@v2
      #   with:
      #     service: <service-name>
      #     region: us-central1
      #     source: .

      # Netlify:
      # - uses: nwtgck/actions-netlify@v3
      #   with:
      #     publish-dir: './out'
      #     production-deploy: true
      #   env:
      #     NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
      #     NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

**Adapt:** replace `pnpm` with `bun` or `npm`. For Bun, use `oven-sh/setup-bun@v2`.
For npm, remove the pnpm setup step — Node.js includes npm.

### Platform config files

Generate the appropriate config file based on the chosen deploy target:

```
# Vercel — vercel.json (optional, Vercel auto-detects most frameworks)
{
  "framework": "nextjs",
  "buildCommand": "pnpm run build",
  "outputDirectory": ".next"
}

# Cloudflare Pages — wrangler.toml
name = "<project-name>"
compatibility_date = "2025-01-01"
pages_build_output_dir = "./out"

# Cloudflare Workers — wrangler.toml
name = "<project-name>"
main = "src/index.ts"
compatibility_date = "2025-01-01"

# Fly.io — fly.toml
app = "<project-name>"
primary_region = "iad"
[build]
  dockerfile = "Dockerfile"
[http_service]
  internal_port = 3000
  force_https = true

# Railway — railway.toml (optional)
[build]
  builder = "dockerfile"
[deploy]
  healthcheckPath = "/health"
  restartPolicyType = "ON_FAILURE"

# Kamal (VPS) — config/deploy.yml
service: <project-name>
image: <registry>/<project-name>
servers:
  web:
    - <vps-ip>
registry:
  server: ghcr.io
  username: <github-username>
  password:
    - KAMAL_REGISTRY_PASSWORD

# Docker Compose (VPS self-hosted) — docker-compose.yml already generated in scaffold
# Coolify / Dokku — connect repo via their web UI, no config file needed
```

Only generate the config file for the platform the user chose. Don't include configs
for platforms they didn't select.

---

---

## GitLab CI (alternative to GitHub Actions)

Generate these if user selects `GitLab CI` in Step 4. Place at project root as `.gitlab-ci.yml`.

### .gitlab-ci.yml

```yaml
stages:
  - validate
  - deploy

variables:
  NODE_VERSION: "22"

# ── CI: runs on every merge request ──────────────────────────────────────────
validate:
  stage: validate
  image: node:${NODE_VERSION}-alpine
  before_script:
    - corepack enable
    - pnpm install --frozen-lockfile
  script:
    - pnpm run harness validate
    - pnpm run harness file-guard
    - pnpm run harness schema
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

# ── Deploy: runs on push to main ─────────────────────────────────────────────
deploy:
  stage: deploy
  image: node:${NODE_VERSION}-alpine
  before_script:
    - corepack enable
    - pnpm install --frozen-lockfile
  script:
    - pnpm run harness validate:full
    - pnpm run build

    # Uncomment ONE deploy target:

    # Vercel:
    # - npx vercel --prod --token $VERCEL_TOKEN

    # Fly.io:
    # - curl -L https://fly.io/install.sh | sh
    # - flyctl deploy --remote-only

    # VPS via SSH + Docker Compose:
    # - apt-get update && apt-get install -y openssh-client
    # - ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "cd /opt/$CI_PROJECT_NAME && git pull && docker compose up -d --remove-orphans"

    # Docker registry push (for container platforms):
    # - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    # - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  environment:
    name: production
```

**Adapt:** replace `pnpm` with `bun` or `npm`. For Bun, use `oven-sh/setup-bun` or
`bun install` directly. Variables like `$VERCEL_TOKEN`, `$VPS_HOST` etc. are set in
GitLab CI/CD settings → Variables.

---

## Python equivalents

### pyproject.toml (ruff + mypy + pytest)

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
select = [
  "E",   # pycodestyle errors
  "W",   # pycodestyle warnings
  "F",   # pyflakes
  "I",   # isort
  "N",   # pep8-naming
  "UP",  # pyupgrade
  "B",   # flake8-bugbear
  "SIM", # flake8-simplify
  "T20", # flake8-print (ban print statements)
  "RUF", # ruff-specific
]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
```

### Makefile (Python)

```makefile
.PHONY: lint lint-fix type-check test validate

lint:
	ruff check .

lint-fix:
	ruff check --fix .
	ruff format .

type-check:
	mypy src/

test:
	pytest

validate: lint type-check test
```

---

## Go equivalents

### golangci-lint (.golangci.yml)

```yaml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - misspell
    - unconvert
    - gocritic
    - revive

linters-settings:
  revive:
    rules:
      - name: exported
        severity: warning
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
```

### Makefile (Go)

```makefile
.PHONY: lint lint-fix type-check test validate build

lint:
	golangci-lint run ./...

lint-fix:
	golangci-lint run --fix ./...
	goimports -w .

type-check:
	go vet ./...

test:
	go test -v -race ./...

test-integration:
	go test -v -race -tags=integration ./...

validate: lint type-check test

build:
	go build -o bin/<app-name> ./cmd/<app-name>/
```

---

## Rust equivalents

### clippy.toml

```toml
too-many-arguments-threshold = 5
cognitive-complexity-threshold = 15
```

### Cargo.toml (lint section)

```toml
[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
all = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
nursery = { level = "warn", priority = -1 }
unwrap_used = "warn"
expect_used = "warn"
```

### Makefile (Rust)

```makefile
.PHONY: lint lint-fix type-check test validate build

lint:
	cargo clippy -- -D warnings

lint-fix:
	cargo clippy --fix --allow-dirty
	cargo fmt

type-check:
	cargo check

test:
	cargo test

validate: lint type-check test

build:
	cargo build --release
```

---

## Docker variants by project type

### Node.js Web App / API (default)

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Node.js CLI Tool (for Docker distribution)

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
ENTRYPOINT ["node", "dist/index.js"]
```

### Python (API or CLI)

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY . .

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
# For API:
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
# For CLI:
# ENTRYPOINT ["python", "-m", "src.cli"]
```

### Go (API or CLI)

```dockerfile
FROM golang:1.22-alpine AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/app ./cmd/<app-name>/

FROM alpine:3.19
COPY --from=build /bin/app /bin/app
# For API:
# EXPOSE 3000
# CMD ["/bin/app"]
# For CLI:
# ENTRYPOINT ["/bin/app"]
```

### Rust (API or CLI)

```dockerfile
FROM rust:1.77-alpine AS build
WORKDIR /app
RUN apk add musl-dev
COPY Cargo.toml Cargo.lock ./
COPY src/ src/
RUN cargo build --release

FROM alpine:3.19
COPY --from=build /app/target/release/<app-name> /bin/app
# ENTRYPOINT ["/bin/app"]
```

**Rules:**
- Only generate Docker if the project needs it (web apps, self-hosted agents, Docker distribution)
- Skip Docker for CLI tools distributed via npm/pip/homebrew (unless user requests it)
- Always multi-stage build (build stage + minimal production stage)
- Never install dev dependencies in production stage

---

## Assembly Rules

1. Read this file BEFORE generating any config — never write configs from memory
2. Always use the strictest settings (strict: true, strictTypeChecked, etc.)
3. Adapt path aliases, ignores, and plugins to the specific project
4. Package manager commands must match the user's choice (pnpm/bun/npm)
5. Docker base images should match the chosen runtime version
6. CI workflows must match the chosen package manager setup action
7. Never downgrade strictness. If a rule causes errors, fix the code, not the config.

---

## Claude Code — .claude/settings.json

```json
{
  "plansDirectory": "./docs/exec-plans/active",
  "permissions": {
    "allowedTools": [
      "Read", "Write",
      "Bash(git *)",
      "Bash(<package-manager> *)",
      "Bash(npx tsx scripts/harness.ts *)",
      "Bash(npx tsx scripts/check-commit-msg.ts *)",
      "Bash(npx lint-staged)",
      "Bash(npx prisma *)",
      "Bash(npx drizzle-kit *)"
    ],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

**Critical:** replace `<package-manager>` with the chosen one (`pnpm`, `bun`, or `npm`).

This config enables **autonomous execution**:
- Routes plan mode output to `docs/exec-plans/active/` (inside repo, versioned)
- Pre-approves ALL harness CLI commands (no "allow?" prompts during task loop)
- Pre-approves git and package manager commands
- Blocks reading .env files (Iron Rule 6: secrets never touch agent context)

## Codex — .codex/config.toml

```toml
# Codex project-level configuration
approval_policy = "never"
# This allows Codex to run harness commands, git, and package manager without prompts.
# For supervised mode: approval_policy = "on-request"

[sandbox]
sandbox_mode = "workspace-write"

[project_doc]
project_doc_max_bytes = 65536
```

**Key difference from Claude Code:**
- Codex does NOT have a native `plansDirectory` config
- AGENTS.md contains the instruction to write plans to `docs/exec-plans/active/`
- Codex sandbox allows workspace writes by default

**Plan file flow (both agents):**

```
Plan mode → plan file lands in docs/exec-plans/active/
  ↓
Session Init → detects new plan file
  ↓
Sync → parse plan → add to PRD + PLAN.md + progress.json
  ↓
Task Execution Loop → runs the new milestone
  ↓
Milestone complete → move plan to docs/exec-plans/completed/
```

