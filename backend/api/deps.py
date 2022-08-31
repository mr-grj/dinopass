from functools import lru_cache
from typing import AsyncGenerator, Callable, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from crud.base import BaseCRUD
from crud.session import SessionLocal
from config.api_settings import APISettings


async def get_session() -> AsyncGenerator:
    """
    Generator for database sessions with error
    handling build in.
    """
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()


def get_crud(crud_type: Type[BaseCRUD]) -> Callable:
    """
    Instantiates a DAO with a db connection.
    """

    def _get_crud(session: AsyncSession = Depends(get_session)) -> BaseCRUD:
        return crud_type(session)

    return _get_crud


@lru_cache()
def get_api_settings() -> APISettings:
    return APISettings()
