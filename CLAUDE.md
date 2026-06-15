# sbtb

Boxing notification service. Crawls fighter rankings and upcoming fight cards, notifies users when their bookmarked fighters are scheduled to fight. Monorepo with a Python/FastAPI backend and a Next.js frontend.

## Quick Start

```bash
# Backend (http://localhost:8000)
cd server
uv sync                                          # Install dependencies
export PYTHONUNBUFFERED=1 SBTB_ENV=local
uvicorn sbtb.app:app --reload                    # Dev server

# Database migrations
uv run alembic upgrade head

# Frontend (http://localhost:3001)
cd clients
pnpm install && pnpm dev
```

## Architecture

```
sbtb/
├── server/                     # FastAPI backend (see server/CLAUDE.md)
│   ├── sbtb/
│   │   ├── {domain}/           # routes.py · service.py · repository.py · schemas.py
│   │   │   └── fighter/
│   │   │       └── avatar_generators/  # gemini.py · openai.py · replicate.py · replicate_template.py
│   │   ├── core/               # config, database session, integrations
│   │   └── models/             # SQLAlchemy models
│   └── migrations/             # Alembic migrations
└── clients/                    # Frontend monorepo (see clients/CLAUDE.md)
    ├── apps/web/               # Next.js 15 website (@sbtb/web, port 3001)
    └── packages/               # Shared packages (future)
```

## Core Rules

See subdirectory CLAUDE.md files for detailed patterns:
- `server/CLAUDE.md` — backend patterns (FastAPI, SQLAlchemy, service/repository, migrations)
- `clients/CLAUDE.md` — frontend patterns (Next.js, Supabase auth, TanStack Query, Zustand, Biome)

## Key Integrations

- **Supabase**: PostgreSQL database, auth (JWT), and file storage (boxer avatar images)
- **Gemini / OpenAI**: AI image generation for fighter Ghibli-style avatars
- **SerpAPI**: Google Images search for fighter reference photos
- **Sentry**: Error tracking (backend)
