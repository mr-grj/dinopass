from crud.base import BaseCRUD
from helpers import generate_hash_key, generate_key_derivation
from models.master_password import MasterPasswordModel


class MasterPasswordCRUD(BaseCRUD):
    async def check_master_password(self, master_password: str):
        hash_key = generate_hash_key(master_password)
        master_password_model = await self.session.get(
            MasterPasswordModel,
            hash_key
        )
        key_derivation = generate_key_derivation(
            master_password_model.salt,
            master_password
        )
        if hash_key == master_password_model.hash_key:
            return {"key_derivation": key_derivation}
        return "Bad something"
