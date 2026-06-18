from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt as pyjwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials

from sbtb.auth.jwt import get_access_token, validate_jwt_token
from sbtb.core.exceptions import Unauthorized
from tests.factories.jwt import create_test_jwt


class TestGetAccessToken:
    def test_extracts_token_from_bearer_credentials(self) -> None:
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="abc.def.ghi")
        assert get_access_token(credentials=creds) == "abc.def.ghi"

    def test_rejects_non_bearer_scheme(self) -> None:
        creds = HTTPAuthorizationCredentials(scheme="Basic", credentials="abc")
        with pytest.raises(Unauthorized):
            get_access_token(credentials=creds)


@pytest.mark.asyncio
class TestValidateJwtToken:
    async def test_valid_es256_token_returns_payload(self) -> None:
        sub = uuid4()
        token = create_test_jwt(sub=sub, email="user@example.com")

        result = await validate_jwt_token(token=token)

        assert result.is_valid is True
        assert result.payload["sub"] == str(sub)
        assert result.payload["email"] == "user@example.com"
        assert result.payload["aud"] == "authenticated"
        assert result.jwt == token

    async def test_expired_token_raises_unauthorized(self) -> None:
        token = create_test_jwt(sub=uuid4(), expired=True)
        with pytest.raises(Unauthorized):
            await validate_jwt_token(token=token)

    async def test_wrong_audience_raises_unauthorized(self) -> None:
        token = create_test_jwt(sub=uuid4(), audience="service_role")
        with pytest.raises(Unauthorized):
            await validate_jwt_token(token=token)

    async def test_malformed_token_raises_unauthorized(self) -> None:
        with pytest.raises(Unauthorized):
            await validate_jwt_token(token="not-a-jwt")

    async def test_wrong_signature_raises_unauthorized(self) -> None:
        # Sign with a different key entirely
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(uuid4()),
            "email": "x@y.com",
            "aud": "authenticated",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        # Use HS256 with random secret — should fail because backend only accepts ES256/RS256 asymmetric keys
        bad_token = pyjwt.encode(payload, "different-secret", algorithm="HS256")
        with pytest.raises(Unauthorized):
            await validate_jwt_token(token=bad_token)
