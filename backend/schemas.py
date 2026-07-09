from datetime import datetime
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from validators import normalize_totp_secret, validate_master_password_strength

_MAX_TAGS = 20
_MAX_TAG_LENGTH = 40


class SimpleDetailSchema(BaseModel):
    detail: str


class MasterPassword(BaseModel):
    master_password: str = Field(min_length=1, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)


class MasterPasswordCreatePayload(BaseModel):
    master_password: str = Field(min_length=1, max_length=1024)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("master_password")
    @classmethod
    def _strong(cls, value: str) -> str:
        return validate_master_password_strength(value)


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

    @field_validator("new_master_password")
    @classmethod
    def _strong(cls, value: str) -> str:
        return validate_master_password_strength(value)


class MasterPasswordStatus(BaseModel):
    initialized: bool


class Password(BaseModel):
    password_name: str = Field(min_length=1, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    password_value: str = Field(min_length=1)
    url: str | None = Field(default=None, max_length=2048)
    totp_secret: str | None = Field(default=None, max_length=512)
    description: str | None = Field(default=None, max_length=1024)
    tags: list[str] = Field(default_factory=list, max_length=_MAX_TAGS)
    favorite: bool = False

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("totp_secret")
    @classmethod
    def _normalize_totp(cls, value: str | None) -> str | None:
        return normalize_totp_secret(value)

    @field_validator("tags")
    @classmethod
    def _clean_tags(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for tag in value:
            tag = tag.strip()[:_MAX_TAG_LENGTH].strip()
            if tag and tag not in cleaned:
                cleaned.append(tag)
        return cleaned


class PasswordHistoryEntry(BaseModel):
    value: str
    changed_at: datetime


class PasswordResponse(Password):
    backed_up: bool
    updated: datetime
    password_history: list[PasswordHistoryEntry] = Field(default_factory=list)


class FavoriteUpdatePayload(BaseModel):
    favorite: bool


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
