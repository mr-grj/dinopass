from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import Forbidden
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


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_master_password_crud(session: SessionDep) -> MasterPasswordCRUD:
    return MasterPasswordCRUD(session)


def get_password_crud(session: SessionDep) -> PasswordCRUD:
    return PasswordCRUD(session)


def get_settings_crud(session: SessionDep) -> SettingsCRUD:
    return SettingsCRUD(session)


MasterPasswordCRUDDep = Annotated[MasterPasswordCRUD, Depends(get_master_password_crud)]
PasswordCRUDDep = Annotated[PasswordCRUD, Depends(get_password_crud)]
SettingsCRUDDep = Annotated[SettingsCRUD, Depends(get_settings_crud)]


def get_key_derivation(
    x_dino_key_derivation: Annotated[str | None, Header()] = None,
) -> str:
    if not x_dino_key_derivation:
        raise Forbidden("Key derivation is missing.")
    return x_dino_key_derivation


KeyDerivationDep = Annotated[str, Depends(get_key_derivation)]


async def require_master_password(crud: MasterPasswordCRUDDep) -> None:
    if not await crud.is_initialized():
        raise Forbidden("No master password set.")
