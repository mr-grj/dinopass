import os
import sys

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


ENGINE = create_engine(f'sqlite:///{os.path.dirname(os.path.dirname(__file__))}/dinopass.db')
SESSION = sessionmaker(bind=ENGINE)
Base = declarative_base()


class PasswordMixin:
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

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


class MasterPassword(Base, PasswordMixin):
    __tablename__ = 'master_password'

    salt = Column(String, nullable=False)
    hash_key = Column(String, nullable=False)

    def __init__(self, salt, hash_key):
        self.salt = salt
        self.hash_key = hash_key


class Password(Base, PasswordMixin):
    __tablename__ = 'passwords'

    password_name = Column(String, nullable=False, unique=True)
    password_value = Column(String, nullable=False)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Password(password_name='{self.password_name}')>"

    def __str__(self):
        return f"<Password(password_name='{self.password_name}', password_value='***')>"

    def __init__(self, password_name, password_value):
        self.password_name = password_name
        self.password_value = password_value

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
    def update_by_field(cls, field, value, field_to_update, new_value, session):
        if not getattr(cls, field) and not isinstance(field, str):
            raise AttributeError(f'Invalid attribute name: {field}')

        if not getattr(cls, field_to_update) and not isinstance(field_to_update, str):
            raise AttributeError(f'Invalid field_to_update name: {field_to_update}')

        return session.query(cls).filter_by(**{field: value}).update({field_to_update: new_value})

    @classmethod
    def delete_by_name(cls, name, session):
        return session.query(cls).filter_by(password_name=name).delete()

    def to_dict(self):
        record = vars(self)
        record.pop('_sa_instance_state')
        record.pop('id')
        return record


try:
    Base.metadata.create_all(ENGINE)
except Exception as operational_error:
    sys.exit(f'Error when connecting to DB: {operational_error}. '
             f'Please make sure you have correctly set up your DB!')
