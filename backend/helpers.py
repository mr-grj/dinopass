import base64
import io
import json
from datetime import UTC, datetime

import bcrypt
import pyzipper
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# KDF version constants
KDF_V1_PBKDF2 = 1  # legacy — CPU-bound, GPU-crackable
KDF_V2_ARGON2ID = 2  # current — memory-hard (64 MiB), GPU/ASIC resistant

# Argon2id parameters (OWASP 2024 interactive profile)
_ARGON2_MEMORY_COST = 65536  # 64 MiB in KiB
_ARGON2_ITERATIONS = 3
_ARGON2_LANES = 4
_ARGON2_LENGTH = 32


def hash_master_password(master_password: str) -> str:
    return bcrypt.hashpw(master_password.encode(), bcrypt.gensalt()).decode()


def verify_master_password(master_password: str, hash_key: str) -> bool:
    return bcrypt.checkpw(master_password.encode(), hash_key.encode())


def _derive_pbkdf2(salt: bytes, master_password: str) -> bytes:
    """Legacy PBKDF2-HMAC-SHA256 (v1). Only used during migration of old vaults."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def _derive_argon2id(salt: bytes, master_password: str) -> bytes:
    """Argon2id (v2): memory-hard, GPU/ASIC resistant."""
    kdf = Argon2id(
        salt=salt,
        length=_ARGON2_LENGTH,
        iterations=_ARGON2_ITERATIONS,
        lanes=_ARGON2_LANES,
        memory_cost=_ARGON2_MEMORY_COST,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def generate_key_derivation(
    salt: bytes, master_password: str, kdf_version: int = KDF_V2_ARGON2ID
) -> bytes:
    if kdf_version == KDF_V1_PBKDF2:
        return _derive_pbkdf2(salt, master_password)
    return _derive_argon2id(salt, master_password)


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
