from fastapi import APIRouter, Depends

from api.v1.endpoints.deps import master_password_case
from cases.master_password import MasterPasswordCase
from schemas.master_password import (
    MasterPassword,
    MasterPasswordPayload,
)

router = APIRouter(prefix="/master_password", tags=["master_password"])


@router.post("/check", response_model=MasterPassword)
async def check_master_password(
    body: MasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPassword:
    return await case.check_master_password(body.master_password)


@router.post("/create", response_model=MasterPassword)
async def create_master_password(
    body: MasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPassword:
    return await case.create_master_password(body.master_password)
