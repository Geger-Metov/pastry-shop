from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.lead import Lead, NewLead
from app.infrastructure.persistence.model.lead import LeadModel


def to_domain(lead: LeadModel) -> Lead:
    return Lead(
        id=lead.id,
        status=lead.status,
        customer_id=lead.customer_id,
        converted_order_id=lead.converted_order_id,
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        comment=lead.comment,
        desired_date=lead.desired_date,
        servings=lead.servings,
        budget=lead.budget,
        decor=lead.decor,
        design_description=lead.design_description,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


class SqlLeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, new_lead: NewLead) -> Lead:
        model = LeadModel(
            name=new_lead.name,
            phone=new_lead.phone,
            email=new_lead.email,
            comment=new_lead.comment,
            desired_date=new_lead.desired_date,
            servings=new_lead.servings,
            budget=new_lead.budget,
            decor=new_lead.decor,
            design_description=new_lead.design_description,
        )
        self._session.add(model)
        await self._session.flush()
        return to_domain(model)
