from urllib.parse import quote

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import get_db_settings

_settings = get_db_settings()

engine = create_async_engine(
    f"postgresql+asyncpg://{_settings.postgres_user}:{quote(_settings.postgres_password)}"
    f"@{_settings.postgres_host}:{_settings.postgres_port}/{_settings.postgres_db}",
    pool_pre_ping=True,
    pool_size=5,
    pool_recycle=_settings.pool_recycle,
)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
