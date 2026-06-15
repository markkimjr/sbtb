# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Saved By The Bell (sbtb) — clients monorepo.** Turborepo + pnpm workspaces. Currently contains one app (`apps/web/`), the main Next.js website. Additional apps (e.g. `apps/app/` for React Native iOS/Android) may be added under `apps/` in the future. Shared packages live in `packages/` (currently empty placeholder).

- **Runtime:** Node >= 22, pnpm 10.28
- **Web app:** Next.js 15, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Zustand, TanStack Query, Framer Motion, Vitest

## Commands

```bash
# Install dependencies (from clients/ root)
pnpm install

# Dev server — Next.js on port 3001 (run from clients/ root or apps/web/)
pnpm dev

# Build all apps via Turborepo
pnpm build

# Lint (Biome)
pnpm lint            # check only
pnpm lint:fix        # check + auto-fix (web only, run from apps/web/)

# Format (Biome)
pnpm format          # biome format --write . (from clients/ root)

# Type-check
pnpm typecheck       # tsc --noEmit

# Tests (Vitest)
pnpm test            # vitest run (single pass)
pnpm test:watch      # vitest (watch mode)
```

## Monorepo Structure

```
clients/
  apps/
    web/              # @sbtb/web — main Next.js website
  packages/           # future shared packages (currently empty)
  biome.json          # root Biome config (lint + format rules)
  tsconfig.base.json  # shared TypeScript compiler options
  turbo.json          # Turborepo task pipeline
  pnpm-workspace.yaml
```

## Web App (`apps/web/`)

### Directory Layout

```
src/
  app/
    (app)/            # authenticated shell — wrapped in Header + main layout
      fighters/       # /fighters — main fighter browsing page
      profile/        # /profile — bookmarked fighters + notification prefs
    (auth)/           # unauthenticated auth pages — centered card layout
      login/
      signup/
      forgot-password/
      verify-email/
    auth/callback/    # Supabase OAuth callback route handler
    layout.tsx        # root layout: fonts, ThemeProvider, QueryProvider, AuthListener, Toaster
  components/
    ui/               # shadcn/ui primitives (button, card, dialog, etc.)
    auth/             # auth form components
    fighters/         # fighter-specific components
    profile/          # profile-specific components
    header.tsx
  hooks/              # custom React hooks
  lib/
    api-client.ts     # apiFetch — thin fetch wrapper with JWT injection
    env.ts            # Zod-validated env vars (throws at startup if missing)
    fonts.ts          # Fraunces + Inter font definitions
    supabase/
      browser.ts      # createClient() — browser Supabase client
      server.ts       # createClient() — server-side Supabase client (cookies)
      middleware.ts    # updateSession() — refreshes Supabase session in middleware
  providers/
    auth-listener.tsx # invalidates TanStack Query user cache on auth state change
    query-provider.tsx
    theme-provider.tsx
  store/
    carousel.ts       # Zustand: fighter carousel index + navigation
    modal.ts          # Zustand: bookmark set, first-bookmark modal, intro-seen flag
  types/
    fighter.ts        # Fighter and WeightClass types (mirrors backend schemas)
```

### Route Groups

- **`(app)/`** — authenticated app shell. `layout.tsx` renders `<Header />` and wraps children in `<main>`. Middleware gates `/profile` — unauthenticated visitors are redirected to `/login?next=/profile`.
- **`(auth)/`** — unauthenticated pages (login, signup, forgot-password, verify-email). Centered card layout, no header.

### Authentication

Auth is handled by **Supabase `@supabase/ssr`** directly — there is no FastAPI auth proxy.

- **Browser client** (`lib/supabase/browser.ts`) — used in Client Components and hooks.
- **Server client** (`lib/supabase/server.ts`) — used in Server Components and Route Handlers; reads/writes cookies via `next/headers`.
- **Middleware** (`middleware.ts` + `lib/supabase/middleware.ts`) — calls `supabase.auth.getUser()` on every non-static request to refresh the session cookie. Also redirects unauthenticated users away from protected routes (`/profile`).
- **`AuthListener`** (`providers/auth-listener.tsx`) — a `"use client"` component mounted in the root layout that subscribes to `onAuthStateChange` and invalidates the `["auth", "user"]` TanStack Query key. This keeps `useUser()` in sync across tabs and after login/logout.

