from typing import Optional

from pydantic import BaseModel


class MasterPassword(BaseModel):
    master_password: str


class MasterPasswordCheck(BaseModel):
    valid: bool
    key_derivation: Optional[str] = None


class MasterPasswordCreate(BaseModel):
    created: bool
    detail: str
    key_derivation: str


class MasterPasswordUpdate(BaseModel):
    updated: bool
    detail: str


class MasterPasswordUpdatePayload(BaseModel):
    master_password: str
    new_master_password: str


class MasterPasswordStatus(BaseModel):
    initialized: bool
