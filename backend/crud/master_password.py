import os

from sqlalchemy import select

from crud.base import BaseCRUD, DBNotFoundError, DBUnableToInsertError
from helpers import generate_hash_key, generate_key_derivation
from models.master_password import MasterPasswordModel
from schemas.master_password import MasterPassword


class MasterPasswordCRUD(BaseCRUD):
    async def check_master_password(self, master_password: str) -> MasterPassword:
        hash_key = generate_hash_key(master_password)
        query = (
            select(MasterPasswordModel)
            .where(MasterPasswordModel.hash_key == hash_key)
        )
        master_password_model = (
            await self.session.execute(query)
        ).scalar()

        if not master_password_model:
            raise DBNotFoundError("No master password matches.")

        key_derivation = generate_key_derivation(
            master_password_model.salt,
            master_password
        )
        if hash_key == master_password_model.hash_key:
            return MasterPassword(key_derivation=key_derivation)

    async def create_master_password(
        self, master_password: str
    ) -> MasterPassword:
        hash_key = generate_hash_key(master_password)
        query = (
            select(MasterPasswordModel).where(MasterPasswordModel.hash_key == hash_key)
        )
        master_password_model = await self.session.execute(query)
        if master_password_model.scalar():
            raise DBUnableToInsertError("Master password already exists.")

        salt = os.urandom(16)
        key_derivation = generate_key_derivation(salt, master_password)
        master_password_model = MasterPasswordModel(
            salt=salt,
            hash_key=hash_key,
        )
        self.session.add(master_password_model)
        await self.session.flush()
        return MasterPassword(key_derivation=key_derivation)
