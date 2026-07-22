import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from helpers import (
    decrypt,
    decrypt_bytes,
    encrypt,
    generate_key_derivation,
    hash_master_password,
    verify_master_password,
)
from models import MasterPasswordModel, PasswordAttachmentModel, PasswordModel
from schemas import (
    MasterPasswordCheck,
    MasterPasswordCreate,
    MasterPasswordUpdate,
)


async def fetch_master_password(session: AsyncSession) -> MasterPasswordModel | None:
    return (await session.execute(select(MasterPasswordModel).limit(1))).scalar()


class MasterPasswordCRUD(BaseCRUD):
    @staticmethod
    def _reencrypt(
        old_key: bytes | str, new_key: bytes | str, token: bytes, pwd: PasswordModel
    ) -> bytes:
        plaintext = decrypt(old_key, token)
        if plaintext is None:
            raise TypesMismatchError(
                f"Could not decrypt password '{pwd.password_name}'."
            )
        return encrypt(new_key, plaintext.encode())

    @classmethod
    def _reencrypt_optional(
        cls,
        old_key: bytes | str,
        new_key: bytes | str,
        token: bytes | None,
        pwd: PasswordModel,
    ) -> bytes | None:
        if token is None:
            return None
        return cls._reencrypt(old_key, new_key, token, pwd)

    @staticmethod
    def _reencrypt_text(
        old_key: bytes | str, new_key: bytes | str, token: bytes | None
    ) -> bytes | None:
        if token is None:
            return None
        plaintext = decrypt(old_key, token)
        if plaintext is None:
            raise TypesMismatchError("Could not decrypt an attachment.")
        return encrypt(new_key, plaintext.encode())

    @staticmethod
    def _reencrypt_binary(
        old_key: bytes | str, new_key: bytes | str, token: bytes
    ) -> bytes:
        raw = decrypt_bytes(old_key, token)
        if raw is None:
            raise TypesMismatchError("Could not decrypt an attachment.")
        return encrypt(new_key, raw)

    async def is_initialized(self) -> bool:
        return await fetch_master_password(self.session) is not None

    async def _get_model(self) -> MasterPasswordModel:
        model = await fetch_master_password(self.session)
        if not model:
            raise NotFound("No master password found.")
        return model

    async def check_master_password(self, master_password: str) -> MasterPasswordCheck:
        model = await self._get_model()
        if not verify_master_password(master_password, model.hash_key):
            return MasterPasswordCheck(valid=False)
        key_derivation = generate_key_derivation(model.salt, master_password)
        return MasterPasswordCheck(valid=True, key_derivation=key_derivation.decode())

    async def create_master_password(
        self, master_password: str
    ) -> MasterPasswordCreate:
        if await self.is_initialized():
            raise Forbidden("Master password already exists.")
        salt = os.urandom(16)
        key_derivation = generate_key_derivation(salt, master_password)
        self.session.add(
            MasterPasswordModel(
                salt=salt,
                hash_key=hash_master_password(master_password),
            )
        )
        await self.session.flush()
        return MasterPasswordCreate(
            created=True,
            detail="Master password created successfully.",
            key_derivation=key_derivation.decode(),
        )

    async def update_master_password(
        self, master_password: str, new_master_password: str, key_derivation: str
    ) -> MasterPasswordUpdate:
        model = await self._get_model()
        if not verify_master_password(master_password, model.hash_key):
            raise Forbidden("Current master password is incorrect.")

        new_salt = os.urandom(16)
        new_key_derivation = generate_key_derivation(new_salt, new_master_password)

        passwords = (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars()

        for pwd in passwords:
            pwd.password_value = self._reencrypt(
                key_derivation, new_key_derivation, pwd.password_value, pwd
            )
            pwd.url = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.url, pwd
            )
            pwd.totp_secret = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.totp_secret, pwd
            )
            pwd.tags = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.tags, pwd
            )
            pwd.custom_fields = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.custom_fields, pwd
            )
            pwd.folder = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.folder, pwd
            )
            pwd.password_history = self._reencrypt_optional(
                key_derivation, new_key_derivation, pwd.password_history, pwd
            )

        attachments = (
            await self.session.execute(select(PasswordAttachmentModel))
        ).scalars()
        for att in attachments:
            att.filename = self._reencrypt_binary(
                key_derivation, new_key_derivation, att.filename
            )
            att.content = self._reencrypt_binary(
                key_derivation, new_key_derivation, att.content
            )
            att.content_type = self._reencrypt_text(
                key_derivation, new_key_derivation, att.content_type
            )

        model.salt = new_salt
        model.hash_key = hash_master_password(new_master_password)
        self.session.add(model)
        await self.session.flush()

        return MasterPasswordUpdate(
            updated=True, detail="Master password updated successfully."
        )
