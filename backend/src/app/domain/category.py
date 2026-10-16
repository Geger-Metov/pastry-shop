from dataclasses import dataclass

from app.domain.locale import Locale


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    parent_id: int | None
    slug: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class CategoryTranslation:
    category_id: int
    locale: Locale
    name: str
    description: str | None
