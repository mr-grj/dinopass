from starlette.datastructures import MutableHeaders

from crud.master_password import MasterPasswordCRUD
from schemas.master_password import (
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPasswordUpdate,
)


class MasterPasswordCase:
    def __init__(self, master_password_crud: MasterPasswordCRUD) -> None:
        self.master_password_crud = master_password_crud

    async def check_master_password(
        self, master_password: str, headers: MutableHeaders
    ) -> MasterPasswordCheck:
        return await self.master_password_crud.check_master_password(
            master_password,
            headers
        )

    async def create_master_password(
        self, master_password: str, headers: MutableHeaders
    ) -> MasterPasswordCreate:
        return await self.master_password_crud.create_master_password(
            master_password,
            headers
        )

    async def update_master_password(
        self, master_password: str, new_master_password: str, headers: MutableHeaders
    ) -> MasterPasswordUpdate:
        return await self.master_password_crud.update_master_password(
            master_password,
            new_master_password,
            headers
        )
