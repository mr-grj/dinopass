from sqlalchemy import select

from crud.base import BaseCRUD, DBNotFoundError, DBBadEncryptionKeyError
from helpers import decrypt
from models.password import PasswordModel
from schemas.password import Password


class PasswordCRUD(BaseCRUD):
    async def get_password(self, key_derivation: str, password_name: str) -> Password:
        password = await self.session.get(PasswordModel, password_name)
        if not password:
            raise DBNotFoundError(f"Password with {password_name} could not be found.")

        decrypted_value = decrypt(key_derivation, password.password_value)
        if not decrypted_value:
            raise DBBadEncryptionKeyError(
                f"Invalid key_derivation for {password.password_name}."
            )

        return Password(
            password_name=password.password_name,
            password_value=decrypted_value,
            description=password.description,
        )

    async def get_passwords(self, key_derivation: str) -> list[Password]:
        passwords = (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars()
        decrypted_passwords = []

        for password in passwords:
            decrypted_value = decrypt(key_derivation, password.password_value)
            if not decrypted_value:
                raise DBBadEncryptionKeyError(
                    f"Invalid key_derivation for {password.password_name}."
                )
            password.password_value = decrypted_value
            decrypted_passwords.append(password)

        return [
            Password(
                password_name=password.password_name,
                password_value=password.password_value,
                description=password.description,
            ) for password in decrypted_passwords
        ]

    async def insert_password(self):
        pass
