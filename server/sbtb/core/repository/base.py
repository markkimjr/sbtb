from collections.abc import AsyncGenerator
from typing import Any, Generic, Self, Sequence, TypeVar

from sqlalchemy import (
    Select,
    func,
    over,
    select,
)

from sbtb.core.database.session import DbSession

M = TypeVar("M")


class BaseRepository(Generic[M]):
    model: type[M]

    def __init__(self, session: DbSession) -> None:
        self.session = session

    async def get_one_or_none(self, statement: Select[tuple[M]]) -> M | None:
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, id: str | int) -> M | None:
        statement = self.get_base_statement().where(self.model.id == id)  # type: ignore
        return await self.get_one_or_none(statement)

    async def get_all(self, statement: Select[tuple[M]]) -> Sequence[M]:
        result = await self.session.execute(statement)
        return result.scalars().unique().all()

    async def stream(self, statement: Select[tuple[M]]) -> AsyncGenerator[M, None]:
        results = await self.session.stream(statement)
        async for result in results.unique().scalars():
            yield result

    async def paginate(self, statement: Select[tuple[M]], *, limit: int, page: int) -> tuple[list[M], int]:
        offset = (page - 1) * limit
        paginated_statement: Select[tuple[M, int]] = (
            statement.add_columns(over(func.count())).limit(limit).offset(offset)
        )
        results = await self.session.stream(paginated_statement)

        items: list[M] = []
        count = 0
        async for result in results.unique():
            item, count = result._tuple()
            items.append(item)

        return items, count

    def get_base_statement(self) -> Select[tuple[M]]:
        return select(self.model)

    async def create(self, object: M, *, flush: bool = False) -> M:
        self.session.add(object)

        if flush:
            await self.session.flush()

        return object

    async def update(
        self,
        object: M,
        *,
        update_dict: dict[str, Any] | None = None,
        flush: bool = False,
    ) -> M:
        if update_dict is not None:
            for attr, value in update_dict.items():
                setattr(object, attr, value)

        self.session.add(object)

        if flush:
            await self.session.flush()

        return object

    async def delete(
        self,
        object: M,
        *,
        flush: bool = False,
    ):
        await self.session.delete(object)

        if flush:
            await self.session.flush()

        return object

    @classmethod
    def from_session(cls, session: DbSession) -> Self:
        return cls(session)
