import base64

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def hash_master_password(master_password: str) -> str:
    return bcrypt.hashpw(master_password.encode(), bcrypt.gensalt()).decode()


def verify_master_password(master_password: str, hash_key: str) -> bool:
    return bcrypt.checkpw(master_password.encode(), hash_key.encode())


def generate_key_derivation(salt: bytes, master_password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def encrypt(key: bytes | str, value: bytes) -> bytes:
    return Fernet(key).encrypt(value)


def decrypt(key: bytes | str, encrypted_value: bytes) -> str | None:
    try:
        return Fernet(key).decrypt(encrypted_value).decode()
    except InvalidToken:
        return None
