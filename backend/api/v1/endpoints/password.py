from fastapi import APIRouter, Depends, status

from api.v1.endpoints.deps import password_case
from api.v1.exceptions import handle_forbidden, handle_not_found, handle_mismatch
from api.v1.responses import inject_responses
from cases.password import PasswordCase
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.password import Password

router = APIRouter(tags=["passwords"])


@router.get(
    "/{password_name}/{key_derivation}",
    name="password:get",
    response_model=Password,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema
        }
    )
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def get_password(
    password_name: str,
    key_derivation: str,
    case: PasswordCase = Depends(password_case)
) -> Password:
    return await case.get_password(key_derivation, password_name)


@router.post(
    "/create/{key_derivation}",
    name="password:create",
    response_model=Password,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema
        }
    )
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def create_password(
    key_derivation: str,
    password: Password,
    case: PasswordCase = Depends(password_case)
) -> Password:
    return await case.create_password(key_derivation, password)


@router.get(
    "/{key_derivation}",
    name="password:get_all",
    response_model=list[Password],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema
        }
    )
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def get_passwords(
    key_derivation: str,
    case: PasswordCase = Depends(password_case)
) -> list[Password]:
    return await case.get_passwords(key_derivation)
