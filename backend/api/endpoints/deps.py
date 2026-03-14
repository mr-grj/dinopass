from collections.abc import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import BaseCRUD
from crud.master_password import MasterPasswordCRUD
from crud.password import PasswordCRUD
from crud.session import AsyncSessionLocal
from crud.settings import SettingsCRUD


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_crud(crud_type: type[BaseCRUD]) -> Callable:
    def _get_crud(session: AsyncSession = Depends(get_session)) -> BaseCRUD:
        return crud_type(session)

    return _get_crud


def get_master_password_crud(
    crud: MasterPasswordCRUD = Depends(get_crud(MasterPasswordCRUD)),
) -> MasterPasswordCRUD:
    return crud


def get_password_crud(
    crud: PasswordCRUD = Depends(get_crud(PasswordCRUD)),
) -> PasswordCRUD:
    return crud


def get_settings_crud(
    crud: SettingsCRUD = Depends(get_crud(SettingsCRUD)),
) -> SettingsCRUD:
    return crud
