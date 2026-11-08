from fastapi import APIRouter, status

from app.api.dependencies import CreateLeadDep
from app.api.schemas import LeadCreated, LeadIn
from app.use_cases.leads import CreateLeadCommand

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadIn, use_case: CreateLeadDep) -> LeadCreated:
    lead = await use_case.execute(CreateLeadCommand(**payload.model_dump()))
    return LeadCreated(id=lead.id)
