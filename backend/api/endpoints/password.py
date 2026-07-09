import io
from datetime import UTC, datetime

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
    UploadFile,
    status,
)
from starlette.responses import StreamingResponse

from api.endpoints.deps import (
    KeyDerivationDep,
    PasswordCRUDDep,
    get_key_derivation,
    require_master_password,
)
from api.exceptions import TypesMismatchError
from api.rate_limit import limiter, rate
from api.responses import inject_responses
from schemas import (
    MasterPassword,
    OnConflict,
    Password,
    PasswordCreate,
    PasswordDelete,
    PasswordImportResult,
    PasswordResponse,
    PasswordUpdate,
    PasswordUpdatePayload,
    SimpleDetailSchema,
)

router = APIRouter(tags=["passwords"])

_MAX_IMPORT_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.get(
    "",
    name="passwords:get",
    response_model=list[PasswordResponse],
    dependencies=[Depends(require_master_password)],
    responses=inject_responses({status.HTTP_403_FORBIDDEN: SimpleDetailSchema}),
)
async def get_passwords(
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> list[PasswordResponse]:
    return await crud.get_passwords(key_derivation)


@router.get(
    "/{password_name}",
    name="passwords:get_by_name",
    response_model=PasswordResponse,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def get_password(
    password_name: str,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> PasswordResponse:
    return await crud.get_password(password_name, key_derivation)


@router.post(
    "/create",
    name="password:create",
    response_model=PasswordCreate,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        }
    ),
)
async def create_password(
    password: Password,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> PasswordCreate:
    return await crud.create_password(password, key_derivation)


@router.patch(
    "/update",
    name="passwords:update",
    response_model=PasswordUpdate,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
        }
    ),
)
async def update_password(
    body: PasswordUpdatePayload,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> PasswordUpdate:
    return await crud.update_password(
        password=body.password,
        new_password=body.new_password,
        key_derivation=key_derivation,
    )


@router.delete(
    "/{password_name}",
    name="passwords:delete",
    response_model=PasswordDelete,
    dependencies=[Depends(require_master_password), Depends(get_key_derivation)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def delete_password(
    password_name: str,
    crud: PasswordCRUDDep,
) -> PasswordDelete:
    return await crud.delete_password(password_name)


@router.post(
    "/import",
    name="passwords:import",
    response_model=PasswordImportResult,
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("5/hour"))
async def import_passwords(
    request: Request,
    file: UploadFile,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
    master_password: str = Form(...),
    on_conflict: OnConflict = Form(OnConflict.skip),
) -> PasswordImportResult:
    if file.size is not None and file.size > _MAX_IMPORT_FILE_BYTES:
        raise TypesMismatchError("File too large. Maximum allowed size is 10 MB.")
    file_bytes = await file.read()
    if len(file_bytes) > _MAX_IMPORT_FILE_BYTES:
        raise TypesMismatchError("File too large. Maximum allowed size is 10 MB.")
    return await crud.import_passwords(
        file_bytes=file_bytes,
        master_password=master_password,
        key_derivation=key_derivation,
        on_conflict=on_conflict,
    )


@router.post(
    "/backup",
    name="passwords:backup",
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("3/hour"))
async def backup_passwords(
    request: Request,
    body: MasterPassword,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> StreamingResponse:
    data = await crud.create_backup(body.master_password, key_derivation)
    filename = f"dinopass_backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.zip"
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
