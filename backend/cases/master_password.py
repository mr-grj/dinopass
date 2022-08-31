from crud.master_password import MasterPasswordCRUD
from models.master_password import MasterPasswordModel
from schemas.master_password import MasterPassword


class MasterPasswordCase:
    def __init__(self, master_password_crud: MasterPasswordCRUD) -> None:
        self.master_password_crud = master_password_crud

    async def check_master_password(self, master_password: str) -> MasterPassword:
        return await self.master_password_crud.check_master_password(master_password)

    async def create_master_password(self, master_password: str) -> MasterPassword:
        return await self.master_password_crud.create_master_password(master_password)
