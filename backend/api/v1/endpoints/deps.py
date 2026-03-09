from fastapi import Depends

from api.deps import get_crud
from crud.master_password import MasterPasswordCRUD
from crud.password import PasswordCRUD


def get_master_password_crud(
    crud: MasterPasswordCRUD = Depends(get_crud(MasterPasswordCRUD)),
) -> MasterPasswordCRUD:
    return crud


def get_password_crud(
    crud: PasswordCRUD = Depends(get_crud(PasswordCRUD)),
) -> PasswordCRUD:
    return crud
