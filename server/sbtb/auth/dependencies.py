from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sbtb.auth.jwt import JWTValidationResult, validate_jwt_token
from sbtb.core.database.session import DbSession
from sbtb.core.exceptions import Unauthorized
from sbtb.models import User
from sbtb.user.service import user_service

_optional_bearer = HTTPBearer(auto_error=False)


async def _optional_jwt_result(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
) -> JWTValidationResult | None:
    """Like validate_jwt_token but returns None if no credentials are present."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    return await validate_jwt_token(token=credentials.credentials)


async def get_current_user(
    session: DbSession,
    jwt_result: JWTValidationResult = Depends(validate_jwt_token),
) -> User:
    if not jwt_result or not jwt_result.is_valid or not jwt_result.payload:
        raise Unauthorized(message="Invalid or expired token")
    return await user_service.get_or_provision_from_jwt(session=session, payload=jwt_result.payload)


async def get_optional_current_user(
    session: DbSession,
    jwt_result: JWTValidationResult | None = Depends(_optional_jwt_result),
) -> User | None:
    if jwt_result is None or not jwt_result.is_valid or not jwt_result.payload:
        return None
    return await user_service.get_or_provision_from_jwt(session=session, payload=jwt_result.payload)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalCurrentUserDep = Annotated[User | None, Depends(get_optional_current_user)]
