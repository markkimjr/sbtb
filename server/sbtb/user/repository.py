from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sbtb.core.repository.base import BaseRepository
from sbtb.models import User


class UserRepository(BaseRepository[User]):
    model = User

    async def upsert_from_jwt(
        self,
        *,
        id: UUID,
        email: str | None,
    ) -> User:
        """Race-safe provisioning of a public.users row from a Supabase JWT.

        Uses INSERT ... ON CONFLICT DO NOTHING so concurrent first-requests for
        the same user resolve to a single row. If the insert no-ops (another
        request won the race), we re-SELECT to return the existing row.
        """
        statement = (
            pg_insert(User)
            .values(id=id, email=email, is_active=True, is_superuser=False)
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(User)
        )
        result = await self.session.execute(statement)
        await self.session.flush()
        inserted = result.scalar_one_or_none()
        if inserted is not None:
            return inserted

        existing = (await self.session.execute(select(User).where(User.id == id))).scalar_one()
        return existing
