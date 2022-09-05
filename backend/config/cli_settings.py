from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Settings(BaseModel):
    base_dir: Path = Path(__file__).parent.parent.parent
    db_filename: str = "dinopass.db"
    db_zip_filename: str = (
        f"dinopass_{datetime.now()}.db.zip".replace(' ', '_')
    )

    email_subject: str = "Dinopass encrypted db backup."
    email_from: str = "Dinopass <dinopass@dinopass.com>"
    email_to: str = "Alexandru Grajdeanu <grajdeanu.alex@gmail.com>"
    email_body: str = "This is an automated email from Dinopass."


settings = Settings()

DB_FILEPATH: str = f"{settings.base_dir / settings.db_filename}"
DB_ZIP_FILEPATH: str = f"{settings.base_dir / settings.db_zip_filename}"

BASE = declarative_base()
ENGINE = create_engine(f'sqlite:///{DB_FILEPATH}')
SESSION = sessionmaker(bind=ENGINE)
