from uuid import uuid4

from sbtb.models import User
from tests.fixtures.database import SaveFixture


async def create_test_user(
    save_fixture: SaveFixture,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    user = User(
        id=uuid4(),
        email=f"test-{uuid4()}@example.com",
        is_active=is_active,
        is_superuser=is_superuser,
    )
    await save_fixture(user)
    return user
