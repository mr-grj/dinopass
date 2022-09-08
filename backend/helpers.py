import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_hash_key(master_password: str) -> str:
    return hashlib.sha512(master_password.encode()).hexdigest()


def generate_key_derivation(salt: bytes, master_password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt(key: bytes | str, value_to_encrypt: bytes) -> bytes:
    return Fernet(key).encrypt(value_to_encrypt)


def decrypt(key, encrypted_value):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_value).decode()
    except InvalidToken:
        return b''
