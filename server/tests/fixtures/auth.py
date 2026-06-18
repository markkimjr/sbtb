from collections.abc import Callable
from uuid import UUID, uuid4

import httpx
import pytest
import pytest_asyncio

from sbtb.models import User
from tests.factories.jwt import create_test_jwt
from tests.factories.user import create_test_user
from tests.fixtures.database import SaveFixture


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_client(
    client: httpx.AsyncClient,
) -> Callable[[str], httpx.AsyncClient]:
    """Return a callable that returns the test client with auth headers merged.

    Usage:
        async def test_x(auth_client, user_jwt):
            _, token = user_jwt
            response = await auth_client(token).get("/api/user/me")
    """

    def _build(token: str) -> httpx.AsyncClient:
        client.headers.update(_auth_headers(token))
        return client

    return _build


@pytest_asyncio.fixture
async def user_jwt(save_fixture: SaveFixture) -> tuple[User, str]:
    user = await create_test_user(save_fixture)
    return user, create_test_jwt(sub=user.id, email=user.email)


@pytest_asyncio.fixture
async def superuser_jwt(save_fixture: SaveFixture) -> tuple[User, str]:
    user = await create_test_user(save_fixture, is_superuser=True)
    return user, create_test_jwt(sub=user.id, email=user.email)


@pytest_asyncio.fixture
def unprovisioned_jwt() -> tuple[UUID, str]:
    """Valid JWT for a Supabase user whose public.users row does not yet exist."""
    sub = uuid4()
    return sub, create_test_jwt(sub=sub, email=f"new-{sub}@example.com")
