from typing import Annotated

from fastapi import Depends

from sbtb.auth.jwt import JWTValidationResult, validate_jwt_token
from sbtb.core.database.session import DbSession
from sbtb.core.exceptions import NotPermitted, Unauthorized
from sbtb.models import User
from sbtb.user.repository import UserRepository


async def superuser_only(
    session: DbSession,
    jwt_result: JWTValidationResult = Depends(validate_jwt_token),
) -> User:
    if not jwt_result or not jwt_result.is_valid:
        raise Unauthorized(message="Invalid or expired token")

    user_id = jwt_result.payload.get("sub")

    user_repo = UserRepository.from_session(session=session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise Unauthorized(message="User not found")
    if not user.is_superuser:
        raise NotPermitted(message="Superuser access required")
    return user


SuperuserDep = Annotated[User, Depends(superuser_only)]
