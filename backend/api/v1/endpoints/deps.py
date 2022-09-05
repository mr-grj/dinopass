from fastapi import Depends

from api.deps import get_crud
from cases.master_password import MasterPasswordCase
from crud.master_password import MasterPasswordCRUD
from cases.password import PasswordCase
from crud.password import PasswordCRUD


async def master_password_case(
    master_password_crud: MasterPasswordCRUD = Depends(get_crud(MasterPasswordCRUD))
) -> MasterPasswordCase:
    return MasterPasswordCase(master_password_crud=master_password_crud)


async def password_case(
    password_crud: PasswordCRUD = Depends(get_crud(PasswordCRUD))
) -> PasswordCase:
    return PasswordCase(password_crud=password_crud)
