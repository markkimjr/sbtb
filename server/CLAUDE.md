# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Saved By The Bell (sbtb)** — a boxing notification service that crawls fighter rankings and upcoming fight card data, then notifies users when their favorite fighter is scheduled to fight next. Built with FastAPI, SQLAlchemy (async), asyncpg, and PostgreSQL. Runs on **Python 3.12**.

## Commands

```bash
# Setup
uv sync

# Activate virtual environment (optional — uv run auto-activates)
source .venv/bin/activate

# Run development server
export PYTHONUNBUFFERED=1 SBTB_ENV=local
uvicorn sbtb.app:app --reload

# Database migrations
uv run alembic upgrade head                              # Apply all migrations
uv run alembic revision --autogenerate -m "description" # Create new migration

# Linting and formatting
uv run ruff check .          # Lint
uv run ruff check --fix .    # Lint and auto-fix
uv run ruff format .         # Format
```

## Architecture

### Module Structure (`sbtb/`)
- **`app.py`** — FastAPI app factory with middleware (CORS, Sentry, correlation IDs)
- **`routes.py`** — API router combining all domain routers under `/api`

### Domain Modules
Each domain follows this pattern: `{domain}/routes.py`, `{domain}/schemas.py`, `{domain}/service.py`, `{domain}/repository.py`
- `fighter/` — Fighter rankings, fight cards, scraping (BoxingRankScraper, BoxingFightCardScraper)

### Core (`sbtb/core/`)
- `config.py` — Settings via pydantic-settings; `SBTB_ENV` selects `.env.local`, `.env.test`, or `.env.prod`
- `database/base.py` — SQLAlchemy base models (`RecordModel` with UUID pk, timestamps)
- `database/session.py` — Async SQLAlchemy session; provides `DbSession` dependency
- `schemas.py` — `BaseSchema`, `IDSchema`, `TimestampedSchema` (Pydantic base classes)

### Models (`sbtb/models/`)
One file per model. All models imported and re-exported from `sbtb/models/__init__.py` so Alembic can discover them with a single import.

Key entities: `Fighter`, `FightCard`, `Bout`, `Rank`, `FightOrganization`, `WeightClass`, `User`

### Migrations (`migrations/`)
Alembic migrations at `server/migrations/`, same level as `server/sbtb/`.

## Environment Configuration

Environment is controlled by `SBTB_ENV`:
- `local` → loads `.env.local` — local development
- `testing` → loads `.env.test` — test environment
- `production` → loads `.env.prod` — production server

### Two Database URLs
- `POSTGRES_DATABASE_URL` (port 6543) — transaction pooler (PgBouncer), used by the app
- `POSTGRES_DATABASE_SESSION_URL` (port 5432) — direct connection, used by Alembic migrations

## Database Session / Transaction Model

Each request that injects `DbSession` (`sbtb/core/database/session.py`) is **fully transactional**. The `get_session()` dependency wraps every request in a try/except/else block:

```python
async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
```

- **No exception raised** → `session.commit()` is called automatically when the request completes.
- **Exception raised** → `session.rollback()` is called automatically.

**Implications for service code:**
- Never call `session.commit()` inside service methods — the request lifecycle handles the commit.
- Use `session.flush()` when you need to write pending changes to the DB mid-request (e.g. to get a generated primary key, or make changes visible to subsequent queries in the same request).

## Service Pattern

Services are stateless classes with module-level singleton instances. Sessions and repos are never stored on the service — they are instantiated per method call:

```python
class ExampleService:
    async def do_something(self, session: DbSession) -> list[Thing]:
        repo = ThingRepo.from_session(session)
        return await repo.get_all()

example_service = ExampleService()
```

Routes import the singleton directly and receive `session: DbSession` via FastAPI's type annotation injection — no `Depends()` needed for the service itself:

```python
from sbtb.fighter.service import example_service

@router.get("/things")
async def get_things(session: DbSession) -> list[ThingRead]:
    return await example_service.do_something(session=session)
```

## Repository Pattern

All repositories inherit from `BaseRepository[M]` and instantiate via `Repo.from_session(session)`. Repos use `flush()`, never `commit()` — transaction lifecycle belongs to the session dependency.

## Code Quality

### Ruff (Linting + Formatting)
This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting (replaces Black + flake8).

```bash
uv run ruff check .          # Lint
uv run ruff check --fix .    # Lint and auto-fix
uv run ruff format .         # Format
```

Configured in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I"]
```

Migrations are excluded from formatting.

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

## Coding Style & Conventions

### SOLID Design Principles
- **Single Responsibility** — each module, class, and function has one clear purpose. Routes handle HTTP. Services handle business logic. Repos handle data access.
- **Open/Closed** — extend behavior by adding new classes/methods, not by modifying existing ones.
- **Liskov Substitution** — subtypes (e.g. specific repos) are interchangeable with their base type (`BaseRepository`).
- **Interface Segregation** — keep interfaces focused. Don't add methods to a class that its consumers don't need.
- **Dependency Inversion** — depend on abstractions (base classes, typed interfaces), not concrete implementations.

### Always Use Keyword Arguments
```python
# Good
result = fighter_repo.get_or_create(name=fighter_name)

# Avoid
result = fighter_repo.get_or_create(fighter_name)
```

### Type Hints
Always use **modern Python 3.10+ type hint syntax**. Never use `typing.Optional`, `typing.List`, `typing.Dict`, or `typing.Tuple` — use native types and `|` union syntax instead:

```python
# Good — native types
async def get_fighters(session: DbSession, limit: int | None = None) -> list[Fighter]:
    ...

def get_map() -> dict[str, list[int]]:
    ...

# Avoid — legacy typing imports
from typing import List, Dict, Optional

async def get_fighters(session: DbSession, limit: Optional[int] = None) -> List[Fighter]:
    ...
```

Only import from `typing` for things unavailable natively: `Any`, `Generic`, `TypeVar`, `Self`, `Annotated`, `TYPE_CHECKING`, `Literal`, etc.

### String Quotations
Use double quotes:
```python
# Good
message = "Hello, world"
config = {"key": "value"}

# Avoid
message = 'Hello, world'
```

### Docstrings
Use Google-style docstrings for non-trivial functions:
```python
async def scrape_and_update_boxing_ranks(self, session: DbSession) -> list[RankRead]:
    """Scrape current boxing rankings and upsert into the database.

    Args:
        session: The active database session for this request.

    Returns:
        List of upserted rank records as read schemas.
    """
```

### Logging
Use `structlog` — never the standard `logging` module:
```python
import structlog

logger = structlog.get_logger(__name__)
```

In `except` blocks, use `logger.exception()` instead of `logger.error()`. It automatically captures the current exception and traceback — no need for `traceback.format_exc()`:

```python
# Good
try:
    ...
except Exception:
    logger.exception("Failed to fetch data")

# Avoid
try:
    ...
except Exception:
    logger.error(f"Failed to fetch data: {traceback.format_exc()}")
```

Use `logger.error()` only for non-exception error conditions (e.g. missing data, validation failures outside of except blocks).

### No Commits in Service Code
Never call `session.commit()` in service or repository methods. Use `session.flush()` for mid-transaction visibility. The request lifecycle in `session.py` owns the commit.
