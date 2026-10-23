from typing import Protocol

from app.domain.category import LocalizedCategory
from app.domain.locale import Locale


class CategoryRepository(Protocol):
    """Контракт доступа к категориям. Реализация - в infrastructure/persistence/repository."""

    async def list_active(self, locale: Locale) -> list[LocalizedCategory]:
        """Активные категории по sort_order. Без перевода (даже на язык по умолчанию) - пропуск."""
        ...

    async def get_active_by_slug(self, slug: str, locale: Locale) -> LocalizedCategory | None:
        """Одна активная категория или None, если такой нет (или она неактивна)."""
        ...
