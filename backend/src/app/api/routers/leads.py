from fastapi import APIRouter, status

from app.api.dependencies import CreateLeadDep
from app.api.schemas import LeadCreated, LeadIn
from app.use_cases.leads import CreateLeadCommand

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadIn, use_case: CreateLeadDep) -> LeadCreated:
    # Поля переносим явно, а не через **payload.model_dump(): так mypy заметит, если поле
    # добавили в LeadIn, но забыли в команде (с ** это ошибка только во время запроса).
    command = CreateLeadCommand(
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
    lead = await use_case.execute(command)
    return LeadCreated(id=lead.id)
