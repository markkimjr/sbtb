from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sbtb import routes
from sbtb.core.config import settings
from sbtb.core.logging import logger

cors_allowed_origins = [
    "https://sbtb.io",
    "http://localhost",
    "http://localhost:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI sbtb app running...")
    yield


app = FastAPI(
    title="sbtbd",
    description="Backend for Saved By The Bell",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=cors_allowed_origins, expose_headers=["x-content-range"])
app.include_router(routes.api_router)
