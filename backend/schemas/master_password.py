from pydantic import BaseModel, ConfigDict, Field


class MasterPassword(BaseModel):
    master_password: str = Field(min_length=1, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)


class MasterPasswordCheck(BaseModel):
    valid: bool
    key_derivation: str | None = None


class MasterPasswordCreate(BaseModel):
    created: bool
    detail: str
    key_derivation: str


class MasterPasswordUpdate(BaseModel):
    updated: bool
    detail: str


class MasterPasswordUpdatePayload(BaseModel):
    master_password: str = Field(min_length=1, max_length=1024)
    new_master_password: str = Field(min_length=1, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)


class MasterPasswordStatus(BaseModel):
    initialized: bool
