from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api import crud, schemas
from backend.db import get_db

master_password_router = APIRouter(
    prefix="/master_password",
    tags=["master_password"]
)


@master_password_router.post("/check", response_model=schemas.MasterPasswordResponse)
def check_master_password(body: schemas.MasterPasswordPayload, db: Session = Depends(get_db)):
    master_password = body.master_password
    if not master_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master password can't be empty."
        )

    response = crud.check_master_password(master_password, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid master password."
        )

    return schemas.MasterPasswordResponse(
        msg="Valid master password.",
        status_code=status.HTTP_200_OK,
        context=schemas.MasterPasswordContext(
            key_derivation=response["key_derivation"]
        )
    )


@master_password_router.post("/create", response_model=schemas.MasterPasswordResponse)
def create_master_password(body: schemas.MasterPasswordPayload, db: Session = Depends(get_db)):
    master_password = body.master_password
    if not master_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master password can't be empty."
        )

    response = crud.create_master_password(master_password, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response["msg"]
        )

    return schemas.MasterPasswordResponse(
        msg="Successfully created master password.",
        status_code=status.HTTP_200_OK,
        context=schemas.MasterPasswordContext(
            key_derivation=response["key_derivation"]
        )
    )
