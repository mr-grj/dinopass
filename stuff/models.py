import getpass
import sys

from psycopg2 import OperationalError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_CREDENTIALS = {
    'drivername': 'postgresql+psycopg2',
    'host': 'localhost',
    'database': 'stuff',
    'username': 'alex',  # stuff
    'password': getpass.getpass('Please enter DB PASS: '),
}

ENGINE = create_engine(URL(**DB_CREDENTIALS))
SESSION = sessionmaker(bind=ENGINE)

Base = declarative_base()


class CredentialsTable(Base):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<Credential(name='{self.name}'>"

    def __str__(self):
        return f"<Credential(name='{self.name}', password='***')>"

    def __init__(self, name, password):
        self.name = name
        self.password = password

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def purge(cls, session):
        return session.query(cls).delete()

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

    def to_dict(self):
        credentials = vars(self)
        credentials.pop('_sa_instance_state')
        credentials.pop('id')
        return credentials


try:
    Base.metadata.create_all(ENGINE)
except OperationalError as operational_error:
    sys.exit(f'Error when connecting to DB: {operational_error}. '
             f'Please make sure you have correctly set up your DB!')
