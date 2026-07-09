from fastapi import (
    APIRouter,
    Request,
    status,
)

from api.endpoints.deps import KeyDerivationDep, MasterPasswordCRUDDep
from api.rate_limit import limiter, rate
from api.responses import inject_responses
from schemas import (
    MasterPassword,
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPasswordCreatePayload,
    MasterPasswordStatus,
    MasterPasswordUpdate,
    MasterPasswordUpdatePayload,
    SimpleDetailSchema,
)

router = APIRouter(tags=["master-password"])


@router.get(
    "/status",
    name="master-password:status",
    response_model=MasterPasswordStatus,
)
async def get_status(
    crud: MasterPasswordCRUDDep,
) -> MasterPasswordStatus:
    return MasterPasswordStatus(initialized=await crud.is_initialized())


@router.post(
    "/check",
    name="master-password:check",
    response_model=MasterPasswordCheck,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("10/hour"))
async def check_master_password(
    request: Request,
    body: MasterPassword,
    crud: MasterPasswordCRUDDep,
) -> MasterPasswordCheck:
    return await crud.check_master_password(master_password=body.master_password)


@router.post(
    "/create",
    name="master-password:create",
    response_model=MasterPasswordCreate,
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("5/hour"))
async def create_master_password(
    request: Request,
    body: MasterPasswordCreatePayload,
    crud: MasterPasswordCRUDDep,
) -> MasterPasswordCreate:
    return await crud.create_master_password(master_password=body.master_password)


@router.patch(
    "/update",
    name="master-password:update",
    response_model=MasterPasswordUpdate,
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("10/hour"))
async def update_master_password(
    request: Request,
    body: MasterPasswordUpdatePayload,
    crud: MasterPasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> MasterPasswordUpdate:
    return await crud.update_master_password(
        master_password=body.master_password,
        new_master_password=body.new_master_password,
        key_derivation=key_derivation,
    )