### API Client

`lib/api-client.ts` exports `apiFetch<T>(path, init?)` — a thin wrapper around `fetch` that:
1. Reads the current Supabase session from the browser client.
2. Injects `Authorization: Bearer <access_token>` if a session exists.
3. Prefixes the path with `NEXT_PUBLIC_API_URL`.
4. Throws `ApiError(status, detail)` on non-2xx responses.

All calls to the FastAPI backend should go through `apiFetch`.

### Environment Variables

Validated at startup via Zod in `lib/env.ts`. Import `env` from there — never read `process.env` directly.

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon/public key |
| `NEXT_PUBLIC_API_URL` | FastAPI backend base URL (e.g. `http://localhost:8000/api`) |

Copy `apps/web/.env.example` to `apps/web/.env.local` and fill in values.

### State Management

- **TanStack Query** — server state (API data, auth user). `useUser()` uses `staleTime: Infinity` and is invalidated on auth events by `AuthListener`.
- **Zustand** — UI-only state that doesn't need to be fetched:
  - `useCarouselStore` — active carousel index and total count.
  - `useModalStore` — in-memory bookmark set, first-bookmark modal open state, and `hasSeenIntro` flag.

> **Note:** Bookmarks are currently stored in-memory in Zustand (mock data). Persistence to the backend is not yet implemented.

### Path Alias

`@` resolves to `src/`. Use `@/` for all imports within `apps/web/src/`.

```ts
// Good
import { apiFetch } from "@/lib/api-client";

// Avoid
import { apiFetch } from "../../lib/api-client";
```

### Design Tokens & Fonts

CSS custom properties are defined in `globals.css`:

| Token | Usage |
|---|---|
| `--color-persimmon` | Primary accent (red-orange) |
| `--color-parchment` | Background / card fill |
| `--color-ink` | Primary text |
| `--color-sand` | Borders, dividers |

Two typefaces are loaded via `lib/fonts.ts` and exposed as CSS variables:

- **Fraunces** (`--font-fraunces`) — display / italic headlines. Use the `font-display` Tailwind class.
- **Inter** (`--font-inter`) — body text. Default sans.

### Linting & Formatting

This project uses **Biome** (not ESLint or Prettier). Configuration cascades:
- `clients/biome.json` — root rules (line width 100, double quotes, trailing commas, `useImportType` off)
- `apps/web/biome.json` — extends root config

```bash
# From clients/ root
pnpm format          # format everything

# From apps/web/
pnpm lint            # biome check .
pnpm lint:fix        # biome check --write .
```

### Testing

Vitest with jsdom. `globals: false` — import `describe`, `it`, `expect` explicitly. Path alias `@` is resolved via `vitest.config.ts`.

```bash
pnpm test            # single run (CI)
pnpm test:watch      # watch mode (development)
```

Test files live next to the code they test (e.g. `hooks/use-toggle-bookmark.test.ts`, `store/carousel.test.ts`).

## Coding Style & Conventions

### TypeScript

- Strict mode. No `any` (warned by Biome). No `// @ts-ignore`.
- Always use `import type` for type-only imports... but `useImportType` is turned off in Biome so mixing is fine.
- Modern syntax: `string | null` not `Optional<string>`, `Array<T>` or `T[]` are both acceptable.

### Components

- All interactive or browser-API-dependent components must be `"use client"`.
- Server Components are the default — avoid `"use client"` unless necessary.
- shadcn/ui components live in `components/ui/` and should not be modified directly. Wrap or compose them for customisation.
- Domain components (`components/fighters/`, `components/auth/`, etc.) are the right place for feature-specific logic.

### Auth Redirect Pattern

When redirecting after auth, use the `?next=` query param:

```ts
router.push(`/login?next=${encodeURIComponent(pathname)}`);
```

The post-signup auto-bookmark flow additionally uses `?fighter=<id>` — `FightersPage` reads this on mount and bookmarks the fighter if the user just signed up.

### No Direct `process.env` Reads

Always import from `@/lib/env`:

```ts
// Good
import { env } from "@/lib/env";
const url = env.NEXT_PUBLIC_API_URL;

// Avoid
const url = process.env.NEXT_PUBLIC_API_URL;
```
