from starlette.datastructures import Headers

from crud.password import PasswordCRUD
from schemas.password import Password, PasswordCreate, PasswordUpdate


class PasswordCase:
    def __init__(self, password_crud: PasswordCRUD) -> None:
        self.password_crud = password_crud

    async def get_password(self, password_name: str, headers: Headers) -> Password:
        return await self.password_crud.get_password(password_name, headers)

    async def create_password(
        self, password: Password, headers: Headers
    ) -> PasswordCreate:
        return await self.password_crud.create_password(password, headers)

    async def get_passwords(self, headers: Headers) -> list[Password]:
        return await self.password_crud.get_passwords(headers)

    async def update_password(
        self, password: Password, new_password: Password, headers: Headers
    ) -> PasswordUpdate:
        return await self.password_crud.update_password(password, new_password, headers)
