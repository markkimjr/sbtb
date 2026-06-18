from typing import Annotated

from fastapi import Depends

from sbtb.auth.dependencies import CurrentUserDep
from sbtb.core.exceptions import NotPermitted
from sbtb.models import User


async def superuser_only(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise NotPermitted(message="Superuser access required")
    return current_user


SuperuserDep = Annotated[User, Depends(superuser_only)]
