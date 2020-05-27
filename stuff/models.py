import os
import sys

from psycopg2 import OperationalError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


ENGINE = create_engine(f'sqlite:///{os.path.dirname(os.path.dirname(__file__))}/stuff.db')
SESSION = sessionmaker(bind=ENGINE)
Base = declarative_base()


class PasswordMixin:
    id = Column(Integer, primary_key=True)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def get(cls, session):
        return session.query(cls).first()

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def has_records(cls, session):
        return cls.get(session)

    @classmethod
    def purge(cls, session):
        return session.query(cls).delete()

    def to_dict(self):
        record = vars(self)
        record.pop('_sa_instance_state')
        record.pop('id')
        return record


class MasterPassword(Base, PasswordMixin):
    __tablename__ = 'master_password'

    salt = Column(String, nullable=False)
    hash_key = Column(String, nullable=False)

    def __init__(self, salt, hash_key):
        self.salt = salt
        self.hash_key = hash_key


class Password(Base, PasswordMixin):
    __tablename__ = 'passwords'

    name = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)

    def __repr__(self):
        return f"<Password(name='{self.name}')>"

    def __str__(self):
        return f"<Password(name='{self.name}', value='***')>"

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @classmethod
    def get_by_name(cls, name, session):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def update_by_field(cls, field, value, field_to_update, new_value, session):
        if not getattr(cls, field) and not isinstance(field, str):
            raise AttributeError(f'Invalid attribute name: {field}')

        if not getattr(cls, field_to_update) and not isinstance(field_to_update, str):
            raise AttributeError(f'Invalid field_to_update name: {field_to_update}')

        return session.query(cls).filter_by(**{field: value}).update({field_to_update: new_value})

    @classmethod
    def delete_by_name(cls, name, session):
        return session.query(cls).filter_by(name=name).delete()


try:
    Base.metadata.create_all(ENGINE)
except OperationalError as operational_error:
    sys.exit(f'Error when connecting to DB: {operational_error}. '
             f'Please make sure you have correctly set up your DB!')
