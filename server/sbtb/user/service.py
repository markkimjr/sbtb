from uuid import UUID

import structlog

from sbtb.core.database.session import DbSession
from sbtb.models import User
from sbtb.user.repository import UserRepository

logger = structlog.get_logger(__name__)


class UserService:
    async def get_or_provision_from_jwt(
        self,
        *,
        session: DbSession,
        payload: dict,
    ) -> User:
        """Return the User for this JWT, creating the row on first contact."""
        user_id: UUID = UUID(payload["sub"])
        repo = UserRepository.from_session(session=session)

        existing = await repo.get_by_id(id=user_id)
        if existing is not None:
            return existing

        try:
            return await repo.upsert_from_jwt(
                id=user_id,
                email=payload.get("email"),
            )
        except Exception:
            logger.exception("Failed to provision user", user_id=user_id)
            raise


user_service = UserService()
