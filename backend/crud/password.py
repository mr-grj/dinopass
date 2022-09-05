from sqlalchemy import select

from crud.base import BaseCRUD, DBNotFoundError, DBBadEncryptionKeyError
from helpers import decrypt, encrypt
from models.password import PasswordModel
from schemas.password import Password


class PasswordCRUD(BaseCRUD):
    async def get_password(self, key_derivation: str, password_name: str) -> Password:
        query = (
            select(PasswordModel)
            .where(PasswordModel.password_name == password_name)
        )
        password_model = (
            await self.session.execute(query)
        ).scalar()
        if not password_model:
            raise DBNotFoundError(f"No password matches {password_name}.")

        decrypted_value = decrypt(key_derivation, password_model.password_value)
        if not decrypted_value:
            raise DBBadEncryptionKeyError(
                f"Invalid key_derivation for {password_model.password_name}."
            )

        return Password(
            password_name=password_model.password_name,
            password_value=decrypted_value,
            description=password_model.description,
        )

    async def create_password(
        self, key_derivation: str, password: Password
    ) -> Password:
        encrypted_value = encrypt(key_derivation, password.password_value)
        password_model = PasswordModel(
            password_name=password.password_name,
            password_value=encrypted_value,
            description=password.description
        )
        self.session.add(password_model)
        await self.session.flush()
        return Password(
            password_name=password.password_name,
            password_value=password.password_value,
            description=password.description
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
