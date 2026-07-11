from fastapi import APIRouter, Depends, Request, status

from api.endpoints.deps import KeyDerivationDep, require_master_password
from api.rate_limit import limiter, rate
from api.responses import inject_responses
from crud import updates
from schemas import SimpleDetailSchema, UpdateApplyPayload, UpdateApplyStatus

router = APIRouter(tags=["updates"])


@router.get(
    "/apply/status",
    name="updates:apply-status",
    response_model=UpdateApplyStatus,
)
async def get_apply_status() -> UpdateApplyStatus:
    return UpdateApplyStatus(**updates.get_apply_status())


@router.post(
    "/apply",
    name="updates:apply",
    response_model=UpdateApplyStatus,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("3/hour"))
async def apply_update(
    request: Request,
    body: UpdateApplyPayload,
    key_derivation: KeyDerivationDep,
) -> UpdateApplyStatus:
    return UpdateApplyStatus(**updates.request_update(body.target))
