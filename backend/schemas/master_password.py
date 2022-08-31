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
