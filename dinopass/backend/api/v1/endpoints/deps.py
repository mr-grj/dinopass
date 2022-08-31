from fastapi import Depends

from src.api.deps import get_crud
from src.cases.user.user import UserCase
from src.crud.user import UserCRUD


async def user_case(
    user_crud: UserCRUD = Depends(get_crud(UserCRUD))
) -> UserCase:
    return UserCase(user_crud=user_crud)
