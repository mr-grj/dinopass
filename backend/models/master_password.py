from sqlalchemy import TIMESTAMP, Column, Integer, LargeBinary, String, func

from models.base import BaseModel


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
