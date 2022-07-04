from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings


class APISettings(BaseSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Dinopass API Service"
    version: str = "0.1.0"

    # Custom settings
    disable_docs: bool = False
    db_filepath: str = str(Path(__file__).parent.parent / 'db' / 'dinopass.db')

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        fastapi_kwargs: Dict[str, Any] = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
            "project_path": self.db_filepath,
        }
        if self.disable_docs:
            fastapi_kwargs.update({
                "docs_url": None,
                "openapi_url": None,
                "redoc_url": None
            })

        return fastapi_kwargs

    class Config:
        validate_assignment = True


@lru_cache()
def get_api_settings() -> APISettings:
    return APISettings()


settings = APISettings()
