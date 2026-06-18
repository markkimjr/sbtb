from uuid import UUID, uuid4

import pytest
from sqlalchemy import select

from sbtb.auth.dependencies import get_current_user, get_optional_current_user
from sbtb.auth.jwt import JWTValidationResult
from sbtb.auth.permissions import superuser_only
from sbtb.core.exceptions import NotPermitted, Unauthorized
from sbtb.models import User
from tests.factories.jwt import create_test_jwt


def _jwt_result(sub: UUID, email: str | None = "u@example.com") -> JWTValidationResult:
    return JWTValidationResult(
        is_valid=True,
        payload={"sub": str(sub), "email": email, "aud": "authenticated"},
        jwt=create_test_jwt(sub=sub, email=email),
    )


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_returns_existing_user(self, session, user_jwt) -> None:
        user, _ = user_jwt
        result = _jwt_result(user.id, user.email)

        returned = await get_current_user(session=session, jwt_result=result)

        assert returned.id == user.id
        assert returned.email == user.email

    async def test_provisions_new_user_on_first_call(self, session, unprovisioned_jwt) -> None:
        sub, _ = unprovisioned_jwt
        result = _jwt_result(sub, email="new@example.com")

        returned = await get_current_user(session=session, jwt_result=result)

        assert returned.id == sub
        assert returned.email == "new@example.com"
        assert returned.is_active is True
        assert returned.is_superuser is False

        # Confirm row actually persisted
        persisted = (await session.execute(select(User).where(User.id == sub))).scalar_one()
        assert persisted.id == sub

    async def test_second_call_returns_existing_row_no_dupe(self, session, unprovisioned_jwt) -> None:
        sub, _ = unprovisioned_jwt
        result = _jwt_result(sub)

        first = await get_current_user(session=session, jwt_result=result)
        second = await get_current_user(session=session, jwt_result=result)

        assert first.id == second.id
        count = (await session.execute(select(User).where(User.id == sub))).scalars().all()
        assert len(count) == 1

    async def test_provisions_with_null_email_when_claim_missing(self, session) -> None:
        sub = uuid4()
        result = _jwt_result(sub, email=None)

        returned = await get_current_user(session=session, jwt_result=result)

        assert returned.id == sub
        assert returned.email is None

    async def test_raises_when_jwt_invalid(self, session) -> None:
        bad_result = JWTValidationResult(is_valid=False, payload=None, jwt=None)
        with pytest.raises(Unauthorized):
            await get_current_user(session=session, jwt_result=bad_result)


@pytest.mark.asyncio
class TestGetOptionalCurrentUser:
    async def test_returns_none_when_no_jwt(self, session) -> None:
        returned = await get_optional_current_user(session=session, jwt_result=None)
        assert returned is None

    async def test_returns_user_when_jwt_present(self, session, user_jwt) -> None:
        user, _ = user_jwt
        result = _jwt_result(user.id, user.email)

        returned = await get_optional_current_user(session=session, jwt_result=result)
        assert returned is not None
        assert returned.id == user.id


@pytest.mark.asyncio
class TestSuperuserOnly:
    async def test_returns_superuser(self, superuser_jwt) -> None:
        user, _ = superuser_jwt
        returned = await superuser_only(current_user=user)
        assert returned.id == user.id
        assert returned.is_superuser is True

    async def test_rejects_non_superuser(self, user_jwt) -> None:
        user, _ = user_jwt
        with pytest.raises(NotPermitted):
            await superuser_only(current_user=user)
