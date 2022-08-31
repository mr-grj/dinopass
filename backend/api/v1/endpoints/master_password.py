from fastapi import APIRouter, Depends

from api.v1.endpoints.deps import master_password_case
from cases.master_password import MasterPasswordCase
from schemas.master_password import (
    MasterPasswordPayload,
    MasterPasswordResponse
)

router = APIRouter(prefix="/master_password", tags=["master_password"])


@router.post("/check", response_model=MasterPasswordResponse)
async def check_master_password(
    body: MasterPasswordPayload,
    case: MasterPasswordCase = Depends(master_password_case)
) -> MasterPasswordResponse:
    return await case.check_master_password(body.master_password)


# @router.post("/create", response_model=MasterPasswordResponse)
# def post_master_password(
#     body: MasterPasswordPayload,
#     db: Session = Depends(get_db)
# ):
#     master_password = body.master_password
#     if not master_password:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Master password can't be empty."
#         )
#
#     response = create_master_password(master_password, db)
#     if not response["valid"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=response["msg"]
#         )
#
#     return MasterPasswordResponse(
#         msg="Successfully created master password.",
#         status_code=status.HTTP_200_OK,
#         context=MasterPasswordContext(
#             key_derivation=response["key_derivation"]
#         )
#     )
