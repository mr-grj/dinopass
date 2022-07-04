import sys

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from backend.api.routes.master_password import master_password_router
from backend.api.routes.passwords import passwords_router
from backend.api_settings import get_api_settings
from backend.db import ENGINE
from backend import models


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

    server.include_router(master_password_router, prefix="/api")
    server.include_router(passwords_router, prefix="/api")

    @server.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(api_settings.docs_url)

    return server


try:
    models.Base.metadata.create_all(bind=ENGINE)
except Exception as operational_error:
    sys.exit(
        f'Error when connecting to DB: {operational_error}. '
        f'Please make sure you have correctly set up your DB!'
    )

app = get_application()
