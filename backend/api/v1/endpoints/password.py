from fastapi import APIRouter, Depends, Request, status

from api.v1.endpoints.deps import get_password_crud
from api.v1.exceptions import handle_forbidden, handle_mismatch, handle_not_found
from api.v1.responses import inject_responses
from crud.password import PasswordCRUD
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.password import (
    Password,
    PasswordCreate,
    PasswordDelete,
    PasswordUpdate,
    PasswordUpdatePayload,
)

router = APIRouter(tags=["passwords"])


@router.get(
    "",
    name="passwords:get",
    response_model=list[Password],
    responses=inject_responses({status.HTTP_403_FORBIDDEN: SimpleDetailSchema}),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def get_passwords(
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> list[Password]:
    return await crud.get_passwords(request.headers)


@router.get(
    "/{password_name}",
    name="passwords:get_by_name",
    response_model=Password,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def get_password(
    password_name: str,
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> Password:
    return await crud.get_password(password_name, request.headers)


@router.post(
    "/create",
    name="password:create",
    response_model=PasswordCreate,
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        }
    ),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def create_password(
    password: Password,
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> PasswordCreate:
    return await crud.create_password(password, request.headers)


@router.patch(
    "/update",
    name="passwords:update",
    response_model=PasswordUpdate,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        }
    ),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def update_password(
    body: PasswordUpdatePayload,
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> PasswordUpdate:
    return await crud.update_password(
        password=body.password,
        new_password=body.new_password,
        headers=request.headers,
    )


@router.delete(
    "/{password_name}",
    name="passwords:delete",
    response_model=PasswordDelete,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def delete_password(
    password_name: str,
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> PasswordDelete:
    return await crud.delete_password(password_name, request.headers)
