import sys
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sbtb import routes
from sbtb.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] - %(filename)s:%(funcName)s:%(lineno)s - %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

cors_allowed_origins = [
    "https://sbtb.io",
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI(
    title="sbtbd",
    description="Backend for Saved By The Bell",
    version=settings.VERSION,
)


async def on_startup() -> None:
    logger.info("FastAPI sbtb app running...")


app.add_middleware(CORSMiddleware, allow_origins=cors_allowed_origins, expose_headers=["x-content-range"])
app.add_event_handler("startup", on_startup)
app.include_router(routes.api_router)

