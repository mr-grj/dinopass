import csv
import io
import json
from collections.abc import Sequence
from datetime import UTC, datetime

import pyzipper
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from api.exceptions import Forbidden, NotFound, TypesMismatchError
from crud.base import BaseCRUD
from crud.master_password import fetch_master_password
from helpers import (
    create_encrypted_zip,
    decrypt,
    decrypt_optional,
    encrypt,
    encrypt_optional,
    verify_master_password,
)
from models import PasswordAttachmentModel, PasswordModel
from schemas import (
    OnConflict,
    Password,
    PasswordCreate,
    PasswordDelete,
    PasswordImportResult,
    PasswordResponse,
    PasswordUpdate,
)
from validators import normalize_totp_secret

_MAX_JSON_BYTES = 50 * 1024 * 1024  # 50 MB
_HISTORY_LIMIT = 10

# Header aliases used when importing a plain CSV exported from another manager
# (Chrome, Bitwarden, KeePass, Proton Pass, ...). First matching column wins.
_CSV_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "name": ("name", "title", "account", "login_name", "item name"),
    "username": ("username", "login_username", "user", "email", "login", "e-mail"),
    "value": ("password", "login_password", "pass"),
    "url": ("url", "uri", "login_uri", "website", "web site", "site", "link"),
    "description": ("notes", "note", "description", "comment", "comments", "extra"),
    "folder": ("folder", "grouping", "group", "category", "collection"),
    "totp_secret": (
        "totp",
        "login_totp",
        "otpauth",
        "otp",
        "2fa",
        "otp_auth",
        "totpauth",
    ),
}


