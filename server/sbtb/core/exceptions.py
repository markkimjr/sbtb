from collections.abc import Sequence
from typing import Any, Literal, LiteralString, NotRequired, TypedDict

import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, create_model
from pydantic_core import ErrorDetails, InitErrorDetails, PydanticCustomError
from pydantic_core import ValidationError as PydanticValidationError

logger = structlog.get_logger(__name__)


class SBTBError(Exception):
    """
    Base exception class for all errors raised by SBTB.

    A custom exception handler for FastAPI takes care
    of catching and returning a proper HTTP error from them.

    Args:
        message: The error message that'll be displayed to the user.
        status_code: The status code of the HTTP response. Defaults to 500.
        code: Machine-readable error code the client can switch on.
        headers: Additional headers to be included in the response.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.headers = headers

    @classmethod
    def schema(cls) -> type[BaseModel]:
        error_literal = Literal[cls.__name__]  # type: ignore

        return create_model(
            cls.__name__,
            error=(error_literal, Field(examples=[cls.__name__])),
            detail=(str, ...),
        )


class BadRequest(SBTBError):
    def __init__(
        self,
        message: str = "Bad request",
        status_code: int = 400,
        code: str | None = "bad_request",
    ) -> None:
        super().__init__(message, status_code, code)


class NotPermitted(SBTBError):
    def __init__(
        self,
        message: str = "Not permitted",
        status_code: int = 403,
        code: str | None = "not_permitted",
    ) -> None:
        super().__init__(message, status_code, code)


class Unauthorized(SBTBError):
    def __init__(
        self,
        message: str = "Unauthorized",
        status_code: int = 401,
        code: str | None = "unauthorized",
    ) -> None:
        super().__init__(
            message,
            status_code,
            code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InternalServerError(SBTBError):
    def __init__(
        self,
        message: str = "Internal Server Error",
        status_code: int = 500,
        code: str | None = "internal_server_error",
    ) -> None:
        super().__init__(message, status_code, code)


class ResourceNotFound(SBTBError):
    def __init__(
        self,
        message: str = "Not found",
        status_code: int = 404,
        code: str | None = "resource_not_found",
    ) -> None:
        super().__init__(message, status_code, code)


class ValidationError(TypedDict):
    loc: tuple[int | str, ...]
    msg: LiteralString
    type: LiteralString
    input: Any
    ctx: NotRequired[dict[str, Any]]


class SBTBRequestValidationError(SBTBError):
    def __init__(self, errors: Sequence[ValidationError]) -> None:
        self._errors = errors

    def errors(self) -> list[ErrorDetails]:
        pydantic_errors: list[InitErrorDetails] = []
        for error in self._errors:
            pydantic_errors.append(
                {
                    "type": PydanticCustomError(error["type"], error["msg"]),
                    "loc": error["loc"],
                    "input": error["input"],
                }
            )
        pydantic_error = PydanticValidationError.from_exception_data(self.__class__.__name__, pydantic_errors)
        return pydantic_error.errors()


async def sbtb_exception_handler(request: Request, exc: SBTBError) -> JSONResponse:
    logger.error("exception occurred", message=exc.message, exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "code": exc.code, "detail": exc.message},
        headers=exc.headers,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError | SBTBRequestValidationError
) -> JSONResponse:
    logger.error("request validation error", error=str(exc), exc_info=exc)
    return JSONResponse(
        status_code=422,
        content={"error": type(exc).__name__, "detail": jsonable_encoder(exc.errors())},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception occurred", exc_info=exc)
    return await sbtb_exception_handler(request, InternalServerError(message=str(exc)))


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,  # type: ignore
    )
    app.add_exception_handler(
        SBTBRequestValidationError,
        request_validation_exception_handler,  # type: ignore
    )
    app.add_exception_handler(SBTBError, sbtb_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore
