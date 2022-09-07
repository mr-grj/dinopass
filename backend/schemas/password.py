from pydantic import BaseModel


class Password(BaseModel):
    password_name: str
    password_value: str | bytes
    description: str


class PasswordCreate(BaseModel):
    """
    Password data schema used as a response after
    creating a new password.
    """
    created: bool
    detail: str


class PasswordUpdate(BaseModel):
    """
    Password data schema used as a response after
    updating a password.
    """
    updated: bool
    detail: str


class PasswordUpdatePayload(BaseModel):
    password: Password
    new_password: Password
