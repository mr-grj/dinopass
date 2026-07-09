import logging

from fastapi import (
    Request,
    status,
)
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class TypesMismatchError(Exception):
    pass


def _detail_handler(status_code: int):
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return handler


forbidden_handler = _detail_handler(status.HTTP_403_FORBIDDEN)
not_found_handler = _detail_handler(status.HTTP_404_NOT_FOUND)
mismatch_handler = _detail_handler(status.HTTP_400_BAD_REQUEST)


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )
