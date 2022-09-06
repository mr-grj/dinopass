from typing import Optional

from sqlalchemy import (
    Column,
    FetchedValue,
    Integer,
    LargeBinary,
    String,
    TIMESTAMP,
)

from models.base import BaseModel


class PasswordModel(BaseModel):
    __tablename__ = 'password'

    id = Column(Integer, primary_key=True)
    created: TIMESTAMP = Column(
        TIMESTAMP, nullable=False, server_default=FetchedValue()
    )
    updated: TIMESTAMP = Column(TIMESTAMP, server_default=FetchedValue())
    deleted: Optional[TIMESTAMP] = Column(TIMESTAMP, nullable=True, default=None)

    password_name = Column(String, nullable=False, unique=True)
    password_value = Column(LargeBinary, nullable=False)
    description = Column(String, nullable=True)

    def __init__(self, password_name, password_value, description):
        self.password_name = password_name
        self.password_value = password_value
        self.description = description


password_table = PasswordModel.__table__
