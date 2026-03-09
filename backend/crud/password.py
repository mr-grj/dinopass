from sqlalchemy import select
from starlette.datastructures import Headers

from api.v1.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from helpers import decrypt, encrypt
from models.master_password import MasterPasswordModel
from models.password import PasswordModel
from schemas.password import Password, PasswordCreate, PasswordDelete, PasswordUpdate


class PasswordCRUD(BaseCRUD):

    @staticmethod
    def _get_key_derivation(headers: Headers) -> str:
        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")
        return key_derivation

    async def _check_master_password_exists(self) -> None:
        result = await self.session.execute(select(MasterPasswordModel).limit(1))
        if result.scalar() is None:
            raise Forbidden("No master password set.")

    async def _get_password_model(self, password_name: str) -> PasswordModel:
        result = (
            await self.session.execute(
                select(PasswordModel).where(PasswordModel.password_name == password_name)
            )
        ).scalar()
        if not result:
            raise NotFound(f"No password found for '{password_name}'.")
        return result

    def _decrypt_or_raise(self, key_derivation: str, model: PasswordModel) -> str:
        decrypted = decrypt(key_derivation, model.password_value)
        if decrypted is None:
            raise TypesMismatchError(f"Invalid key for '{model.password_name}'.")
        return decrypted

    async def get_passwords(self, headers: Headers) -> list[Password]:
        await self._check_master_password_exists()
        key_derivation = self._get_key_derivation(headers)
        passwords = (
            await self.session.execute(select(PasswordModel).order_by(PasswordModel.password_name))
        ).scalars()
        return [
            Password(
                password_name=p.password_name,
                password_value=self._decrypt_or_raise(key_derivation, p),
                description=p.description,
            )
            for p in passwords
        ]

    async def get_password(self, password_name: str, headers: Headers) -> Password:
        await self._check_master_password_exists()
        key_derivation = self._get_key_derivation(headers)
        model = await self._get_password_model(password_name)
        return Password(
            password_name=model.password_name,
            password_value=self._decrypt_or_raise(key_derivation, model),
            description=model.description,
        )

    async def create_password(self, password: Password, headers: Headers) -> PasswordCreate:
        await self._check_master_password_exists()
        key_derivation = self._get_key_derivation(headers)

        existing = (
            await self.session.execute(
                select(PasswordModel).where(PasswordModel.password_name == password.password_name)
            )
        ).scalar()
        if existing:
            raise TypesMismatchError("A password with that name already exists.")

        self.session.add(
            PasswordModel(
                password_name=password.password_name,
                password_value=encrypt(key_derivation, password.password_value.encode()),
                description=password.description,
            )
        )
        await self.session.flush()
        return PasswordCreate(created=True, detail="Password created successfully.")

    async def update_password(
        self, password: Password, new_password: Password, headers: Headers
    ) -> PasswordUpdate:
        await self._check_master_password_exists()
        key_derivation = self._get_key_derivation(headers)
        model = await self._get_password_model(password.password_name)

        if model.password_name != new_password.password_name:
            conflict = (
                await self.session.execute(
                    select(PasswordModel).where(PasswordModel.password_name == new_password.password_name)
                )
            ).scalar()
            if conflict:
                raise TypesMismatchError("A password with that name already exists.")
            model.password_name = new_password.password_name

        decrypted = self._decrypt_or_raise(key_derivation, model)
        if decrypted != new_password.password_value:
            model.password_value = encrypt(key_derivation, new_password.password_value.encode())

        if model.description != new_password.description:
            model.description = new_password.description

        self.session.add(model)
        await self.session.flush()
        return PasswordUpdate(updated=True, detail="Password updated successfully.")

    async def delete_password(self, password_name: str, headers: Headers) -> PasswordDelete:
        await self._check_master_password_exists()
        self._get_key_derivation(headers)
        model = await self._get_password_model(password_name)
        await self.session.delete(model)
        await self.session.flush()
        return PasswordDelete(deleted=True, detail="Password deleted successfully.")
