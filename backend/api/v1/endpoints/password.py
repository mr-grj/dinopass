import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from starlette.responses import StreamingResponse

from api.rate_limit import limiter
from api.v1.endpoints.deps import get_password_crud
from api.v1.exceptions import handle_forbidden, handle_mismatch, handle_not_found
from api.v1.responses import inject_responses
from crud.password import PasswordCRUD
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.master_password import MasterPassword
from schemas.password import (
    Password,
    PasswordCreate,
    PasswordDelete,
    PasswordResponse,
    PasswordUpdate,
    PasswordUpdatePayload,
)

router = APIRouter(tags=["passwords"])


@router.get(
    "",
    name="passwords:get",
    response_model=list[PasswordResponse],
    responses=inject_responses({status.HTTP_403_FORBIDDEN: SimpleDetailSchema}),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def get_passwords(
    request: Request,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> list[PasswordResponse]:
    return await crud.get_passwords(request.headers)


@router.get(
    "/{password_name}",
    name="passwords:get_by_name",
    response_model=PasswordResponse,
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
) -> PasswordResponse:
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


@router.post(
    "/backup",
    name="passwords:backup",
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit("3/hour")
@handle_forbidden
@handle_not_found
@handle_mismatch
async def backup_passwords(
    request: Request,
    body: MasterPassword,
    crud: PasswordCRUD = Depends(get_password_crud),
) -> StreamingResponse:
    data = await crud.create_backup(body.master_password, request.headers)
    filename = f"dinopass_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
