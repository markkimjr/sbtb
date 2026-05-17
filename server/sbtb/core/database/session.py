from typing import Annotated, AsyncGenerator
from uuid import uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sbtb.core.config import settings

engine = create_async_engine(
    settings.POSTGRES_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=settings.POOL_SIZE,
    pool_pre_ping=True,
    max_overflow=settings.MAX_OVERFLOW,
    connect_args={
        "statement_cache_size": 0,  # Disable statement cache for asyncpg (use transaction connection pooler)
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
        "prepared_statement_cache_size": 0,
    },
)

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()


DbSession = Annotated[AsyncSession, Depends(get_session)]
