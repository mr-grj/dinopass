from sqlalchemy import func, select

from api.exceptions import NotFound, TypesMismatchError
from crud.base import BaseCRUD
from helpers import (
    decrypt,
    decrypt_bytes,
    encrypt,
    encrypt_optional,
)
from models import PasswordAttachmentModel, PasswordModel
from schemas import AttachmentResponse

_MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024  # 5 MB per file
_MAX_ATTACHMENTS_PER_ENTRY = 20
_MAX_TOTAL_BYTES = 25 * 1024 * 1024  # 25 MB across all attachments of one entry


class AttachmentCRUD(BaseCRUD):
    async def _get_active_password(self, password_name: str) -> PasswordModel:
        model = (
            await self.session.execute(
                select(PasswordModel).where(
                    PasswordModel.password_name == password_name,
                    PasswordModel.deleted.is_(None),
                )
            )
        ).scalar()
        if not model:
            raise NotFound(f"No password found for '{password_name}' in the vault.")
        return model

    async def _get_attachment(
        self, password_id: int, attachment_id: int
    ) -> PasswordAttachmentModel:
        model = (
            await self.session.execute(
                select(PasswordAttachmentModel).where(
                    PasswordAttachmentModel.id == attachment_id,
                    PasswordAttachmentModel.password_id == password_id,
                )
            )
        ).scalar()
        if not model:
            raise NotFound("Attachment not found.")
        return model

    @staticmethod
    def _to_response(
        model: PasswordAttachmentModel, key_derivation: str
    ) -> AttachmentResponse:
        filename = decrypt(key_derivation, model.filename)
        if filename is None:
            raise TypesMismatchError("Invalid key for attachment.")
        return AttachmentResponse(
            id=model.id,
            filename=filename,
            content_type=decrypt(key_derivation, model.content_type)
            if model.content_type is not None
            else None,
            size_bytes=model.size_bytes,
            created=model.created,
        )

    async def list_attachments(
        self, password_name: str, key_derivation: str
    ) -> list[AttachmentResponse]:
        password = await self._get_active_password(password_name)
        models = (
            await self.session.execute(
                select(PasswordAttachmentModel)
                .where(PasswordAttachmentModel.password_id == password.id)
                .order_by(PasswordAttachmentModel.created)
            )
        ).scalars()
        return [self._to_response(m, key_derivation) for m in models]

    async def add_attachment(
        self,
        password_name: str,
        filename: str,
        content_type: str | None,
        data: bytes,
        key_derivation: str,
    ) -> AttachmentResponse:
        if not data:
            raise TypesMismatchError("Attachment is empty.")
        if len(data) > _MAX_ATTACHMENT_BYTES:
            raise TypesMismatchError("Attachment too large. Maximum size is 5 MB.")

        password = await self._get_active_password(password_name)

        count = (
            await self.session.execute(
                select(func.count())
                .select_from(PasswordAttachmentModel)
                .where(PasswordAttachmentModel.password_id == password.id)
            )
        ).scalar() or 0
        if count >= _MAX_ATTACHMENTS_PER_ENTRY:
            raise TypesMismatchError(
                f"This entry already has the maximum of "
                f"{_MAX_ATTACHMENTS_PER_ENTRY} attachments."
            )

        used = (
            await self.session.execute(
                select(
                    func.coalesce(func.sum(PasswordAttachmentModel.size_bytes), 0)
                ).where(PasswordAttachmentModel.password_id == password.id)
            )
        ).scalar() or 0
        if used + len(data) > _MAX_TOTAL_BYTES:
            raise TypesMismatchError(
                "Attachments for this entry would exceed the 25 MB total limit."
            )

        model = PasswordAttachmentModel(
            password_id=password.id,
            filename=encrypt(key_derivation, filename.encode()),
            content=encrypt(key_derivation, data),
            content_type=encrypt_optional(key_derivation, content_type),
            size_bytes=len(data),
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_response(model, key_derivation)

    async def get_attachment_data(
        self, password_name: str, attachment_id: int, key_derivation: str
    ) -> tuple[str, str | None, bytes]:
        password = await self._get_active_password(password_name)
        model = await self._get_attachment(password.id, attachment_id)

        filename = decrypt(key_derivation, model.filename)
        data = decrypt_bytes(key_derivation, model.content)
        if filename is None or data is None:
            raise TypesMismatchError("Invalid key for attachment.")
        content_type = (
            decrypt(key_derivation, model.content_type)
            if model.content_type is not None
            else None
        )
        return filename, content_type, data

    async def delete_attachment(self, password_name: str, attachment_id: int) -> None:
        password = await self._get_active_password(password_name)
        model = await self._get_attachment(password.id, attachment_id)
        await self.session.delete(model)
        await self.session.flush()
