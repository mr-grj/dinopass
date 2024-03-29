from sqlalchemy import (
    Column,
    FetchedValue,
    Integer,
    LargeBinary,
    String,
    TIMESTAMP,
)
from typing import Optional

from models.base import BaseModel


class MasterPasswordModel(BaseModel):
    __tablename__ = 'master_password'

    id = Column(Integer, primary_key=True)
    created: TIMESTAMP = Column(
        TIMESTAMP, nullable=False, server_default=FetchedValue()
    )
    updated: TIMESTAMP = Column(TIMESTAMP, server_default=FetchedValue())
    deleted: Optional[TIMESTAMP] = Column(TIMESTAMP, nullable=True, default=None)

    salt = Column(LargeBinary, nullable=False)
    hash_key = Column(String, nullable=False)

    def __init__(self, salt, hash_key):
        self.salt = salt
        self.hash_key = hash_key


master_password_table = MasterPasswordModel.__table__
