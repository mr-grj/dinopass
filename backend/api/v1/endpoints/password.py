from fastapi import APIRouter, Depends

from api.v1.endpoints.deps import password_case
from cases.password import PasswordCase
from schemas.password import Password

router = APIRouter(prefix="/passwords", tags=["passwords"])


@router.get("/{password_name}/{key_derivation}", response_model=list[Password])
async def get_password(
    password_name: str,
    key_derivation: str,
    case: PasswordCase = Depends(password_case)
):
    return await case.get_password(key_derivation, password_name)


@router.get("/{key_derivation}", response_model=list[Password])
async def get_passwords(
    key_derivation: str,
    case: PasswordCase = Depends(password_case)
):
    return await case.get_passwords(key_derivation)
