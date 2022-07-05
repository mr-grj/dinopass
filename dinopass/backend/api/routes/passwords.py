from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api import crud, schemas
from backend.config.db import get_db

passwords_router = APIRouter(
    prefix="/passwords",
    tags=["passwords"]
)


@passwords_router.get("/{key_derivation}", response_model=schemas.PasswordsResponse)
def get_all_passwords(key_derivation: str, db: Session = Depends(get_db)):
    response = crud.get_all_passwords(key_derivation, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something bad happened: {response['msg']}"
        )

    passwords = response["passwords"]
    if not passwords:
        return schemas.PasswordsResponse(
            msg="No passwords stored.",
            status_code=status.HTTP_200_OK,
            passwords=[]
        )

    return schemas.PasswordsResponse(
        msg="Successfully fetched passwords.",
        status_code=status.HTTP_200_OK,
        passwords=passwords
    )
