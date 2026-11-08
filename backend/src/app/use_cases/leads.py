from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from app.domain.lead import Lead, NewLead
from app.domain.money import Money
from app.domain.phone import normalize_phone
from app.domain.repository.lead import LeadRepository
from app.domain.repository.unit_of_work import UnitOfWork


class LeadInputError(ValueError):
    """Данные заявки не подходят. field - имя поля формы (для сообщения под полем)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


@dataclass(frozen=True, slots=True)
class CreateLeadCommand:
    """Что пришло от клиента. Телефон - ровно как ввёл пользователь (ещё не E.164)."""

    name: str
    phone: str
    email: str | None = None
    comment: str | None = None
    desired_date: date | None = None
    servings: int | None = None
    budget: Money | None = None
    decor: str | None = None
    design_description: str | None = None


class CreateLead:
    """Сценарий "клиент оставил заявку": проверить, нормализовать, сохранить, закоммитить."""

    def __init__(
        self,
        leads: LeadRepository,
        uow: UnitOfWork,
        *,
        default_country_code: str | None,
        today: Callable[[], date] = date.today,  # подменяется в тестах
    ) -> None:
        self._leads = leads
        self._uow = uow
        self._default_country_code = default_country_code
        self._today = today

    async def execute(self, command: CreateLeadCommand) -> Lead:
        try:
            phone = normalize_phone(command.phone, self._default_country_code)
        except ValueError as exc:
            raise LeadInputError("Некорректный номер телефона", field="phone") from exc

        if command.desired_date is not None and command.desired_date < self._today():
            raise LeadInputError("Дата не может быть в прошлом", field="desired_date")

        try:
            new_lead = NewLead(
                name=command.name,
                phone=phone,
                email=command.email,
                comment=command.comment,
                desired_date=command.desired_date,
                servings=command.servings,
                budget=command.budget,
                decor=command.decor,
                design_description=command.design_description,
            )
        except ValueError as exc:  # правила домена, которые не поймала схема API
            raise LeadInputError(str(exc)) from exc

        lead = await self._leads.add(new_lead)
        await self._uow.commit()  # одна заявка - один commit, и только после успешного add
        return lead
