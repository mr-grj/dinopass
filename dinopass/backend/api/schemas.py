from typing import List
from pydantic import BaseModel


class MasterPasswordContext(BaseModel):
    key_derivation: str


class MasterPasswordPayload(BaseModel):
    master_password: str

    class Config:
        orm_mode = True


class MasterPasswordResponse(BaseModel):
    msg: str
    status_code: int
    context: MasterPasswordContext = {}

    class Config:
        orm_mode = True


class Password(BaseModel):
    password_name: str
    password_value: str
    description: str

    class Config:
        orm_mode = True


class PasswordsResponse(BaseModel):
    status_code: int
    msg: str

    passwords: List[Password] = []

    class Config:
        orm_mode = True
