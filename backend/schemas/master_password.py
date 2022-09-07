from pydantic import BaseModel


class MasterPassword(BaseModel):
    master_password: str


class MasterPasswordCheck(BaseModel):
    """
    Master Password data schema used as a response after
    checking if a master password is valid or not.
    """
    valid: bool


class MasterPasswordCreate(BaseModel):
    """
    Master Password data schema used as a response after
    creating a new master password.
    """
    created: bool
    detail: str


class MasterPasswordUpdate(BaseModel):
    """
    Master Password data schema used as a response after
    updating a master password.
    """
    updated: bool
    detail: str


class MasterPasswordUpdatePayload(BaseModel):
    master_password: str
    new_master_password: str
