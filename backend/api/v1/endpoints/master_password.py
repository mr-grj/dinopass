from fastapi import APIRouter, Depends, Request, status

from api.rate_limit import limiter
from api.v1.endpoints.deps import get_master_password_crud
from api.v1.exceptions import handle_forbidden, handle_mismatch, handle_not_found
from api.v1.responses import inject_responses
from crud.master_password import MasterPasswordCRUD
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.master_password import (
    MasterPassword,
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPasswordStatus,
    MasterPasswordUpdate,
    MasterPasswordUpdatePayload,
)

router = APIRouter(tags=["master-password"])


@router.get(
    "/status",
    name="master-password:status",
    response_model=MasterPasswordStatus,
)
async def get_status(
    crud: MasterPasswordCRUD = Depends(get_master_password_crud),
) -> MasterPasswordStatus:
    return MasterPasswordStatus(initialized=await crud.is_initialized())


@router.post(
    "/check",
    name="master-password:check",
    response_model=MasterPasswordCheck,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit("10/hour")
@handle_forbidden
@handle_not_found
@handle_mismatch
async def check_master_password(
    request: Request,
    body: MasterPassword,
    crud: MasterPasswordCRUD = Depends(get_master_password_crud),
) -> MasterPasswordCheck:
    return await crud.check_master_password(master_password=body.master_password)


@router.post(
    "/create",
    name="master-password:create",
    response_model=MasterPasswordCreate,
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
@handle_forbidden
@handle_not_found
@handle_mismatch
async def create_master_password(
    body: MasterPassword,
    crud: MasterPasswordCRUD = Depends(get_master_password_crud),
) -> MasterPasswordCreate:
    return await crud.create_master_password(master_password=body.master_password)


@router.patch(
    "/update",
    name="master-password:update",
    response_model=MasterPasswordUpdate,
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
async def update_master_password(
    body: MasterPasswordUpdatePayload,
    request: Request,
    crud: MasterPasswordCRUD = Depends(get_master_password_crud),
) -> MasterPasswordUpdate:
    return await crud.update_master_password(
        master_password=body.master_password,
        new_master_password=body.new_master_password,
        headers=request.headers,
    )
