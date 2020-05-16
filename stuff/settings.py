import getpass
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


load_dotenv()


DB_PASSWORD = getpass.getpass('Please enter DB PASS: ')
if not DB_PASSWORD:
    raise ValueError('You MUST insert your DB password.')


DB_CREDENTIALS = {
    'drivername': os.getenv('DB_DRIVERNAME'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': DB_PASSWORD,
}

ENGINE = create_engine(URL(**DB_CREDENTIALS))
SESSION = sessionmaker(bind=ENGINE)
session = SESSION()
