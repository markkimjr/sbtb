import pytest
from sqlalchemy import select

from sbtb.models import User


@pytest.mark.asyncio
class TestGetUserMe:
    async def test_returns_401_without_auth(self, client) -> None:
        response = await client.get("/api/user/me")
        assert response.status_code == 401

    async def test_returns_existing_user(self, auth_client, user_jwt) -> None:
        user, token = user_jwt
        response = await auth_client(token).get("/api/user/me")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(user.id)
        assert body["email"] == user.email
        assert body["isSuperuser"] is False
        assert body["isActive"] is True

    async def test_provisions_new_user_on_first_request(self, auth_client, unprovisioned_jwt, session) -> None:
        sub, token = unprovisioned_jwt

        response = await auth_client(token).get("/api/user/me")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == str(sub)

        persisted = (await session.execute(select(User).where(User.id == sub))).scalar_one()
        assert persisted.id == sub

    async def test_superuser_flag_passes_through(self, auth_client, superuser_jwt) -> None:
        _, token = superuser_jwt
        response = await auth_client(token).get("/api/user/me")
        assert response.status_code == 200
        assert response.json()["isSuperuser"] is True
