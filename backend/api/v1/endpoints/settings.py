from fastapi import APIRouter, Depends

from api.v1.endpoints.deps import get_settings_crud
from crud.settings import SettingsCRUD
from schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(tags=["settings"])


@router.get("", name="settings:get", response_model=SettingsResponse)
async def get_settings(
    crud: SettingsCRUD = Depends(get_settings_crud),
) -> SettingsResponse:
    return await crud.get_settings()


@router.patch("", name="settings:update", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdate,
    crud: SettingsCRUD = Depends(get_settings_crud),
) -> SettingsResponse:
    return await crud.update_settings(body)
