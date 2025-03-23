from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse, JSONResponse, Response

from .fighter.routes import router as fighter_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(fighter_router)


@api_router.get("/", response_description="Root", include_in_schema=False)
async def root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Saved By The Bell API"},
        status_code=status.HTTP_200_OK,
    )

@api_router.get("/ping", response_description="Ping", include_in_schema=False)
async def ping() -> Response:
    return PlainTextResponse("pong")

