# @sbtb/web

Next.js 15 web app for sbtb (Saved By The Bell).

## Setup

```bash
cd clients
pnpm install
cp apps/web/.env.example apps/web/.env.local
# edit apps/web/.env.local — paste your Supabase anon key from:
# https://supabase.com/dashboard/project/dldlbwfgushjbmwkqqcj > Settings > API
```

## Development

```bash
# from clients/
pnpm --filter @sbtb/web dev

# or from clients/apps/web/
pnpm dev
```

Open http://localhost:3001.

## Scripts

| Command | Description |
|---|---|
| `pnpm dev` | Dev server on :3001 (Turbopack) |
| `pnpm build` | Production build |
| `pnpm lint` | Biome lint |
| `pnpm lint:fix` | Biome lint with auto-fix |
| `pnpm typecheck` | TypeScript check (no emit) |
| `pnpm test` | Vitest unit tests |

## Project structure

```
src/
├── app/
│   ├── (app)/          # main app chrome — fighters + profile
│   ├── (auth)/         # stripped auth pages — login/signup/etc
│   ├── auth/callback/  # OAuth + email-verify code exchange
│   ├── layout.tsx      # root: providers, fonts, theme
│   └── page.tsx        # redirect → /fighters
├── components/
│   ├── auth/           # LoginForm, SignupForm, GoogleOAuthButton, etc.
│   ├── fighters/       # FighterCarousel, FighterCard, BookmarkButton, etc.
│   ├── profile/        # NotificationPreferences, BookmarkedFightersGrid, etc.
│   ├── header.tsx
│   └── ui/             # shadcn primitives
├── hooks/              # useUser, useToggleBookmark
├── lib/
│   ├── supabase/       # browser / server / middleware clients
│   ├── api-client.ts   # JWT-injecting fetch wrapper for FastAPI
│   ├── env.ts          # zod env validation
│   ├── fonts.ts        # Fraunces + Inter via next/font
│   ├── mock-fighters.ts
│   └── utils.ts        # cn()
├── providers/          # ThemeProvider, QueryProvider, AuthListener
├── store/              # Zustand: carousel + modal/bookmarks
└── types/
    └── fighter.ts
```

## Notes

This session ships the bootstrap: auth + UI shell with mock fighter data.
Real backend wiring (fighters API, bookmarks persistence, notification prefs) is a follow-up.

**Before testing auth:** replace `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env.local` with
the real anon key from your Supabase dashboard — Project Settings → API → anon public.
