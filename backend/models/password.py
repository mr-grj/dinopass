from typing import Optional

from sqlalchemy import Column, Integer, LargeBinary, String, TIMESTAMP, func

from models.base import BaseModel


class PasswordModel(BaseModel):
    __tablename__ = "password"

    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted: Optional[TIMESTAMP] = Column(TIMESTAMP, nullable=True, default=None)

    password_name = Column(String, nullable=False, unique=True)
    password_value = Column(LargeBinary, nullable=False)
    description = Column(String, nullable=True)
