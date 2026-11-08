from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.lead import LeadStatus, NewLead
from app.domain.repository.lead import LeadRepository
from app.infrastructure.persistence.model.lead import LeadModel
from app.infrastructure.persistence.repositories.lead_repo import SqlLeadRepository


def make_repository(session: AsyncSession) -> LeadRepository:
    return SqlLeadRepository(session)


async def test_add_returns_saved_lead_with_database_values(session: AsyncSession) -> None:
    lead = await make_repository(session).add(NewLead(name="Анна", phone="+996555123456"))

    assert lead.id > 0
    assert lead.status is LeadStatus.NEW  # значение по умолчанию задала БД
    assert lead.customer_id is None
    assert lead.converted_order_id is None
    assert lead.created_at is not None
    assert lead.updated_at is not None


async def test_add_stores_every_field(session: AsyncSession) -> None:
    new_lead = NewLead(
        name="Анна",
        phone="+996555123456",
        email="anna@example.com",
        comment="Без орехов",
        desired_date=date(2030, 5, 1),
        servings=12,
        budget=Decimal("7500.50"),
        decor="Ягоды",
        design_description="Двухъярусный торт",
    )

    lead = await make_repository(session).add(new_lead)

    row = (await session.execute(select(LeadModel).where(LeadModel.id == lead.id))).scalar_one()
    assert (row.name, row.phone, row.email, row.comment) == (
        "Анна",
        "+996555123456",
        "anna@example.com",
        "Без орехов",
    )
    assert (row.desired_date, row.servings, row.budget) == (
        date(2030, 5, 1),
        12,
        Decimal("7500.50"),
    )
    assert (row.decor, row.design_description) == ("Ягоды", "Двухъярусный торт")
    assert (lead.servings, lead.budget, lead.email) == (12, Decimal("7500.50"), "anna@example.com")


async def test_two_leads_get_different_ids(session: AsyncSession) -> None:
    repository = make_repository(session)

    first = await repository.add(NewLead(name="Анна", phone="+996555123456"))
    second = await repository.add(NewLead(name="Борис", phone="+996555654321"))

    assert first.id != second.id
    count = (await session.execute(select(func.count()).select_from(LeadModel))).scalar_one()
    assert count == 2
