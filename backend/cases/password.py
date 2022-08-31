from crud.password import PasswordCRUD
from schemas.password import Password


class PasswordCase:
    def __init__(self, password_crud: PasswordCRUD) -> None:
        self.password_crud = password_crud

    async def get_password(self, key_derivation: str, password_name: str) -> Password:
        return await self.password_crud.get_password(key_derivation, password_name)

    async def create_password(
        self, key_derivation: str, password: Password
    ) -> Password:
        return await self.password_crud.create_password(key_derivation, password)

    async def get_passwords(self, key_derivation: str) -> list[Password]:
        return await self.password_crud.get_passwords(key_derivation)
