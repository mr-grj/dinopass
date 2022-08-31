from sqlalchemy import select

from backend.crud.base import BaseCRUD, DBNotFoundError
from backend.models.master_password import MasterPasswordModel
from backend.schemas.master_password import (
    MasterPasswordContext,
    MasterPasswordPayload,
    MasterPasswordResponse,
)


class MasterPasswordCRUD(BaseCRUD):
    async def get_master_password(self, password_name: str):
        master_password = await self.session.get(MasterPasswordModel, password_name)
        if not master_password:
            raise DBNotFoundError(f"Master password with {user_id} could not be found.")
