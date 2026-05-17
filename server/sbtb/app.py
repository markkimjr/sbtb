import contextlib
import logging
from collections.abc import AsyncIterator
from uuid import uuid4

import sentry_sdk
import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration

from sbtb.core.config import settings
from sbtb.core.exceptions import add_exception_handlers
from sbtb.core.logging import configure_logging
from sbtb.core.util import is_valid_uuid4
from sbtb.routes import api_router

configure_logging()
logger = structlog.get_logger(__name__)

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment=settings.ENV,
    )
    logger.info("Sentry SDK initialized.")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("FastAPI sbtb app running...")
    yield
    logger.info("FastAPI sbtb app shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Saved By The Bell",
        description="Boxing fight notification service",
        version=settings.VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
        allow_headers=settings.CORS_ALLOWED_HEADERS,
    )

    app.add_middleware(
        CorrelationIdMiddleware,  # type: ignore
        header_name="X-Request-ID",
        update_request_header=True,
        generator=lambda: uuid4().hex,
        validator=is_valid_uuid4,
        transformer=lambda a: a,
    )

    add_exception_handlers(app=app)

    app.include_router(api_router)

    if settings.SENTRY_DSN and "local" not in settings.ENV.lower():
        app.add_middleware(SentryAsgiMiddleware)

    return app


app = create_app()
