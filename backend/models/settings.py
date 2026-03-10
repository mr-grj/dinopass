from sqlalchemy import TIMESTAMP, Column, Integer, func

from models.base import BaseModel


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
