from sqlalchemy import select

from crud.base import BaseCRUD
from models.settings import SettingsModel
from schemas.settings import SettingsResponse, SettingsUpdate

_DEFAULTS = dict(
    inactivity_ms=120_000,
    warn_before_ms=60_000,
    hidden_ms=60_000,
    debounce_ms=1_000,
    clipboard_clear_ms=30_000,
)


class SettingsCRUD(BaseCRUD):
    async def _get_or_create(self) -> SettingsModel:
        model = (await self.session.execute(select(SettingsModel).limit(1))).scalar()
        if model is None:
            model = SettingsModel(**_DEFAULTS)
            self.session.add(model)
            await self.session.flush()
        return model

    @staticmethod
    def _to_response(model: SettingsModel) -> SettingsResponse:
        return SettingsResponse(
            inactivity_ms=model.inactivity_ms,
            warn_before_ms=model.warn_before_ms,
            hidden_ms=model.hidden_ms,
            debounce_ms=model.debounce_ms,
            clipboard_clear_ms=model.clipboard_clear_ms,
        )

    async def get_settings(self) -> SettingsResponse:
        return self._to_response(await self._get_or_create())

    async def update_settings(self, data: SettingsUpdate) -> SettingsResponse:
        model = await self._get_or_create()
        for field, value in data.model_dump().items():
            setattr(model, field, value)
        self.session.add(model)
        await self.session.flush()
        return self._to_response(model)
