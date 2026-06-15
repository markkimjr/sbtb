from collections.abc import AsyncIterator, Callable, Coroutine
from uuid import uuid4

import pytest
import pytest_asyncio
from pydantic_core import Url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from sbtb.core.config import settings
from sbtb.core.database.base import BaseModel
from sbtb.models import *  # noqa — ensures all models are registered on BaseModel.metadata


def get_database_url(driver: str = "asyncpg") -> str:
    return str(
        Url.build(
            scheme=f"postgresql+{driver}",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=int(settings.POSTGRES_PORT),
            path=settings.POSTGRES_DB,
        )
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def initialize_test_database() -> AsyncIterator[None]:
    sync_database_url = get_database_url("psycopg2")
    async_database_url = get_database_url("asyncpg")

    if database_exists(sync_database_url):
        drop_database(sync_database_url)

    create_database(sync_database_url)

    engine = create_async_engine(
        url=async_database_url,
        pool_size=settings.POOL_SIZE,
        future=True,
        max_overflow=settings.MAX_OVERFLOW,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
            "prepared_statement_cache_size": 0,
        },
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    await engine.dispose()

    yield

    drop_database(sync_database_url)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    async_database_url = get_database_url("asyncpg")

    engine = create_async_engine(
        url=async_database_url,
        pool_size=settings.POOL_SIZE,
        future=True,
        max_overflow=settings.MAX_OVERFLOW,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
            "prepared_statement_cache_size": 0,
        },
    )

    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await transaction.rollback()
    await connection.close()
    await engine.dispose()


SaveFixture = Callable[[BaseModel], Coroutine[None, None, None]]


def save_fixture_factory(session: AsyncSession) -> SaveFixture:
    async def _save_fixture(model: BaseModel) -> None:
        session.add(model)
        await session.flush()

    return _save_fixture


@pytest.fixture
def save_fixture(session: AsyncSession) -> SaveFixture:
    return save_fixture_factory(session)
