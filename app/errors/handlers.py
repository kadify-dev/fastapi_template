from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors.exceptions import (
    BaseHTTPException,
    DatabaseError,
    ServerError,
    ValidationError,
)


def get_error_response(request: Request, exc: BaseHTTPException) -> dict:
    error_response = {
        "error": {
            "type": exc.__class__.__name__,
            "message": exc.detail,
            "code": exc.status_code,
        }
    }

    if isinstance(exc, ValidationError):
        error_response["error"]["details"] = getattr(exc, "errors", None)

    return error_response


async def http_exception_handler(
    request: Request, exc: BaseHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=get_error_response(request, exc),
        headers=exc.headers,
    )


async def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "UnexpectedServerError",
                "message": "Internal server error",
                "code": 500,
            }
        },
    )
