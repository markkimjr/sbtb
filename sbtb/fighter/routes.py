from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse, JSONResponse, Response

from .schemas import FighterSchema

from sbtb.database.session import DbSession

router = APIRouter(prefix="/fighter")

@router.get("/",
            response_description="Fighter Root",
            include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


# create fighter route (post)
@router.post("/",
             response_description="Create a new fighter",
             response_model=FighterSchema,
             status_code=status.HTTP_201_CREATED,
             tags=["fighters"])
async def create_fighter(fighter: FighterSchema, db: DbSession):
    pass
