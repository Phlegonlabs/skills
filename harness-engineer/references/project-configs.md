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

      # Deploy — adapt to target platform:
      # Vercel:
      # - uses: amondnet/vercel-action@v25
      #   with:
      #     vercel-token: ${{ secrets.VERCEL_TOKEN }}
      #     vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
      #     vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
      #     vercel-args: '--prod'
      #
      # Fly.io:
      # - uses: superfly/flyctl-actions/setup-flyctl@master
      # - run: flyctl deploy --remote-only
      #   env:
      #     FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Adapt:** replace `pnpm` with `bun` or `npm`. For Bun, use `oven-sh/setup-bun@v2`.
For npm, remove the pnpm setup step — Node.js includes npm.

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
    "allowedTools": ["Read", "Write", "Bash(git *)", "Bash(<package-manager> *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

**Critical:** replace `<package-manager>` with the chosen one (`pnpm`, `bun`, or `npm`).

This config:
- Routes plan mode output to `docs/exec-plans/active/` (inside repo, versioned)
- Pre-approves git and package manager commands (reduces approval prompts)
- Blocks reading .env files (Iron Rule 6: secrets never touch agent context)

## Codex — .codex/config.toml

```toml
# Codex project-level configuration
# Codex reads AGENTS.md automatically from the project root.

approval_policy = "on-request"

[project_doc]
project_doc_max_bytes = 65536
# Ensure AGENTS.md is fully loaded (default is 32KB, increase for larger projects)
```

**Key difference from Claude Code:**
- Codex does NOT have a native `plansDirectory` config
- Instead, AGENTS.md contains an explicit instruction:
  "When creating a plan, write it to `docs/exec-plans/active/<YYYY-MM-DD-description>.md`"
- Codex follows AGENTS.md instructions, so plans land in the same directory by convention
- Session Init detects new plan files identically regardless of which agent created them

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

