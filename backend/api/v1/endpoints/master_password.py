from fastapi import APIRouter, Depends, status

from api.v1.endpoints.deps import master_password_case
from api.v1.exceptions import (
    handle_forbidden,
    handle_not_found,
    handle_mismatch,
)
from api.v1.responses import inject_responses
from cases.master_password import MasterPasswordCase
from schemas.exceptions_responses import SimpleDetailSchema
from schemas.master_password import (
    MasterPassword,
    MasterPasswordPayload,
    UpdateMasterPasswordPayload,
)

router = APIRouter(tags=["master-password"])


@router.post(
    "/check",
    name="master-password:check",
    response_model=MasterPassword,
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
async def check_master_password(
    body: MasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPassword:
    return await case.check_master_password(body.master_password)


@router.post(
    "/create",
    name="master-password:create",
    response_model=MasterPassword,
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
async def create_master_password(
    body: MasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPassword:
    return await case.create_master_password(body.master_password)


@router.patch(
    "/update",
    name="master-password:update",
    response_model=MasterPassword,
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
async def update_master_password(
    body: UpdateMasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPassword:
    return await case.update_master_password(
        body.master_password,
        body.new_master_password
    )
