"""Session-scoped ES256 keypair for signing test JWTs.

Provides an autouse fixture that replaces sbtb.auth.jwt._get_jwks_client with a
stub returning our test public key, so JWT verification never hits the real
Supabase JWKS endpoint.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

import sbtb.auth.jwt as auth_jwt_module

_private_key = ec.generate_private_key(ec.SECP256R1())
_public_key = _private_key.public_key()

TEST_PRIVATE_KEY_PEM: bytes = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

TEST_PUBLIC_KEY_PEM: bytes = _public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)


@pytest.fixture(autouse=True)
def mock_jwks_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Patch _get_jwks_client so JWT verification uses our test public key."""
    fake_signing_key = MagicMock()
    fake_signing_key.key = TEST_PUBLIC_KEY_PEM

    fake_client = MagicMock()
    fake_client.get_signing_key_from_jwt = MagicMock(return_value=fake_signing_key)

    monkeypatch.setattr(auth_jwt_module, "_get_jwks_client", lambda: fake_client)
    yield
