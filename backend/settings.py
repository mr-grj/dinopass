from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def _package_version() -> str:
    try:
        return version("backend")
    except PackageNotFoundError:
        return "0.0.0"


class APISettings(BaseSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "CipherMoth API Service"
    version: str = _package_version()
    disable_docs: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
        if self.disable_docs:
            kwargs.update({"docs_url": None, "openapi_url": None, "redoc_url": None})
        return kwargs

    model_config = {"validate_assignment": True}


class DBSettings(BaseSettings):
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "ciphermoth"
    postgres_user: str = "ciphermoth"
    postgres_password: str = "ciphermoth"
    pool_recycle: int = 900

    model_config = SettingsConfigDict(env_file=".db.env", extra="ignore")


@lru_cache
def get_api_settings() -> APISettings:
    return APISettings()


@lru_cache
def get_db_settings() -> DBSettings:
    return DBSettings()
