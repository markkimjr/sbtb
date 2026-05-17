import logging
import logging.config
from typing import Any, Generic, TypeVar

import fastapi
import rich
import sentry_sdk
import starlette
import structlog
import uvicorn
from asgi_correlation_id import correlation_id
from rich.traceback import install as install_rich_traceback
from structlog.dev import ConsoleRenderer, RichTracebackFormatter

from sbtb.core.config import settings

Logger = structlog.stdlib.BoundLogger
RendererType = TypeVar("RendererType")


def add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add correlation ID from asgi_correlation_id to log events."""
    cid = correlation_id.get()
    event_dict["correlation_id"] = cid if cid else "-"
    return event_dict


class CustomLogging(Generic[RendererType]):
    """Logging configurator for structlog and stdlib logging."""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    @classmethod
    def get_level(cls) -> str:
        return settings.LOG_LEVEL

    @classmethod
    def get_processors(cls) -> list[Any]:
        return [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.LINENO]
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            add_correlation_id,
            cls.timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    @classmethod
    def get_renderer(cls) -> RendererType:
        raise NotImplementedError()

    @classmethod
    def get_foreign_pre_chain(cls) -> list[Any]:
        """Processors for stdlib loggers routed through structlog."""
        return [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.LINENO]
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            add_correlation_id,
            cls.timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]

    @classmethod
    def configure_stdlib(cls) -> None:
        level = cls.get_level()
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {
                    "sbtb": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            cls.get_renderer(),
                        ],
                        "foreign_pre_chain": cls.get_foreign_pre_chain(),
                    },
                },
                "handlers": {
                    "default": {
                        "level": level,
                        "class": "logging.StreamHandler",
                        "formatter": "sbtb",
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["default"],
                        "level": level,
                        "propagate": False,
                    },
                    "sbtb": {
                        "handlers": ["default"],
                        "level": "DEBUG",
                        "propagate": False,
                    },
                    # Suppress noisy uvicorn access logs
                    "uvicorn.access": {
                        "handlers": [],
                        "level": "WARNING",
                        "propagate": False,
                    },
                    # Propagate third-party loggers to the root logger
                    **{
                        logger_name: {
                            "handlers": [],
                            "propagate": True,
                        }
                        for logger_name in [
                            "uvicorn",
                            "uvicorn.error",
                            "sqlalchemy",
                            "httpx",
                            "httpcore",
                            "asgi_correlation_id",
                        ]
                    },
                },
            }
        )

    @classmethod
    def configure_structlog(cls) -> None:
        structlog.configure_once(
            processors=cls.get_processors(),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @classmethod
    def configure(cls) -> None:
        cls.configure_stdlib()
        cls.configure_structlog()


class Development(CustomLogging[ConsoleRenderer]):
    """Development logging with colorized console output and rich tracebacks."""

    @classmethod
    def get_renderer(cls) -> ConsoleRenderer:
        return ConsoleRenderer(
            colors=True,
            exception_formatter=RichTracebackFormatter(
                show_locals=False,
                width=120,
                suppress=[structlog, starlette, uvicorn, fastapi, sentry_sdk],
            ),
        )

    @classmethod
    def configure(cls) -> None:
        install_rich_traceback(
            show_locals=False,
            width=120,
            suppress=[structlog, starlette, uvicorn, rich, fastapi, sentry_sdk],
        )
        super().configure()


class Production(CustomLogging[structlog.processors.JSONRenderer]):
    """Production logging with JSON output for log aggregation systems."""

    @classmethod
    def get_renderer(cls) -> structlog.processors.JSONRenderer:
        return structlog.processors.JSONRenderer(ensure_ascii=False)


def configure_logging() -> None:
    """Configure logging based on ENV environment variable."""
    if "local" in settings.ENV.lower():
        Development.configure()
    else:
        Production.configure()
