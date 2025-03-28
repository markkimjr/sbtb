import sys
import logging
import colorlog

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sbtb import routes
from sbtb.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
colored_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] - %(filename)s:%(funcName)s:%(lineno)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(colored_formatter)
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

