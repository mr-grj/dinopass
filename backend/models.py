from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Integer,
    LargeBinary,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass


class MasterPasswordModel(BaseModel):
    __tablename__ = "master_password"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
    deleted: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=None)

    salt: Mapped[bytes] = mapped_column(LargeBinary)
    hash_key: Mapped[str] = mapped_column(String)


class PasswordModel(BaseModel):
    __tablename__ = "passwords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
    deleted: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=None)

    password_name: Mapped[str] = mapped_column(String, unique=True)
    username: Mapped[str | None] = mapped_column(String)
    password_value: Mapped[bytes] = mapped_column(LargeBinary)
    description: Mapped[str | None] = mapped_column(String)
    backed_up: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )


class SettingsModel(BaseModel):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    inactivity_ms: Mapped[int] = mapped_column(Integer, server_default="120000")
    warn_before_ms: Mapped[int] = mapped_column(Integer, server_default="60000")
    hidden_ms: Mapped[int] = mapped_column(Integer, server_default="60000")
    debounce_ms: Mapped[int] = mapped_column(Integer, server_default="1000")
    clipboard_clear_ms: Mapped[int] = mapped_column(Integer, server_default="30000")
