import getpass
import os
import sys

from dotenv import load_dotenv
from psycopg2 import OperationalError
from sqlalchemy import Column, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()


Base = declarative_base()

DB_CREDENTIALS = {
    'drivername': os.getenv('DB_DRIVERNAME'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': getpass.getpass('Please enter DB PASS: '),
}
ENGINE = create_engine(URL(**DB_CREDENTIALS))
SESSION = sessionmaker(bind=ENGINE)


class CredentialsTable(Base):
    __tablename__ = 'credentials'
    __table_args__ = (
        UniqueConstraint('name', 'group', name='unique_name_group'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<Credential(name='{self.name}', group='{self.group}'>"

    def __str__(self):
        return f"<Credential(name='{self.name}', group='{self.group}', " \
               f"password='***'>"

    def __init__(self, name, group, password):
        self.name = name
        self.group = group
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
    def get_by_field(cls, field, value, session):
        if not getattr(cls, field):
            raise AttributeError(f'Invalid attribute name: {field}')

        return session.query(cls).filter_by(**{field: value}).first()

    @classmethod
    def update_by_field(cls, field, value, field_to_update, new_value, session):
        if not getattr(cls, field) and not isinstance(field, str):
            raise AttributeError(f'Invalid attribute name: {field}')

        if not getattr(cls, field_to_update) and not isinstance(field_to_update, str):
            raise AttributeError(f'Invalid field_to_update name: {field_to_update}')

        return session.query(cls).filter_by(**{field: value}).update({field_to_update: new_value})

    @classmethod
    def delete_by_field(cls, field, value, session):
        if not getattr(cls, field):
            raise AttributeError(f'Invalid attribute name: {field}')

        return session.query(cls).filter_by(**{field: value}).delete()

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
