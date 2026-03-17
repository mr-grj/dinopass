from fastapi import status

from schemas import SimpleDetailSchema


def inject_responses(response_status_codes: dict | None = None) -> dict:
    defaults = {
        status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        status.HTTP_401_UNAUTHORIZED: SimpleDetailSchema,
        status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        status.HTTP_500_INTERNAL_SERVER_ERROR: SimpleDetailSchema,
    }

    merged = defaults | (response_status_codes or {})
    return {code: {"model": model} for code, model in merged.items()}
