import sys

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from api.v1.endpoints.master_password import router as master_password_router
from api.v1.endpoints.password import router as passwords_router
from config.api_settings import get_api_settings


def get_application() -> FastAPI:
    api_settings = get_api_settings()

    server = FastAPI(**api_settings.fastapi_kwargs)
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @server.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(api_settings.docs_url)

    get_routers(server)

    return server


def get_routers(server: FastAPI) -> None:
    server.include_router(master_password_router, prefix="/api")
    server.include_router(passwords_router, prefix="/api")


app = get_application()
