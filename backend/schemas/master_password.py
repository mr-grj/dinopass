from pydantic import BaseModel


class MasterPassword(BaseModel):
    """
    Master Password data.
    """
    key_derivation: str


class MasterPasswordPayload(BaseModel):
    master_password: str


class UpdateMasterPasswordPayload(BaseModel):
    master_password: str
    new_master_password: str
