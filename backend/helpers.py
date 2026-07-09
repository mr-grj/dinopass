import base64
import hashlib
import hmac
import io
import json
import struct
import time
from datetime import UTC, datetime

import bcrypt
import pyzipper
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

_ARGON2_MEMORY_COST = 65536
_ARGON2_ITERATIONS = 3
_ARGON2_LANES = 4
_ARGON2_LENGTH = 32


def _bcrypt_input(master_password: str) -> bytes:
    digest = hashlib.sha256(master_password.encode()).digest()
    return base64.b64encode(digest)


def hash_master_password(master_password: str) -> str:
    return bcrypt.hashpw(_bcrypt_input(master_password), bcrypt.gensalt()).decode()


def verify_master_password(master_password: str, hash_key: str) -> bool:
    return bcrypt.checkpw(_bcrypt_input(master_password), hash_key.encode())


def generate_key_derivation(salt: bytes, master_password: str) -> bytes:
    kdf = Argon2id(
        salt=salt,
        length=_ARGON2_LENGTH,
        iterations=_ARGON2_ITERATIONS,
        lanes=_ARGON2_LANES,
        memory_cost=_ARGON2_MEMORY_COST,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def encrypt(key: bytes | str, value: bytes) -> bytes:
    return Fernet(key).encrypt(value)


def decrypt(key: bytes | str, encrypted_value: bytes) -> str | None:
    try:
        return Fernet(key).decrypt(encrypted_value).decode()
    except InvalidToken:
        return None


def encrypt_optional(key: bytes | str, value: str | None) -> bytes | None:
    if value is None:
        return None
    return encrypt(key, value.encode())


def decrypt_optional(key: bytes | str, encrypted_value: bytes | None) -> str | None:
    if encrypted_value is None:
        return None
    return decrypt(key, encrypted_value)


def generate_totp(secret: str, *, digits: int = 6, period: int = 30) -> str:
    """
    Return the current TOTP code for a base32 secret (RFC 6238, HMAC-SHA1).

    Used by the CLI so `password get` can show the live code. The web UI has its
    own Web Crypto implementation; both stay small and dependency-free so the
    two-factor path is easy to audit.
    """
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    counter = int(time.time()) // period
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def create_encrypted_zip(entries: list[dict[str, object]], password: str) -> bytes:
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
