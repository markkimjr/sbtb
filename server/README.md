# Saved By The Bell — Server

Boxing notification service that crawls fighter rankings and upcoming fight cards, then notifies users when their favorite fighter is scheduled to fight next.

## Tech Stack

- **Python 3.12**
- **FastAPI** — async web framework
- **SQLAlchemy 2.x (async)** + **asyncpg** — database ORM
- **PostgreSQL** (Supabase) — primary database
- **Alembic** — database migrations
- **aiohttp** — async HTTP for scraping
- **Selenium + ChromeDriver** — fight card scraping (JavaScript-rendered pages)
- **Ruff** — linting and formatting
- **uv** — dependency management

## Setup

Install Python 3.12 and [uv](https://docs.astral.sh/uv/):

```bash
brew install uv
```

Install dependencies:

```bash
uv sync
```

## Environment

Copy the example env file and fill in your values:

```bash
cp .env.example .env.local
```

Environment is selected via `SBTB_ENV`:

| `SBTB_ENV` | Config file | Usage |
|---|---|---|
| `local` | `.env.local` | Local development |
| `testing` | `.env.test` | Test environment |
| `production` | `.env.prod` | Production server |

## Running the Server

```bash
export PYTHONUNBUFFERED=1 SBTB_ENV=local
uvicorn sbtb.app:app --reload
```

## Database Migrations

Apply all pending migrations:

```bash
uv run alembic upgrade head
```

Create a new migration after model changes:

```bash
uv run alembic revision --autogenerate -m "description"
```

> **Note:** Migrations use a direct PostgreSQL connection (port 5432), not the PgBouncer transaction pooler (port 6543), because DDL statements are incompatible with transaction pooling.

## Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
uv run ruff check .          # Lint
uv run ruff check --fix .    # Lint and auto-fix
uv run ruff format .         # Format
```

### Pre-commit Hooks

Install hooks after cloning:

```bash
uv run pre-commit install
```

The following checks run automatically on every `git commit`:
- **ruff** — lints staged Python files, blocks commit on errors
- **ruff-format** — formats staged Python files in place (re-stage and recommit if changed)
- **uv-lock** — validates `uv.lock` is up to date
- **uv-export** — regenerates `requirements.txt` when `pyproject.toml` or `uv.lock` changes

## Project Structure

```
server/
├── sbtb/
│   ├── app.py               # FastAPI app factory
│   ├── routes.py            # Top-level router (/api/v1)
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── schemas.py       # BaseSchema, IDSchema, TimestampedSchema
│   │   └── database/
│   │       ├── base.py      # RecordModel (UUID pk, timestamps)
│   │       └── session.py   # Async session, DbSession dependency
│   ├── models/
│   │   ├── __init__.py      # Central model exports (for Alembic)
│   │   ├── fighter.py
│   │   ├── fight_card.py
│   │   ├── bout.py
│   │   ├── rank.py
│   │   ├── fight_organization.py
│   │   ├── weight_class.py
│   │   └── user.py
│   └── fighter/
│       ├── routes.py        # HTTP endpoints
│       ├── service.py       # Business logic + module-level singletons
│       ├── repository.py    # Data access (inherits BaseRepository)
│       ├── schemas.py       # Pydantic request/response schemas
│       ├── scraper.py       # BoxingRankScraper, BoxingFightCardScraper
│       └── driver.py        # ChromeDriver setup (Selenium)
└── migrations/              # Alembic migration files
```
