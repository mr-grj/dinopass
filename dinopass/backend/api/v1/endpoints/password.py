from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.crud import get_all_passwords
from backend.api.schemas import PasswordsResponse

passwords_router = APIRouter(
    prefix="/passwords",
    tags=["passwords"]
)


@passwords_router.get("/{key_derivation}", response_model=PasswordsResponse)
async def get_all_passwords(key_derivation: str, db: Session = Depends(get_db)):
    response = get_all_passwords(key_derivation, db)
    if not response["valid"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something bad happened: {response['msg']}"
        )

    passwords = response["passwords"]
    if not passwords:
        return PasswordsResponse(
            msg="No passwords stored.",
            status_code=status.HTTP_200_OK,
            passwords=[]
        )

    return PasswordsResponse(
        msg="Successfully fetched passwords.",
        status_code=status.HTTP_200_OK,
        passwords=passwords
    )
