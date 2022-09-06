from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from api.routes import make_api_router, make_api_exceptions
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

    add_routes(server)
    add_exceptions(server)

    return server


def add_exceptions(application: FastAPI) -> None:
    """
    Add custom exceptions for this app.
    """
    make_api_exceptions(application)


def add_routes(server: FastAPI) -> None:
    server.include_router(make_api_router(), prefix="/api")


app = get_application()
