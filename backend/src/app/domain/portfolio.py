from dataclasses import dataclass
from datetime import datetime

from app.domain.locale import Locale


@dataclass(frozen=True, slots=True)
class PortfolioItem:
    id: int
    category_id: int | None
    image_path: str
    sort_order: int
    is_published: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PortfolioItemTranslation:
    portfolio_item_id: int
    locale: Locale
    title: str
    description: str | None
