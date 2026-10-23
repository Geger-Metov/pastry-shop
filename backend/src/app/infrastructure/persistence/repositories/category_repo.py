from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.category import Category, LocalizedCategory
from app.domain.locale import DEFAULT_LOCALE, Locale, parse_locale
from app.infrastructure.persistence.model.category import CategoryModel, CategoryTranslationModel

# type _Row = tuple[CategoryModel, CategoryTranslationModel, CategoryTranslationModel]


def _to_category(model: CategoryModel) -> Category:
    return Category(
        id=model.id,
        parent_id=model.parent_id,
        slug=model.slug,
        sort_order=model.sort_order,
        is_active=model.is_active,
    )


def _to_localized(
    category: CategoryModel,
    requested: CategoryTranslationModel | None,
    fallback: CategoryTranslationModel | None,
) -> LocalizedCategory:
    # перевод на запрошенный язык важнее; иначе язык по умолчанию
    translation = requested or fallback

    if translation is None:  # SQL это уже отфильтровал; защита от будущих правок запроса
        raise LookupError(f"Category {category.id} has no usable translation")
    return LocalizedCategory(
        category=_to_category(category),
        locale=parse_locale(translation.locale),
        name=translation.name,
        description=translation.description,
    )


def _active_localized_select(
    locale: Locale,
) -> Select[CategoryModel, CategoryTranslationModel, CategoryTranslationModel]:
    """Категории + перевод на нужный язык + перевод на язык по умолчанию (оба LEFT JOIN).

    Одним запросом, без N+1: язык выбирается в Python (см. _to_localized).
    """
    requested = aliased(CategoryTranslationModel)
    fallback = aliased(CategoryTranslationModel)
    return (
        select(CategoryModel, requested, fallback)
        .outerjoin(
            requested,
            and_(requested.category_id == CategoryModel.id, requested.locale == locale),
        )
        .outerjoin(
            fallback,
            and_(fallback.category_id == CategoryModel.id, fallback.locale == DEFAULT_LOCALE),
        )
        .where(
            CategoryModel.is_active,
            # хотя бы какой-то перевод должен быть
            or_(requested.category_id.is_not(None), fallback.category_id.is_not(None)),
        )
    )


class SqlCategoryRepository:
    """Реализация CategoryRepository (domain/repository/category.py) на SQLAlchemy.

    Сессию получает снаружи и НЕ коммитит.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self, locale: Locale) -> list[LocalizedCategory]:
        stmt = _active_localized_select(locale).order_by(CategoryModel.sort_order, CategoryModel.id)
        rows = (await self._session.execute(stmt)).all()
        return [_to_localized(*row) for row in rows]

    async def get_active_by_slug(self, slug: str, locale: Locale) -> LocalizedCategory | None:
        stmt = _active_localized_select(locale).where(CategoryModel.slug == slug)
        row = (await self._session.execute(stmt)).first()
        return _to_localized(*row) if row is not None else None
