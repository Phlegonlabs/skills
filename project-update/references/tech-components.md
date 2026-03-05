# Tech Components (Modular Stack Selection)

Libraries marked ⚠ DEPRECATED should not be selected. Review this list when updating `assets/versions.json`.

Use this file in interview rounds to pick stack modules by category.
Reference version suggestions from `assets/versions.json`.

## 1. Framework / Meta-Framework
- Vite + React (react 19, vite 6.x): modern SPA baseline.
- Next.js (15): SSR/SSG, content and commerce.
- TanStack Start (1.x): type-safe React full-stack.
- Remix / React Router v7 (7.x): progressive SSR full-stack.
- SvelteKit (2.x): performance-first websites.

## 2. Routing
- TanStack Router 1.163.x: best type-safety for new React SPA.
- React Router 7.x: migration path from RRv6/Remix.
- Framework-native routing: use when on Next/Svelte/Nuxt.

## 3. State Management
- Zustand 5.x: default lightweight state.
- TanStack Query 5.x: server-state/cache.
- Jotai 2.x: atomized state graph.
- Redux Toolkit 2.x: enterprise Redux legacy investment.
- XState 5.x: complex workflow state machine.

## 4. UI Components
- shadcn/ui: customizable modern React UI.
- Radix UI: unstyled primitives for custom design systems.
- Mantine 8.x: all-in-one component + hooks toolkit.
- HeroUI 2.x: Tailwind-friendly component suite.
- Ant Design 5.x / MUI 6.x: enterprise data-dense UI.

## 5. CSS / Styling
- Tailwind CSS 4.0: default utility-first baseline.
- UnoCSS 66.x: highly flexible utility engine.
- Panda CSS 1.3: zero-runtime typed styling.
- CSS Modules: minimal dependency choice.
- NativeWind 4.x: React Native utility styling.

## 6. Backend
- Hono 4.x: edge/multi-runtime backend.
- oRPC 1.x: TS-first RPC + OpenAPI capable.
- Elysia 1.x: Bun-native high-performance backend.
- tRPC 11.x: TS monorepo internal API.
- Fastify 5.x / NestJS 11.x / FastAPI 0.115+: specialized alternatives.

## 7. Database
- Supabase, Cloudflare D1, Turso/libSQL, Neon, Convex, SQLite local.

## 8. ORM
- Drizzle, Prisma 7, Kysely.

## 9. Auth
- Better Auth, Clerk, Auth.js v5, Supabase Auth, WorkOS, Kinde.
- Lucia is deprecated (2025-03), do not choose.

## 10. Deployment
- Cloudflare, Vercel, Railway, Fly.io, SST, Coolify.

## 11. Email
- Resend + React Email, Postmark, AWS SES.

## 12. Storage
- Cloudflare R2, AWS S3, Uploadthing.

## 13. Background Jobs
- Trigger.dev v3, Inngest, BullMQ, Cloudflare Queues.

## 14. Payments
- Stripe, LemonSqueezy, Paddle, X402.

## 15. Analytics / Monitoring
- PostHog, Plausible/Umami, Sentry, OpenTelemetry.

## 16. Validation
- Zod, Valibot, ArkType, Standard Schema v1.

## 17. AI / LLM Integration
- Vercel AI SDK v6, Mastra, LangChain JS, OpenRouter.

## 18. Testing
- Vitest 2.x, Playwright 1.4x, React Testing Library, bun test.

## 19. Dev Tools
- Biome 2.3, ESLint 9 + Prettier 3.7, pnpm 9.x, bun 1.x, Turborepo 2.x.

## 20. Rich Text / Animation / Charts
- Rich text: TipTap / BlockNote / Lexical.
- Animation: Motion 11 / GSAP / Lottie.
- Charts: Recharts / Tremor / Nivo / D3.

## Composition Examples
- Modern SPA (B2B SaaS): Vite + React -> TanStack Router -> Zustand + Query -> shadcn/ui -> Tailwind -> Hono -> Drizzle + D1 -> Better Auth -> Cloudflare.
- Content Site: Astro -> Tailwind -> shadcn/ui -> Cloudflare Pages -> Plausible.
- Mobile App: Expo -> Expo Router -> Zustand -> NativeWind -> Hono -> Supabase.
- AI SaaS: Next.js -> Query -> Zustand -> shadcn/ui -> Tailwind -> Vercel AI SDK + Mastra -> Supabase + pgvector.
- Web3 DApp: Vite + React -> Router -> wagmi + viem -> shadcn/ui -> Tailwind -> Hono -> X402.
