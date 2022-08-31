from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.crud import check_master_password, create_master_password
from backend.api.schemas import (
    MasterPasswordContext,
    MasterPasswordPayload,
    MasterPasswordResponse,
)

master_password_router = APIRouter(
    prefix="/master_password",
    tags=["master_password"]
)


@master_password_router.post("/check", response_model=MasterPasswordResponse)
def check_master_password(
    body: MasterPasswordPayload,
    db: Session = Depends(get_db)
):
    master_password = body.master_password
    if not master_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master password can't be empty."
        )

    response = check_master_password(master_password, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid master password."
        )

    return MasterPasswordResponse(
        msg="Valid master password.",
        status_code=status.HTTP_200_OK,
        context=MasterPasswordContext(
            key_derivation=response["key_derivation"]
        )
    )


@master_password_router.post("/create", response_model=MasterPasswordResponse)
def post_master_password(
    body: MasterPasswordPayload,
    db: Session = Depends(get_db)
):
    master_password = body.master_password
    if not master_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master password can't be empty."
        )

    response = create_master_password(master_password, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response["msg"]
        )

    return MasterPasswordResponse(
        msg="Successfully created master password.",
        status_code=status.HTTP_200_OK,
        context=MasterPasswordContext(
            key_derivation=response["key_derivation"]
        )
    )
