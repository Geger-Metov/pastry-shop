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


@dataclass(frozen=True, slots=True)
class LocalizedCategory:
    """Категория с названием на одном языке: read model для API витрины.

    `locale` - язык, на котором РЕАЛЬНО вернулись name и description. Он может отличаться
    от запрошенного: если перевода на нужный язык нет, берётся язык по умолчанию.
    """

    category: Category
    locale: Locale
    name: str
    description: str | None
