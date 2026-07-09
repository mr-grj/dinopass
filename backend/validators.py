from urllib.parse import parse_qs, urlparse

_MIN_MASTER_PASSWORD_LENGTH = 12
_MIN_CHARACTER_CLASSES = 2

_BASE32_ALPHABET = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")


def _character_classes(password: str) -> int:
    return sum(
        (
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        )
    )


def validate_master_password_strength(password: str) -> str:
    """
    Return the password unchanged, or raise ValueError if it is too weak.
    """
    if len(password) < _MIN_MASTER_PASSWORD_LENGTH:
        raise ValueError(
            f"Master password must be at least {_MIN_MASTER_PASSWORD_LENGTH} "
            "characters long."
        )

    if _character_classes(password) < _MIN_CHARACTER_CLASSES:
        raise ValueError(
            "Master password must mix at least two of: lowercase, uppercase, "
            "numbers, symbols."
        )

    return password


def normalize_totp_secret(raw: str | None) -> str | None:
    """
    Normalize a two-factor secret to bare base32, or raise ValueError.

    Accepts either a raw base32 secret (as shown next to most "enable 2FA" QR
    codes) or a full ``otpauth://`` URI, since users commonly paste either.
    Spaces and padding are stripped and the result is upper-cased so the same
    secret always encrypts to a comparable value. Returns None for empty input.
    """
    if not raw:
        return None

    value = raw.strip()
    if value.lower().startswith("otpauth://"):
        secret = parse_qs(urlparse(value).query).get("secret", [""])[0]
        value = secret

    value = value.replace(" ", "").upper().rstrip("=")
    if not value:
        return None

    if any(c not in _BASE32_ALPHABET for c in value):
        raise ValueError("TOTP secret must be valid base32 or an otpauth:// URI.")

    return value
