from typing import AsyncGenerator, Callable, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import BaseCRUD
from crud.session import AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_crud(crud_type: Type[BaseCRUD]) -> Callable:
    def _get_crud(session: AsyncSession = Depends(get_session)) -> BaseCRUD:
        return crud_type(session)

    return _get_crud
