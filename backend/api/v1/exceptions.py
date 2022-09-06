from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from schemas.exceptions_responses import InternalServerErrorResponseSchema, DetailSchema


class Forbidden(Exception):
    """
    Handle HTTP Forbidden (403) exceptions.
    """


class NotFound(Exception):
    """
    Handle HTTP Not Found (404) exceptions.
    """


class TypesMismatchError(Exception):
    """
    Handle HTTP Mismatch (400) exceptions.
    """


def handle_forbidden(func: Callable) -> Callable:
    """
    Decorator for endpoints to handle Forbidden exceptions.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Forbidden as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )

    return wrapper


def handle_mismatch(func: Callable) -> Callable:
    """
    Decorator for endpoints to trigger TypesMismatchError exception
    if expected type of input argument does not match with actual.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except (TypeError, TypesMismatchError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    return wrapper


def handle_not_found(func: Callable) -> Callable:
    """
    Decorator for endpoints to trigger NotFound exception
    if something was not found in database.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except NotFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    return wrapper


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    This handler is launched automatically for each endpoint.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=InternalServerErrorResponseSchema(
            detail=DetailSchema(message=str(exc), error_type=str(type(exc)))
        ).dict(),
    )
