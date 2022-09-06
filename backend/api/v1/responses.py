from fastapi import status

from schemas.exceptions_responses import (
    InternalServerErrorResponseSchema,
    SimpleDetailSchema,
)


def inject_responses(response_status_codes: dict = None) -> dict:
    """
    Inject responses in an endpoint's documentation.
    """
    default_responses_model_map = {
        status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        status.HTTP_401_UNAUTHORIZED: SimpleDetailSchema,
        status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        status.HTTP_500_INTERNAL_SERVER_ERROR: InternalServerErrorResponseSchema,
    }

    if not response_status_codes:
        response_status_codes = {}

    response_status_codes = default_responses_model_map | response_status_codes

    for status_code, model in response_status_codes.items():
        response_status_codes[status_code] = {"model": model}

    return response_status_codes
