from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Password(BaseModel):
    password_name: str = Field(min_length=1, max_length=255)
    password_value: str = Field(min_length=1)
    description: Optional[str] = Field(default=None, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)


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
