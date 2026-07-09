import io
import json

import pyzipper
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from crud.master_password import fetch_master_password
from helpers import (
    create_encrypted_zip,
    decrypt,
    encrypt,
    verify_master_password,
)
from models import PasswordModel
from schemas import (
    OnConflict,
    Password,
    PasswordCreate,
    PasswordDelete,
    PasswordImportResult,
    PasswordResponse,
    PasswordUpdate,
)

_MAX_JSON_BYTES = 50 * 1024 * 1024  # 50 MB


class PasswordCRUD(BaseCRUD):
    async def _get_password_model(self, password_name: str) -> PasswordModel:
        result = (
            await self.session.execute(
                select(PasswordModel).where(
                    PasswordModel.password_name == password_name
                )
            )
        ).scalar()
        if not result:
            raise NotFound(f"No password found for '{password_name}'.")
        return result

    def _decrypt_or_raise(self, key_derivation: str, model: PasswordModel) -> str:
        decrypted = decrypt(key_derivation, model.password_value)
        if decrypted is None:
            raise TypesMismatchError(f"Invalid key for '{model.password_name}'.")
        return decrypted

    def _to_response(
        self, model: PasswordModel, key_derivation: str
    ) -> PasswordResponse:
        return PasswordResponse(
            password_name=model.password_name,
            username=model.username,
            password_value=self._decrypt_or_raise(key_derivation, model),
            description=model.description,
            backed_up=model.backed_up,
        )

    async def _verify_master_password(self, master_password: str) -> None:
        mp_model = await fetch_master_password(self.session)
        if not mp_model:
            raise NotFound("No master password found.")

        if not verify_master_password(master_password, mp_model.hash_key):
            raise Forbidden("Incorrect master password.")

    async def get_passwords(self, key_derivation: str) -> list[PasswordResponse]:
        models = (
            await self.session.execute(
                select(PasswordModel).order_by(PasswordModel.password_name)
            )
        ).scalars()
        return [self._to_response(m, key_derivation) for m in models]

    async def get_password(
        self, password_name: str, key_derivation: str
    ) -> PasswordResponse:
        model = await self._get_password_model(password_name)
        return self._to_response(model, key_derivation)

    async def create_password(
        self, password: Password, key_derivation: str
    ) -> PasswordCreate:
        self.session.add(
            PasswordModel(
                password_name=password.password_name,
                username=password.username,
                password_value=encrypt(
                    key_derivation, password.password_value.encode()
                ),
                description=password.description,
            )
        )

        try:
            await self.session.flush()
        except IntegrityError as e:
            raise TypesMismatchError("A password with that name already exists.") from e
        return PasswordCreate(created=True, detail="Password created successfully.")

    async def update_password(
        self, password: Password, new_password: Password, key_derivation: str
    ) -> PasswordUpdate:
        model = await self._get_password_model(password.password_name)

        if model.password_name != new_password.password_name:
            conflict = (
                await self.session.execute(
                    select(PasswordModel).where(
                        PasswordModel.password_name == new_password.password_name
                    )
                )
            ).scalar()
            if conflict:
                raise TypesMismatchError("A password with that name already exists.")
            model.password_name = new_password.password_name

        decrypted = self._decrypt_or_raise(key_derivation, model)
        if decrypted != new_password.password_value:
            model.password_value = encrypt(
                key_derivation, new_password.password_value.encode()
            )

        if model.username != new_password.username:
            model.username = new_password.username

        if model.description != new_password.description:
            model.description = new_password.description

        model.backed_up = False
        await self.session.flush()
        return PasswordUpdate(updated=True, detail="Password updated successfully.")

    async def delete_password(self, password_name: str) -> PasswordDelete:
        model = await self._get_password_model(password_name)
        await self.session.delete(model)
        await self.session.flush()
        return PasswordDelete(deleted=True, detail="Password deleted successfully.")

    async def create_backup(self, master_password: str, key_derivation: str) -> bytes:
        await self._verify_master_password(master_password)

        passwords = (
            (
                await self.session.execute(
                    select(PasswordModel).order_by(PasswordModel.password_name)
                )
            )
            .scalars()
            .all()
        )

        entries = [
            {
                "name": p.password_name,
                "username": p.username,
                "value": self._decrypt_or_raise(key_derivation, p),
                "description": p.description,
            }
            for p in passwords
        ]

        for p in passwords:
            p.backed_up = True

        await self.session.flush()

        return create_encrypted_zip(entries, master_password)

    async def import_passwords(
        self,
        file_bytes: bytes,
        master_password: str,
        key_derivation: str,
        on_conflict: OnConflict,
    ) -> PasswordImportResult:
        await self._verify_master_password(master_password)

        try:
            with pyzipper.AESZipFile(io.BytesIO(file_bytes), "r") as zf:
                zf.setpassword(master_password.encode())
                with zf.open("dinopass_backup.json") as entry:
                    raw = entry.read(_MAX_JSON_BYTES + 1)
            if len(raw) > _MAX_JSON_BYTES:
                raise TypesMismatchError("Backup content is too large.")
        except TypesMismatchError:
            raise
        except Exception as e:
            raise TypesMismatchError(
                "Could not read backup file. Ensure it is a valid dinopass backup."
            ) from e

        try:
            entries = json.loads(raw)["passwords"]
            if not isinstance(entries, list):
                raise ValueError
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise TypesMismatchError("Invalid backup file format.") from e

        existing = {
            model.password_name: model
            for model in (await self.session.execute(select(PasswordModel))).scalars()
        }

        imported = skipped = overwritten = 0

        for entry in entries:
            try:
                name = entry["name"]
                value = entry["value"]
            except (KeyError, TypeError):
                continue

            if not name or not value:
                continue

            username = entry.get("username")
            description = entry.get("description")
            current = existing.get(name)

            if current:
                if on_conflict == OnConflict.skip:
                    skipped += 1
                else:
                    current.password_value = encrypt(key_derivation, value.encode())
                    current.username = username
                    current.description = description
                    current.backed_up = False
                    overwritten += 1
            else:
                model = PasswordModel(
                    password_name=name,
                    username=username,
                    password_value=encrypt(key_derivation, value.encode()),
                    description=description,
                )
                self.session.add(model)
                existing[name] = model
                imported += 1

        await self.session.flush()
        return PasswordImportResult(
            imported=imported,
            skipped=skipped,
            overwritten=overwritten,
            total=imported + skipped + overwritten,
        )