class PasswordCRUD(BaseCRUD):
    async def _get_password_model(
        self, password_name: str, *, deleted: bool = False
    ) -> PasswordModel:
        trashed = (
            PasswordModel.deleted.is_not(None)
            if deleted
            else PasswordModel.deleted.is_(None)
        )
        result = (
            await self.session.execute(
                select(PasswordModel).where(
                    PasswordModel.password_name == password_name,
                    trashed,
                )
            )
        ).scalar()
        if not result:
            where = "trash" if deleted else "vault"
            raise NotFound(f"No password found for '{password_name}' in the {where}.")
        return result

    def _decrypt_or_raise(self, key_derivation: str, model: PasswordModel) -> str:
        decrypted = decrypt(key_derivation, model.password_value)
        if decrypted is None:
            raise TypesMismatchError(f"Invalid key for '{model.password_name}'.")
        return decrypted

    @staticmethod
    def _encode_json(key_derivation: str, data: list) -> bytes | None:
        if not data:
            return None
        return encrypt(key_derivation, json.dumps(data).encode())

    @staticmethod
    def _decode_json_list(key_derivation: str, token: bytes | None) -> list:
        raw = decrypt_optional(key_derivation, token)
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    def _decode_tags(self, key_derivation: str, model: PasswordModel) -> list[str]:
        return self._decode_json_list(key_derivation, model.tags)

    def _decode_custom_fields(
        self, key_derivation: str, model: PasswordModel
    ) -> list[dict[str, object]]:
        return self._normalize_custom_fields(
            self._decode_json_list(key_derivation, model.custom_fields)
        )

    def _decode_history(
        self, key_derivation: str, model: PasswordModel
    ) -> list[dict[str, str]]:
        return self._decode_json_list(key_derivation, model.password_history)

    def _apply_fields(
        self,
        model: PasswordModel,
        key_derivation: str,
        *,
        kind: str,
        username: str | None,
        url: str | None,
        totp_secret: str | None,
        description: str | None,
        tags: list[str],
        custom_fields: list[dict[str, object]],
        folder: str | None,
        favorite: bool,
    ) -> None:
        """Write every shared (encrypted) column onto ``model``, except the
        password value and history, which each callsite handles itself."""
        model.kind = kind
        model.username = username
        model.url = encrypt_optional(key_derivation, url)
        model.totp_secret = encrypt_optional(key_derivation, totp_secret)
        model.description = description
        model.tags = self._encode_json(key_derivation, tags)
        model.custom_fields = self._encode_json(key_derivation, custom_fields)
        model.folder = encrypt_optional(key_derivation, folder)
        model.favorite = favorite

    def _to_response(
        self, model: PasswordModel, key_derivation: str, attachment_count: int = 0
    ) -> PasswordResponse:
        return PasswordResponse(
            password_name=model.password_name,
            kind=model.kind,
            username=model.username,
            password_value=self._decrypt_or_raise(key_derivation, model),
            url=decrypt_optional(key_derivation, model.url),
            totp_secret=decrypt_optional(key_derivation, model.totp_secret),
            description=model.description,
            tags=self._decode_tags(key_derivation, model),
            custom_fields=self._decode_custom_fields(key_derivation, model),
            folder=decrypt_optional(key_derivation, model.folder),
            favorite=model.favorite,
            backed_up=model.backed_up,
            updated=model.updated,
            deleted=model.deleted,
            password_history=self._decode_history(key_derivation, model),
            attachment_count=attachment_count,
        )

    async def _attachment_counts(self, password_ids: list[int]) -> dict[int, int]:
        if not password_ids:
            return {}
        rows = (
            await self.session.execute(
                select(
                    PasswordAttachmentModel.password_id,
                    func.count(),
                )
                .where(PasswordAttachmentModel.password_id.in_(password_ids))
                .group_by(PasswordAttachmentModel.password_id)
            )
        ).all()
        return {password_id: count for password_id, count in rows}

    async def _verify_master_password(self, master_password: str) -> None:
        mp_model = await fetch_master_password(self.session)
        if not mp_model:
            raise NotFound("No master password found.")

        if not verify_master_password(master_password, mp_model.hash_key):
            raise Forbidden("Incorrect master password.")

    async def get_passwords(self, key_derivation: str) -> list[PasswordResponse]:
        models = list(
            (
                await self.session.execute(
                    select(PasswordModel)
                    .where(PasswordModel.deleted.is_(None))
                    .order_by(PasswordModel.password_name)
                )
            ).scalars()
        )
        counts = await self._attachment_counts([m.id for m in models])
        return [
            self._to_response(m, key_derivation, counts.get(m.id, 0)) for m in models
        ]

    async def get_trash(self, key_derivation: str) -> list[PasswordResponse]:
        models = list(
            (
                await self.session.execute(
                    select(PasswordModel)
                    .where(PasswordModel.deleted.is_not(None))
                    .order_by(PasswordModel.deleted.desc())
                )
            ).scalars()
        )
        counts = await self._attachment_counts([m.id for m in models])
        return [
            self._to_response(m, key_derivation, counts.get(m.id, 0)) for m in models
        ]

    async def get_password(
        self, password_name: str, key_derivation: str
    ) -> PasswordResponse:
        model = await self._get_password_model(password_name)
        return self._to_response(model, key_derivation)

    async def create_password(
        self, password: Password, key_derivation: str
    ) -> PasswordCreate:
        model = PasswordModel(
            password_name=password.password_name,
            password_value=encrypt(key_derivation, password.password_value.encode()),
        )
        self._apply_fields(
            model,
            key_derivation,
            kind=password.kind,
            username=password.username,
            url=password.url,
            totp_secret=password.totp_secret,
            description=password.description,
            tags=password.tags,
            custom_fields=[f.model_dump() for f in password.custom_fields],
            folder=password.folder,
            favorite=password.favorite,
        )
        self.session.add(model)

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
                        PasswordModel.password_name == new_password.password_name,
                        PasswordModel.deleted.is_(None),
                    )
                )
            ).scalar()
            if conflict:
                raise TypesMismatchError("A password with that name already exists.")
            model.password_name = new_password.password_name

        old_value = self._decrypt_or_raise(key_derivation, model)
        if old_value != new_password.password_value:
            if new_password.kind == "login":
                history = self._decode_history(key_derivation, model)
                history.insert(
                    0,
                    {"value": old_value, "changed_at": datetime.now(UTC).isoformat()},
                )
                del history[_HISTORY_LIMIT:]
                model.password_history = encrypt(
                    key_derivation, json.dumps(history).encode()
                )
            model.password_value = encrypt(
                key_derivation, new_password.password_value.encode()
            )

        self._apply_fields(
            model,
            key_derivation,
            kind=new_password.kind,
            username=new_password.username,
            url=new_password.url,
            totp_secret=new_password.totp_secret,
            description=new_password.description,
            tags=new_password.tags,
            custom_fields=[f.model_dump() for f in new_password.custom_fields],
            folder=new_password.folder,
            favorite=new_password.favorite,
        )

        model.backed_up = False
        await self.session.flush()
        return PasswordUpdate(updated=True, detail="Password updated successfully.")

    async def set_favorite(self, password_name: str, favorite: bool) -> PasswordUpdate:
        model = await self._get_password_model(password_name)
        model.favorite = favorite
        await self.session.flush()
        detail = "Added to favorites." if favorite else "Removed from favorites."
        return PasswordUpdate(updated=True, detail=detail)

    async def delete_password(self, password_name: str) -> PasswordDelete:
        model = await self._get_password_model(password_name)
        model.deleted = datetime.now(UTC).replace(tzinfo=None)

        await self.session.flush()

        return PasswordDelete(deleted=True, detail="Password moved to trash.")

    async def restore_password(self, password_name: str) -> PasswordUpdate:
        model = await self._get_password_model(password_name, deleted=True)
        conflict = (
            await self.session.execute(
                select(PasswordModel).where(
                    PasswordModel.password_name == password_name,
                    PasswordModel.deleted.is_(None),
                )
            )
        ).scalar()
        if conflict:
            raise TypesMismatchError(
                f"An active password named '{password_name}' already exists. "
                "Rename or delete it before restoring."
            )
        model.deleted = None
        await self.session.flush()
        return PasswordUpdate(updated=True, detail="Password restored from trash.")

    async def purge_password(self, password_name: str) -> PasswordDelete:
        model = await self._get_password_model(password_name, deleted=True)
        await self.session.delete(model)
        await self.session.flush()
        return PasswordDelete(deleted=True, detail="Password permanently deleted.")

    async def create_backup(self, master_password: str, key_derivation: str) -> bytes:
        await self._verify_master_password(master_password)

        passwords = (
            (
                await self.session.execute(
                    select(PasswordModel)
                    .where(PasswordModel.deleted.is_(None))
                    .order_by(PasswordModel.password_name)
                )
            )
            .scalars()
            .all()
        )

        entries: list[dict[str, object]] = [
            {
                "name": p.password_name,
                "kind": p.kind,
                "username": p.username,
                "value": self._decrypt_or_raise(key_derivation, p),
                "url": decrypt_optional(key_derivation, p.url),
                "totp_secret": decrypt_optional(key_derivation, p.totp_secret),
                "description": p.description,
                "tags": self._decode_tags(key_derivation, p),
                "custom_fields": self._decode_custom_fields(key_derivation, p),
                "folder": decrypt_optional(key_derivation, p.folder),
                "favorite": p.favorite,
            }
            for p in passwords
        ]

        for p in passwords:
            p.backed_up = True

        await self.session.flush()

        return create_encrypted_zip(entries, master_password)

    def _upsert_entry(
        self,
        *,
        existing: dict[str, PasswordModel],
        key_derivation: str,
        on_conflict: OnConflict,
        name: str,
        value: str,
        kind: str,
        username: str | None,
        url: str | None,
        totp_secret: str | None,
        description: str | None,
        tags: list[str],
        custom_fields: list[dict[str, object]],
        folder: str | None,
        favorite: bool,
    ) -> str:
        current = existing.get(name)
        if current is None:
            current = PasswordModel(password_name=name)
            self.session.add(current)
            existing[name] = current
            outcome = "imported"
        elif on_conflict == OnConflict.skip:
            return "skipped"
        else:
            outcome = "overwritten"

        current.password_value = encrypt(key_derivation, value.encode())
        self._apply_fields(
            current,
            key_derivation,
            kind=kind,
            username=username,
            url=url,
            totp_secret=totp_secret,
            description=description,
            tags=tags,
            custom_fields=custom_fields,
            folder=folder,
            favorite=favorite,
        )
        if outcome == "overwritten":
            current.backed_up = False

        return outcome

    async def _load_existing(self) -> dict[str, PasswordModel]:
        return {
            model.password_name: model
            for model in (
                await self.session.execute(
                    select(PasswordModel).where(PasswordModel.deleted.is_(None))
                )
            ).scalars()
        }

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
                with zf.open("ciphermoth_backup.json") as entry:
                    raw = entry.read(_MAX_JSON_BYTES + 1)
            if len(raw) > _MAX_JSON_BYTES:
                raise TypesMismatchError("Backup content is too large.")
        except TypesMismatchError:
            raise
        except Exception as e:
            raise TypesMismatchError(
                "Could not read backup file. Ensure it is a valid ciphermoth backup."
            ) from e

        try:
            entries = json.loads(raw)["passwords"]
            if not isinstance(entries, list):
                raise ValueError
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise TypesMismatchError("Invalid backup file format.") from e

        existing = await self._load_existing()
        counts = {"imported": 0, "skipped": 0, "overwritten": 0}

        for entry in entries:
            try:
                name = entry["name"]
                value = entry["value"]
            except (KeyError, TypeError):
                continue
            if not name or not value:
                continue

            raw_tags = entry.get("tags")
            outcome = self._upsert_entry(
                existing=existing,
                key_derivation=key_derivation,
                on_conflict=on_conflict,
                name=name,
                value=value,
                kind="note" if entry.get("kind") == "note" else "login",
                username=entry.get("username"),
                url=entry.get("url"),
                totp_secret=entry.get("totp_secret"),
                description=entry.get("description"),
                tags=raw_tags if isinstance(raw_tags, list) else [],
                custom_fields=self._normalize_custom_fields(entry.get("custom_fields")),
                folder=entry.get("folder"),
                favorite=bool(entry.get("favorite", False)),
            )
            counts[outcome] += 1

        await self.session.flush()
        return self._result(counts)

    async def import_passwords_csv(
        self,
        file_bytes: bytes,
        key_derivation: str,
        on_conflict: OnConflict,
    ) -> PasswordImportResult:
        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as e:
            raise TypesMismatchError("CSV file must be UTF-8 encoded.") from e

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise TypesMismatchError("CSV file has no header row.")

        column_for = self._map_csv_columns(reader.fieldnames)
        if "name" not in column_for or "value" not in column_for:
            raise TypesMismatchError(
                "CSV must have a name/title column and a password column."
            )

        existing = await self._load_existing()
        counts = {"imported": 0, "skipped": 0, "overwritten": 0}

        for row in reader:
            name = (row.get(column_for["name"]) or "").strip()
            value = row.get(column_for["value"]) or ""
            if not name or not value:
                continue

            outcome = self._upsert_entry(
                existing=existing,
                key_derivation=key_derivation,
                on_conflict=on_conflict,
                name=name,
                value=value,
                kind="login",
                username=self._csv_cell(row, column_for, "username"),
                url=self._csv_cell(row, column_for, "url"),
                totp_secret=self._csv_totp(row, column_for),
                description=self._csv_cell(row, column_for, "description"),
                tags=[],
                custom_fields=[],
                folder=self._csv_cell(row, column_for, "folder"),
                favorite=False,
            )
            counts[outcome] += 1

        await self.session.flush()
        return self._result(counts)

    @staticmethod
    def _normalize_custom_fields(raw: object) -> list[dict[str, object]]:
        if not isinstance(raw, list):
            return []
        fields: list[dict[str, object]] = []
        for item in raw:
            if isinstance(item, dict) and item.get("label"):
                fields.append(
                    {
                        "label": str(item.get("label")),
                        "value": str(item.get("value", "")),
                        "hidden": bool(item.get("hidden", False)),
                    }
                )
        return fields

    @staticmethod
    def _map_csv_columns(fieldnames: Sequence[str]) -> dict[str, str]:
        normalized = {(name or "").strip().lower(): name for name in fieldnames}
        column_for: dict[str, str] = {}
        for field, aliases in _CSV_FIELD_ALIASES.items():
            for alias in aliases:
                if alias in normalized:
                    column_for[field] = normalized[alias]
                    break
        return column_for

    @staticmethod
    def _csv_cell(
        row: dict[str, str], column_for: dict[str, str], field: str
    ) -> str | None:
        column = column_for.get(field)
        if not column:
            return None
        value = (row.get(column) or "").strip()
        return value or None

    @staticmethod
    def _csv_totp(row: dict[str, str], column_for: dict[str, str]) -> str | None:
        raw = PasswordCRUD._csv_cell(row, column_for, "totp_secret")
        try:
            return normalize_totp_secret(raw)
        except ValueError:
            return None

    @staticmethod
    def _result(counts: dict[str, int]) -> PasswordImportResult:
        return PasswordImportResult(
            imported=counts["imported"],
            skipped=counts["skipped"],
            overwritten=counts["overwritten"],
            total=counts["imported"] + counts["skipped"] + counts["overwritten"],
        )
