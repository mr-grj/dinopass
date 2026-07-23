import io
from datetime import UTC, datetime
from urllib.parse import quote

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
    AttachmentCRUDDep,
    KeyDerivationDep,
    PasswordCRUDDep,
    get_key_derivation,
    require_master_password,
)
from api.exceptions import TypesMismatchError
from api.rate_limit import limiter, rate
from api.responses import inject_responses
from schemas import (
    AttachmentResponse,
    FavoriteUpdatePayload,
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
_MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024  # 5 MB


async def _read_capped(file: UploadFile, max_bytes: int, message: str) -> bytes:
    if file.size is not None and file.size > max_bytes:
        raise TypesMismatchError(message)
    data = await file.read()
    if len(data) > max_bytes:
        raise TypesMismatchError(message)
    return data


def _safe_content_disposition(filename: str) -> str:
    cleaned = filename.replace("\r", "").replace("\n", "").replace('"', "")
    cleaned = cleaned.strip() or "attachment"
    ascii_name = cleaned.encode("ascii", "replace").decode("ascii").replace("?", "_")
    quoted = quote(cleaned, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quoted}"


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
    "/trash",
    name="passwords:trash",
    response_model=list[PasswordResponse],
    dependencies=[Depends(require_master_password)],
    responses=inject_responses({status.HTTP_403_FORBIDDEN: SimpleDetailSchema}),
)
async def get_trash(
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
) -> list[PasswordResponse]:
    return await crud.get_trash(key_derivation)


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


@router.patch(
    "/{password_name}/favorite",
    name="passwords:favorite",
    response_model=PasswordUpdate,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def set_favorite(
    password_name: str,
    body: FavoriteUpdatePayload,
    crud: PasswordCRUDDep,
) -> PasswordUpdate:
    return await crud.set_favorite(password_name, body.favorite)


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
    "/{password_name}/restore",
    name="passwords:restore",
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
async def restore_password(
    password_name: str,
    crud: PasswordCRUDDep,
) -> PasswordUpdate:
    return await crud.restore_password(password_name)


@router.delete(
    "/{password_name}/purge",
    name="passwords:purge",
    response_model=PasswordDelete,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def purge_password(
    password_name: str,
    crud: PasswordCRUDDep,
) -> PasswordDelete:
    return await crud.purge_password(password_name)


@router.get(
    "/{password_name}/attachments",
    name="attachments:list",
    response_model=list[AttachmentResponse],
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def list_attachments(
    password_name: str,
    crud: AttachmentCRUDDep,
    key_derivation: KeyDerivationDep,
) -> list[AttachmentResponse]:
    return await crud.list_attachments(password_name, key_derivation)


@router.post(
    "/{password_name}/attachments",
    name="attachments:add",
    response_model=AttachmentResponse,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("60/hour"))
async def add_attachment(
    request: Request,
    password_name: str,
    file: UploadFile,
    crud: AttachmentCRUDDep,
    key_derivation: KeyDerivationDep,
) -> AttachmentResponse:
    data = await _read_capped(
        file, _MAX_ATTACHMENT_BYTES, "Attachment too large. Maximum size is 5 MB."
    )
    return await crud.add_attachment(
        password_name=password_name,
        filename=file.filename or "attachment",
        content_type=file.content_type,
        data=data,
        key_derivation=key_derivation,
    )


@router.get(
    "/{password_name}/attachments/{attachment_id}",
    name="attachments:download",
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def download_attachment(
    password_name: str,
    attachment_id: int,
    crud: AttachmentCRUDDep,
    key_derivation: KeyDerivationDep,
) -> StreamingResponse:
    filename, content_type, data = await crud.get_attachment_data(
        password_name, attachment_id, key_derivation
    )
    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": _safe_content_disposition(filename)},
    )


@router.delete(
    "/{password_name}/attachments/{attachment_id}",
    name="attachments:delete",
    response_model=PasswordDelete,
    dependencies=[Depends(require_master_password), Depends(get_key_derivation)],
    responses=inject_responses(
        {
            status.HTTP_404_NOT_FOUND: SimpleDetailSchema,
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
        }
    ),
)
async def delete_attachment(
    password_name: str,
    attachment_id: int,
    crud: AttachmentCRUDDep,
) -> PasswordDelete:
    await crud.delete_attachment(password_name, attachment_id)
    return PasswordDelete(deleted=True, detail="Attachment deleted.")


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
    file_bytes = await _read_capped(
        file, _MAX_IMPORT_FILE_BYTES, "File too large. Maximum allowed size is 10 MB."
    )
    return await crud.import_passwords(
        file_bytes=file_bytes,
        master_password=master_password,
        key_derivation=key_derivation,
        on_conflict=on_conflict,
    )


@router.post(
    "/import/csv",
    name="passwords:import_csv",
    response_model=PasswordImportResult,
    dependencies=[Depends(require_master_password)],
    responses=inject_responses(
        {
            status.HTTP_403_FORBIDDEN: SimpleDetailSchema,
            status.HTTP_400_BAD_REQUEST: SimpleDetailSchema,
            status.HTTP_429_TOO_MANY_REQUESTS: SimpleDetailSchema,
        }
    ),
)
@limiter.limit(rate("5/hour"))
async def import_passwords_csv(
    request: Request,
    file: UploadFile,
    crud: PasswordCRUDDep,
    key_derivation: KeyDerivationDep,
    on_conflict: OnConflict = Form(OnConflict.skip),
) -> PasswordImportResult:
    file_bytes = await _read_capped(
        file, _MAX_IMPORT_FILE_BYTES, "File too large. Maximum allowed size is 10 MB."
    )
    return await crud.import_passwords_csv(
        file_bytes=file_bytes,
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
    filename = f"ciphermoth_backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.zip"
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
