from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt as pyjwt

from tests.fixtures.jwt_keys import TEST_PRIVATE_KEY_PEM


def create_test_jwt(
    sub: UUID,
    email: str | None = "test@example.com",
    audience: str = "authenticated",
    expired: bool = False,
) -> str:
    """ES256-signed JWT shaped like a Supabase-issued one."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "email": email,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now - timedelta(hours=1) if expired else now + timedelta(hours=1)).timestamp()),
    }
    return pyjwt.encode(payload, TEST_PRIVATE_KEY_PEM, algorithm="ES256")
