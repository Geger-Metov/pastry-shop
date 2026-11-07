from app.domain.lead import Lead, NewLead
from app.domain.phone import normalize_phone
from app.domain.repository.lead import LeadRepository


class CreateLead:
    def __init__(self, repo: LeadRepository) -> None:
        self.repo = repo

    async def execute(self, new_lead: NewLead) -> Lead:
        phone = normalize_phone(new_lead.phone)
        normalized_lead = NewLead(
            name=new_lead.name,
            phone=phone,
            email=new_lead.email,
            comment=new_lead.comment,
            desired_date=new_lead.desired_date,
            servings=new_lead.servings,
            budget=new_lead.budget,
            decor=new_lead.decor,
            design_description=new_lead.design_description,
        )
        return await self.repo.add(normalized_lead)
