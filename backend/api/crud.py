import os

from sqlalchemy.orm import Session

from helpers import generate_hash_key, generate_key_derivation
from views import MasterPasswordView, PasswordView

SALT_LENGTH = 16


def check_master_password(master_password: str, db: Session) -> dict:
    master_password_view = MasterPasswordView(db)

    hash_key = generate_hash_key(master_password)
    key_derivation = generate_key_derivation(
        master_password_view.salt,
        master_password
    )
    if master_password_view.is_valid(hash_key):
        return {
            "valid": True,
            "key_derivation": key_derivation
        }
    return {"valid": False}


def create_master_password(master_password: str, db: Session) -> dict:
    master_password_view = MasterPasswordView(db)
    if master_password_view.has_records():
        return {
            "msg": "It looks like you already have a master password.",
            "valid": False
        }

    salt = os.urandom(SALT_LENGTH)
    hash_key = generate_hash_key(master_password)
    key_derivation = generate_key_derivation(salt, master_password)

    try:
        master_password_view.create(salt=salt, hash_key=hash_key)
    except Exception as e:
        return {
            "msg": f"{e}",
            "valid": False
        }

    return {
        "valid": True,
        "key_derivation": key_derivation
    }


def get_all_passwords(key_derivation, db: Session):
    password_view = PasswordView(db)
    try:
        response = password_view.get_all(key_derivation)
    except Exception as e:
        return {
            "msg": f"{e}",
            "valid": False
        }

    if response is False:
        return {
            "msg": "Bad derivation key provided.",
            "valid": False
        }

    return {
        "valid": True,
        "passwords": response
    }
