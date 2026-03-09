from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from api.rate_limit import limiter
from api.routes import make_api_exceptions, make_api_router
from config.api_settings import get_api_settings

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def get_application() -> FastAPI:
    settings = get_api_settings()
    server = FastAPI(**settings.fastapi_kwargs)

    server.state.limiter = limiter
    server.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    server.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Content-Type", "x-dino-key-derivation"],
    )

    @server.middleware("http")
    async def add_security_headers(request: Request, call_next) -> JSONResponse:
        response = await call_next(request)
        response.headers.update(_SECURITY_HEADERS)
        return response

    if not settings.disable_docs:
        @server.get("/", include_in_schema=False)
        def redirect_to_docs() -> RedirectResponse:
            return RedirectResponse(settings.docs_url)

    server.include_router(make_api_router(), prefix="/api")
    make_api_exceptions(server)

    return server


app = get_application()
