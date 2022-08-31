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

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def get(cls, session):
        return session.query(cls).first()

    @classmethod
    def has_records(cls, session):
        return cls.get(session)

    @classmethod
    def purge(cls, session):
        return session.query(cls).delete()

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def update_name(cls, current_name, new_name, session):
        if not session.query(cls).filter_by(password_name=current_name).first():
            raise ValueError(f"No password with name={current_name}")
        return (
            session
                .query(cls)
                .filter_by(**{"password_name": current_name})
                .update({"password_name": new_name})
        )

    @classmethod
    def update_password(cls, name, new_password, session):
        if not session.query(cls).filter_by(password_name=name).first():
            raise ValueError(f"No password with name={name}")

        return (
            session
                .query(cls)
                .filter_by(**{"password_name": name})
                .update({"password_value": new_password})
        )

    @classmethod
    def delete_by_name(cls, name, session):
        return session.query(cls).filter_by(password_name=name).delete()

    def to_dict(self):
        record = vars(self)
        record.pop('_sa_instance_state')
        record.pop('id')
        return record


password_table = PasswordModel.__table__
