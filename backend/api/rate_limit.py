import os

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def rate(default: str) -> str:
    return os.environ.get("DINOPASS_RATE_LIMIT", default)
