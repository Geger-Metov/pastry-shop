from fastapi import APIRouter

from app.api.dependencies import SettingsDep
from app.api.schemas import ShopOut

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("")
async def get_shop_currency(settings: SettingsDep) -> ShopOut:
    return ShopOut(currency=settings.shop_currency)
