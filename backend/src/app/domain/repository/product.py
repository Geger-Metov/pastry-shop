from typing import Protocol

from app.domain.locale import Locale
from app.domain.product import LocalizedProduct


class ProductRepository(Protocol):
    """Контракт доступа к товарам витрины. Реализация - в infrastructure/persistence/repositories.

    Витрина видит только активные товары в активной категории, у которых есть перевод
    (на запрошенный язык или на язык по умолчанию) и хотя бы один активный вариант (без него
    нет цены). Варианты, картинки и аллергены уже загружены в результат.
    """

    async def list_active(self, locale: Locale) -> list[LocalizedProduct]:
        """Все товары витрины по sort_order, затем id."""
        ...

    async def list_active_by_category(
        self, category_slug: str, locale: Locale
    ) -> list[LocalizedProduct]:
        """Товары одной категории. Неизвестная или неактивная категория - пустой список."""
        ...

    async def get_active_by_slug(self, slug: str, locale: Locale) -> LocalizedProduct | None:
        """Один товар или None, если такого нет (или он не виден на витрине)."""
        ...
