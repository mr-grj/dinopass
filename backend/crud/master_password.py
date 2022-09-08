import os

from sqlalchemy import select
from starlette.datastructures import MutableHeaders

from api.v1.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from helpers import generate_hash_key, generate_key_derivation, encrypt, decrypt
from models.master_password import MasterPasswordModel
from models.password import PasswordModel
from schemas.master_password import (
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPasswordUpdate,
)


class MasterPasswordCRUD(BaseCRUD):

    async def _get_master_password_model(self, hash_key) -> MasterPasswordModel:
        master_password_model = (
            await self.session.execute(
                select(MasterPasswordModel).where(
                    MasterPasswordModel.hash_key == hash_key
                )
            )
        ).scalar()
        if not master_password_model:
            raise NotFound("No master password matches.")
        return master_password_model

    async def check_master_password(
        self, master_password: str, headers: MutableHeaders
    ) -> MasterPasswordCheck:
        hash_key = generate_hash_key(master_password)
        master_password_model = await self._get_master_password_model(hash_key)

        key_derivation = generate_key_derivation(
            master_password_model.salt,
            master_password
        )
        if hash_key == master_password_model.hash_key:
            headers["x-dino-key-derivation"] = key_derivation.decode()
            return MasterPasswordCheck(valid=True)

        return MasterPasswordCheck(valid=False)

    async def create_master_password(
        self, master_password: str, headers: MutableHeaders
    ) -> MasterPasswordCreate:
        hash_key = generate_hash_key(master_password)

        await self._get_master_password_model(hash_key)

        salt = os.urandom(16)
        key_derivation = generate_key_derivation(salt, master_password)
        master_password_model = MasterPasswordModel(salt=salt, hash_key=hash_key)

        self.session.add(master_password_model)
        await self.session.flush()

        headers["x-dino-key-derivation"] = key_derivation.decode()
        return MasterPasswordCreate(
            created=True,
            detail="Master password has been successfully created."
        )

    async def update_master_password(
        self, master_password: str, new_master_password: str, headers: MutableHeaders
    ) -> MasterPasswordUpdate:
        new_salt = os.urandom(16)
        new_key_derivation = generate_key_derivation(
            new_salt,
            new_master_password
        )

        for password in (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars():
            decrypted_value = decrypt(
                headers["x-dino-key-derivation"],
                password.password_value
            )
            if not decrypted_value:
                raise TypesMismatchError(
                    f"Invalid key_derivation for {password.password_name}."
                )

            # encrypt password with new key
            encrypted_value = encrypt(new_key_derivation, decrypted_value)
            password.password_value = encrypted_value
            self.session.add(password)
            await self.session.flush()

        hash_key_current_password = generate_hash_key(master_password)

        master_password_model = await self._get_master_password_model(
            hash_key_current_password
        )
        hash_key_new_password = generate_hash_key(new_master_password)

        master_password_model.salt = new_salt
        master_password_model.hash_key = hash_key_new_password

        self.session.add(master_password_model)
        await self.session.flush()

        return MasterPasswordUpdate(
            updated=True,
            detail="Master password has been successfully updated."
        )
