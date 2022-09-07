from sqlalchemy import select
from starlette.datastructures import Headers

from api.v1.exceptions import NotFound, TypesMismatchError, Forbidden
from crud.base import BaseCRUD
from helpers import decrypt, encrypt
from models.password import PasswordModel
from schemas.password import Password, PasswordCreate, PasswordUpdate


class PasswordCRUD(BaseCRUD):

    async def get_passwords(self, headers: Headers) -> list[Password]:
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")
        print("=" * 20)
        print("=" * 20)
        print("=" * 20)
        print("=" * 20)
        print("HERE1")
        passwords = (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars()
        decrypted_passwords = []

        for password in passwords:
            decrypted_value = decrypt(key_derivation, password.password_value)
            if not decrypted_value:
                raise TypesMismatchError(
                    f"Invalid key_derivation for {password.password_name}."
                )
            password.password_value = decrypted_value
            decrypted_passwords.append(password)

        print(decrypted_passwords[0].password_value)
        print(type(decrypted_passwords[0].password_value.encode()))

        return [
            Password(
                password_name=password.password_name,
                password_value=password.password_value,
                description=password.description,
            ) for password in decrypted_passwords
        ]

    async def get_password(self, password_name: str, headers: Headers) -> Password:
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")

        query = (
            select(PasswordModel)
            .where(PasswordModel.password_name == password_name)
        )
        password_model = (
            await self.session.execute(query)
        ).scalar()
        if not password_model:
            raise NotFound(f"No password matches {password_name}.")

        decrypted_value = decrypt(key_derivation, password_model.password_value)
        if not decrypted_value:
            raise TypesMismatchError(
                f"Invalid key_derivation for {password_model.password_name}."
            )

        return Password(
            password_name=password_model.password_name,
            password_value=decrypted_value,
            description=password_model.description,
        )

    async def create_password(
        self, password: Password, headers: Headers
    ) -> PasswordCreate:
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")

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
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")

        query = (
            select(PasswordModel)
            .where(PasswordModel.password_name == password.password_name)
        )
        password_model = (
            await self.session.execute(query)
        ).scalar()
        if not password_model:
            raise NotFound(f"No password matches {password.password_name}.")

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
