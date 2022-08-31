from functools import lru_cache

from pydantic import BaseSettings


class DBSettings(BaseSettings):
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "dinopass"
    postgres_user: str = "dinopass"
    postgres_password: str = "dinopass"
    pool_recycle: int = 900

    class Config:
        env_file = ".db.env"


@lru_cache()
def get_db_settings() -> DBSettings:
    return DBSettings()


db_settings = DBSettings()
