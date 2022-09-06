from fastapi import APIRouter, FastAPI

from api.v1.endpoints import master_password, password
from api.v1.exceptions import internal_error_handler
from api.v1.responses import inject_responses


def make_api_router() -> APIRouter:
    api_router = APIRouter()

    api_router.responses = inject_responses()

    api_router.include_router(master_password.router, prefix="/master_password")
    api_router.include_router(password.router, prefix="/password")

    return api_router


def make_api_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(Exception, internal_error_handler)
