from sqlalchemy import select
from starlette.datastructures import Headers

from api.v1.exceptions import NotFound, TypesMismatchError, Forbidden
from crud.base import BaseCRUD
from helpers import decrypt, encrypt
from models.password import PasswordModel
from schemas.password import Password, PasswordCreate, PasswordUpdate


class PasswordCRUD(BaseCRUD):

    @staticmethod
    def _get_key_derivation(headers: Headers) -> str:
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")
        return key_derivation

    @staticmethod
    def _get_decrypted_password_value(key_derivation: str, password: Password) -> str:
        decrypted_value = decrypt(key_derivation, password.password_value)
        if not decrypted_value:
            raise TypesMismatchError(
                f"Invalid key_derivation for {password.password_name}."
            )
        return decrypted_value

    async def _get_password_model(self, password_name: str) -> PasswordModel:
        password_model = (
            await self.session.execute(
                select(PasswordModel).where(
                    PasswordModel.password_name == password_name
                )
            )
        ).scalar()
        if not password_model:
            raise NotFound(f"No password matches {password_name}.")
        return password_model

    async def get_passwords(self, headers: Headers) -> list[Password]:
        key_derivation = self._get_key_derivation(headers)
        passwords = (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars()

        decrypted_passwords = []
        for password in passwords:
            decrypted_value = self._get_decrypted_password_value(
                key_derivation, password
            )
            password.password_value = decrypted_value.encode("utf8")
            decrypted_passwords.append(password)

        return [
            Password(
                password_name=password.password_name,
                password_value=password.password_value,
                description=password.description,
            ) for password in decrypted_passwords
        ]

    async def get_password(self, password_name: str, headers: Headers) -> Password:
        key_derivation = self._get_key_derivation(headers)
        password_model = await self._get_password_model(password_name)
        password = Password(
            password_name=password_model.password_name,
            password_value=password_model.password_value,
            description=password_model.description,
        )
        decrypted_value = self._get_decrypted_password_value(key_derivation, password)
        password.password_value = decrypted_value
        return password

    async def create_password(
        self, password: Password, headers: Headers
    ) -> PasswordCreate:
        key_derivation = self._get_key_derivation(headers)
        password_model = PasswordModel(
            password_name=password.password_name,
            password_value=encrypt(key_derivation, password.password_value),
            description=password.description
        )
        self.session.add(password_model)
        await self.session.flush()
        return PasswordCreate(
            created=True,
            detail="Password has been successfully created."
        )

    async def update_password(
        self, password: Password, new_password: Password, headers: Headers
    ) -> PasswordUpdate:
        key_derivation = self._get_key_derivation(headers)
        password_model = self._get_password_model(password.password_name)

        if password_model.password_name != new_password.password_name:
            password_model.password_name = new_password.password_name

        if password_model.password_value != new_password.password_value:
            password_model.password_value = encrypt(
                key_derivation,
                password.password_value
            )

        if password_model.description != new_password.description:
            password_model.description = new_password.description

        self.session.add(password_model)
        await self.session.flush()

        return PasswordUpdate(
            updated=True,
            detail="Password has been successfully updated."
        )
