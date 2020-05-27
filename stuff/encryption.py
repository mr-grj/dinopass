import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_hash_key(master_password):
    return hashlib.sha512(master_password.encode()).hexdigest()


def generate_key_derivation(salt, master_password):
    """Generate Fernet Key:

    salt: os.urandom(16)
    password: bytes
    """

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt(key, value_to_encrypt):
    f = Fernet(key)
    encrypted_value = f.encrypt(value_to_encrypt.encode())
    return encrypted_value


def decrypt(key, encrypted_value):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_value)
    except InvalidToken:
        return b''
