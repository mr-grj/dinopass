from fastapi import APIRouter, FastAPI

from api.endpoints import (
    master_password,
    password,
    settings,
)
from api.exceptions import internal_error_handler
from api.responses import inject_responses


def make_api_router() -> APIRouter:
    api_router = APIRouter()

    api_router.responses = inject_responses()

    api_router.include_router(master_password.router, prefix="/master_password")
    api_router.include_router(password.router, prefix="/passwords")
    api_router.include_router(settings.router, prefix="/settings")

    return api_router


def make_api_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(Exception, internal_error_handler)
