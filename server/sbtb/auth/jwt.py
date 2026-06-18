import jwt
import structlog
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from sbtb.core.config import settings
from sbtb.core.exceptions import Unauthorized

logger = structlog.get_logger(__name__)

security = HTTPBearer()

# Lazily-initialized JWKS client for ES256/RS256 verification
_jwks_client: jwt.PyJWKClient | None = None


def _get_jwks_client() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


class JWTValidationResult(BaseModel):
    is_valid: bool
    payload: dict | None = None
    jwt: str | None = None


def get_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise Unauthorized(message="Invalid auth header")
    return credentials.credentials


async def validate_jwt_token(
    token: str = Depends(get_access_token),
) -> JWTValidationResult:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            audience="authenticated",
            algorithms=["ES256", "RS256"],
            leeway=3,
        )
        return JWTValidationResult(is_valid=True, payload=payload, jwt=token)
    except Exception:
        logger.exception("Error validating JWT token")
        raise Unauthorized(message="Invalid or expired token")
