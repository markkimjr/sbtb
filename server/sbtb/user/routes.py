from fastapi import APIRouter

from sbtb.auth.dependencies import CurrentUserDep
from sbtb.user.schemas import UserMeRead

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/me",
    response_description="Current authenticated user's profile",
    response_model=UserMeRead,
)
async def get_me(current_user: CurrentUserDep) -> UserMeRead:
    return UserMeRead.model_validate(current_user)
