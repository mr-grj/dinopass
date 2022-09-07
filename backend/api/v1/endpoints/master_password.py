from fastapi import APIRouter, Depends, Response, status

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
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPassword,
    MasterPasswordUpdate,
    MasterPasswordUpdatePayload,
)

router = APIRouter(tags=["master-password"])


@router.post(
    "/check",
    name="master-password:check",
    response_model=MasterPasswordCheck,
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
    body: MasterPassword,
    response: Response,
    case: MasterPasswordCase = Depends(master_password_case),
) -> MasterPasswordCheck:
    return await case.check_master_password(
        master_password=body.master_password,
        headers=response.headers
    )


@router.post(
    "/create",
    name="master-password:create",
    response_model=MasterPasswordCreate,
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
    body: MasterPassword,
    response: Response,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPasswordCreate:
    return await case.create_master_password(
        master_password=body.master_password,
        headers=response.headers
    )


@router.patch(
    "/update",
    name="master-password:update",
    response_model=MasterPasswordUpdate,
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
    body: MasterPasswordUpdatePayload,
    response: Response,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPasswordUpdate:
    return await case.update_master_password(
        master_password=body.master_password,
        new_master_password=body.new_master_password,
        headers=response.headers
    )
