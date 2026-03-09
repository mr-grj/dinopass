import os

from sqlalchemy import select
from starlette.datastructures import Headers

from api.v1.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from helpers import (
    decrypt,
    encrypt,
    generate_key_derivation,
    hash_master_password,
    verify_master_password,
)
from models.master_password import MasterPasswordModel
from models.password import PasswordModel
from schemas.master_password import MasterPasswordCheck, MasterPasswordCreate, MasterPasswordUpdate


class MasterPasswordCRUD(BaseCRUD):

    async def is_initialized(self) -> bool:
        result = await self.session.execute(select(MasterPasswordModel).limit(1))
        return result.scalar() is not None

    async def _get_model(self) -> MasterPasswordModel:
        result = await self.session.execute(select(MasterPasswordModel).limit(1))
        model = result.scalar()
        if not model:
            raise NotFound("No master password found.")
        return model

    async def check_master_password(self, master_password: str) -> MasterPasswordCheck:
        model = await self._get_model()
        if not verify_master_password(master_password, model.hash_key):
            return MasterPasswordCheck(valid=False)
        key_derivation = generate_key_derivation(model.salt, master_password)
        return MasterPasswordCheck(valid=True, key_derivation=key_derivation.decode())

    async def create_master_password(self, master_password: str) -> MasterPasswordCreate:
        if await self.is_initialized():
            raise Forbidden("Master password already exists.")
        salt = os.urandom(16)
        key_derivation = generate_key_derivation(salt, master_password)
        self.session.add(MasterPasswordModel(salt=salt, hash_key=hash_master_password(master_password)))
        await self.session.flush()
        return MasterPasswordCreate(
            created=True,
            detail="Master password created successfully.",
            key_derivation=key_derivation.decode(),
        )

    async def update_master_password(
        self, master_password: str, new_master_password: str, headers: Headers
    ) -> MasterPasswordUpdate:
        model = await self._get_model()
        if not verify_master_password(master_password, model.hash_key):
            raise Forbidden("Current master password is incorrect.")

        key_derivation = headers.get("x-dino-key-derivation")
        if not key_derivation:
            raise Forbidden("Key derivation is missing.")

        new_salt = os.urandom(16)
        new_key_derivation = generate_key_derivation(new_salt, new_master_password)

        passwords = (
            await self.session.execute(select(PasswordModel).order_by(PasswordModel.password_name))
        ).scalars()

        for pwd in passwords:
            decrypted = decrypt(key_derivation, pwd.password_value)
            if decrypted is None:
                raise TypesMismatchError(f"Could not decrypt password '{pwd.password_name}'.")
            pwd.password_value = encrypt(new_key_derivation, decrypted.encode())
            self.session.add(pwd)

        model.salt = new_salt
        model.hash_key = hash_master_password(new_master_password)
        self.session.add(model)
        await self.session.flush()

        return MasterPasswordUpdate(updated=True, detail="Master password updated successfully.")
