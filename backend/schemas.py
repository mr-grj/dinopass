from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SimpleDetailSchema(BaseModel):
    detail: str


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


class Password(BaseModel):
    password_name: str = Field(min_length=1, max_length=255)
    password_value: str = Field(min_length=1)
    description: str | None = Field(default=None, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)


class PasswordResponse(Password):
    backed_up: bool


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


class SettingsResponse(BaseModel):
    inactivity_ms: int
    warn_before_ms: int
    hidden_ms: int
    debounce_ms: int
    clipboard_clear_ms: int


class SettingsUpdate(BaseModel):
    inactivity_ms: int = Field(ge=30_000, le=3_600_000)
    warn_before_ms: int = Field(ge=5_000, le=600_000)
    hidden_ms: int = Field(ge=10_000, le=3_600_000)
    debounce_ms: int = Field(ge=100, le=10_000)
    clipboard_clear_ms: int = Field(ge=5_000, le=600_000)


class OnConflict(StrEnum):
    skip = "skip"
    overwrite = "overwrite"


class PasswordImportResult(BaseModel):
    imported: int
    skipped: int
    overwritten: int
    total: int
