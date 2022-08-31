from typing import List

from pydantic import BaseModel


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
