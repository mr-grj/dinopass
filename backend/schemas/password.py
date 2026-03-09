from typing import Optional

from pydantic import BaseModel


class Password(BaseModel):
    password_name: str
    password_value: str
    description: Optional[str] = None


class PasswordCreate(BaseModel):
    created: bool
    detail: str


class PasswordUpdate(BaseModel):
    updated: bool
    detail: str


class PasswordDelete(BaseModel):
    deleted: bool
    detail: str


class PasswordUpdatePayload(BaseModel):
    password: Password
    new_password: Password
