from fastapi import APIRouter, Depends, Request, status

from api.v1.endpoints.deps import password_case
from api.v1.exceptions import handle_forbidden, handle_not_found, handle_mismatch
from api.v1.responses import inject_responses
from cases.password import PasswordCase
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.password import (
    Password,
    PasswordCreate,
    PasswordUpdate,
    PasswordUpdatePayload,
)

router = APIRouter(tags=["passwords"])


@router.get(
    "",
    name="passwords:get",
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
    request: Request,
    case: PasswordCase = Depends(password_case)
) -> list[Password]:
    return await case.get_passwords(request.headers)


@router.get(
    "/{password_name}",
    name="passwords:get_by_name",
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
    request: Request,
    case: PasswordCase = Depends(password_case)
) -> Password:
    return await case.get_password(password_name, request.headers)


@router.post(
    "/create",
    name="password:create",
    response_model=PasswordCreate,
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
    password: Password,
    request: Request,
    case: PasswordCase = Depends(password_case)
) -> PasswordCreate:
    return await case.create_password(password, request.headers)


@router.patch(
    "/update",
    name="passwords:update",
    response_model=PasswordUpdate,
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
async def update_password(
    body: PasswordUpdatePayload,
    request: Request,
    case: PasswordCase = Depends(password_case)
) -> PasswordUpdate:
    return await case.update_password(
        password=body.password,
        new_password=body.new_password,
        headers=request.headers
    )
