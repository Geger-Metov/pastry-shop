from fastapi import APIRouter, status

from app.api.dependencies import CreateLeadDep
from app.api.schemas import LeadCreated, LeadIn
from app.domain.lead import NewLead

router = APIRouter(prefix="leads", tags=["leads"])


@router.post("", response_model=LeadCreated, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadIn, use_case: CreateLeadDep) -> LeadCreated:
    lead = await use_case.execute(
        NewLead(
            name=payload.name,
            phone=payload.phone,
            email=payload.email,
            comment=payload.comment,
            desired_date=payload.desired_date,
            servings=payload.servings,
            budget=payload.budget,
            decor=payload.decor,
            design_description=payload.design_description,
        )
    )
    return LeadCreated(id=lead.id)
