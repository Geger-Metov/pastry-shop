"""Зависимости FastAPI: здесь (и только здесь) контракты связываются с реализациями."""

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.locale import DEFAULT_LOCALE, Locale, parse_locale
from app.domain.repository.category import CategoryRepository
from app.domain.repository.lead import LeadRepository
from app.domain.repository.product import ProductRepository
from app.infrastructure.database.session import get_session
from app.infrastructure.persistence.repositories.category_repo import SqlCategoryRepository
from app.infrastructure.persistence.repositories.lead_repo import SqlLeadRepository
from app.infrastructure.persistence.repositories.product_repo import SqlProductRepository
from app.use_cases.leads import CreateLead

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_locale(
    locale: Annotated[str | None, Query(description="Язык ответа: ru, en или fr")] = None,
) -> Locale:
    """Язык из ?locale=. Нет параметра или язык не поддерживается - язык по умолчанию."""
    if locale is None:
        return DEFAULT_LOCALE
    try:
        return parse_locale(locale)
    except ValueError:
        return DEFAULT_LOCALE


def get_category_repository(session: SessionDep) -> CategoryRepository:
    return SqlCategoryRepository(session)


def get_product_repository(session: SessionDep) -> ProductRepository:
    return SqlProductRepository(session)


def get_lead_repository(session: SessionDep) -> LeadRepository:
    return SqlLeadRepository(session)


def get_create_lead(session: SessionDep) -> CreateLead:
    return CreateLead(SqlLeadRepository(session))


LocaleDep = Annotated[Locale, Depends(get_locale)]
CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]
ProductRepositoryDep = Annotated[ProductRepository, Depends(get_product_repository)]
LeadRepositoryDep = Annotated[LeadRepository, Depends(get_lead_repository)]
CreateLeadDep = Annotated[CreateLead, Depends(get_create_lead)]
