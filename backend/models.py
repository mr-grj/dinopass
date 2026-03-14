from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    LargeBinary,
    String,
    func,
)
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class MasterPasswordModel(BaseModel):
    __tablename__ = "master_password"

    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted: TIMESTAMP | None = Column(TIMESTAMP, nullable=True, default=None)

    salt = Column(LargeBinary, nullable=False)
    hash_key = Column(String, nullable=False)
    kdf_version = Column(Integer, nullable=False, server_default="1")


class PasswordModel(BaseModel):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted: TIMESTAMP | None = Column(TIMESTAMP, nullable=True, default=None)

    password_name = Column(String, nullable=False, unique=True)
    password_value = Column(LargeBinary, nullable=False)
    description = Column(String, nullable=True)
    backed_up = Column(Boolean, nullable=False, default=False, server_default="false")


class SettingsModel(BaseModel):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    inactivity_ms = Column(Integer, nullable=False, server_default="120000")
    warn_before_ms = Column(Integer, nullable=False, server_default="60000")
    hidden_ms = Column(Integer, nullable=False, server_default="60000")
    debounce_ms = Column(Integer, nullable=False, server_default="1000")
    clipboard_clear_ms = Column(Integer, nullable=False, server_default="30000")
