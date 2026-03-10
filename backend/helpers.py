import base64
import io
import json
from datetime import UTC, datetime

import bcrypt
import pyzipper
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


def create_encrypted_zip(entries: list[dict], password: str) -> bytes:
    payload = json.dumps(
        {"exported_at": datetime.now(UTC).isoformat(), "passwords": entries},
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")

    buf = io.BytesIO()
    with pyzipper.AESZipFile(
        buf, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES
    ) as zf:
        zf.setpassword(password.encode())
        zf.writestr("dinopass_backup.json", payload)
    return buf.getvalue()
