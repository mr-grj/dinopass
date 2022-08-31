from pydantic import BaseModel


class Password(BaseModel):
    password_name: str
    password_value: str
    description: str
