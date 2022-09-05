from urllib.parse import quote

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models.base import BaseModel
from config.db_settings import db_settings


def create_engine_configuration(
    postgres_host: str,
    postgres_port: int,
    postgres_db: str,
    postgres_user: str,
    postgres_password: str,
    pool_recycle: int = 900,
) -> dict:
    db_url = (
        f"postgresql+asyncpg://{postgres_user}:{quote(postgres_password)}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )
    return {
        f"url": f"{db_url}",
        "pool_pre_ping": True,
        "pool_size": 100,
        "pool_recycle": pool_recycle
    }


engine = create_async_engine(
    **create_engine_configuration(
        db_settings.postgres_host,
        db_settings.postgres_port,
        db_settings.postgres_db,
        db_settings.postgres_user,
        db_settings.postgres_password,
        db_settings.pool_recycle,
    )
)


SessionLocal = sessionmaker(expire_on_commit=False, class_=AsyncSession)
SessionLocal.configure(binds={BaseModel: engine})
