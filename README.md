# Saved By The Bell

Never miss a fight. **Saved By The Bell** notifies you when your favorite boxer is scheduled to compete next.

## Why

Unlike the NBA, NFL, or MLB — where every team plays on a fixed schedule published months in advance — boxing has no central organizing body. Fights are negotiated and announced independently, sometimes just weeks out, spread across dozens of promoters and broadcasters.

Boxing fans don't follow a team. They follow individual fighters: Ryan Garcia, Gervonta Davis, Canelo Álvarez. But there's no reliable way to know when your fighter is next scheduled to compete without constantly checking Twitter, ESPN, and individual promoter sites.

Saved By The Bell solves this. Bookmark the fighters you care about, and we'll do the watching for you — notifying you the moment a fight is announced and reminding you as it gets closer.

Browse a curated roster of active fighters, bookmark the ones you follow, and get an email the moment a fight card drops with them on it. No more checking sports sites daily — we ring the bell when it matters.

## What it does

- **Fighter discovery** — browse ranked fighters across all weight classes with Ghibli-style portraits
- **Bookmarks** — save fighters you want to follow
- **Fight card tracking** — crawls upcoming fight cards and matches them against your bookmarks
- **Email notifications** — sends you a heads-up when a bookmarked fighter is scheduled to fight
- **Notification preferences** — choose which alerts you receive: when a fight is first announced, 1 week out, 1 day before, and day-of. Turn each on or off independently so you only get the reminders that matter to you

## Stack

**Backend** — Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL via Supabase, asyncpg

**Frontend** — Next.js 15, React 19, TypeScript, Tailwind CSS 4, Supabase Auth

**Infrastructure** — Supabase (database + auth + storage), Sentry (error tracking)

## Repo structure

```
sbtb/
├── server/          # FastAPI backend
└── clients/
    └── apps/web/    # Next.js frontend
```

See `server/CLAUDE.md` and `clients/CLAUDE.md` for development setup and conventions.
