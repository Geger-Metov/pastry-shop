from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.domain.lead import Lead, LeadStatus, NewLead
from app.use_cases.leads import CreateLead, CreateLeadCommand, LeadInputError

TODAY = date(2026, 11, 7)


class FakeLeadRepository:
    def __init__(self, events: list[str]) -> None:
        self.added: list[NewLead] = []
        self._events = events

    async def add(self, new_lead: NewLead) -> Lead:
        self._events.append("add")
        self.added.append(new_lead)
        return Lead(
            id=1,
            status=LeadStatus.NEW,
            customer_id=None,
            converted_order_id=None,
            name=new_lead.name,
            phone=new_lead.phone,
            email=new_lead.email,
            comment=new_lead.comment,
            desired_date=new_lead.desired_date,
            servings=new_lead.servings,
            budget=new_lead.budget,
            decor=new_lead.decor,
            design_description=new_lead.design_description,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


class FakeUnitOfWork:
    def __init__(self, events: list[str]) -> None:
        self.commits = 0
        self._events = events

    async def commit(self) -> None:
        self._events.append("commit")
        self.commits += 1


def make_use_case(
    *, default_country_code: str | None = "996"
) -> tuple[CreateLead, FakeLeadRepository, FakeUnitOfWork, list[str]]:
    events: list[str] = []
    repository = FakeLeadRepository(events)
    uow = FakeUnitOfWork(events)
    use_case = CreateLead(
        repository, uow, default_country_code=default_country_code, today=lambda: TODAY
    )
    return use_case, repository, uow, events


async def test_saves_then_commits_once() -> None:
    use_case, repository, uow, events = make_use_case()

    lead = await use_case.execute(CreateLeadCommand(name="Анна", phone="+996555123456"))

    assert lead.id == 1
    assert events == ["add", "commit"]  # commit строго после add
    assert uow.commits == 1
    assert len(repository.added) == 1


async def test_national_phone_uses_default_country_code() -> None:
    use_case, repository, _, _ = make_use_case(default_country_code="996")

    await use_case.execute(CreateLeadCommand(name="Анна", phone="0555 123 456"))

    assert repository.added[0].phone == "+996555123456"


async def test_national_phone_without_default_country_code_is_rejected() -> None:
    use_case, repository, uow, _ = make_use_case(default_country_code=None)

    with pytest.raises(LeadInputError) as error:
        await use_case.execute(CreateLeadCommand(name="Анна", phone="0555123456"))

    assert error.value.field == "phone"
    assert repository.added == []
    assert uow.commits == 0


async def test_past_desired_date_is_rejected_and_nothing_is_saved() -> None:
    use_case, repository, uow, _ = make_use_case()

    with pytest.raises(LeadInputError) as error:
        await use_case.execute(
            CreateLeadCommand(name="Анна", phone="+996555123456", desired_date=date(2026, 11, 6))
        )

    assert error.value.field == "desired_date"
    assert repository.added == []
    assert uow.commits == 0


async def test_today_is_allowed() -> None:
    use_case, repository, _, _ = make_use_case()

    await use_case.execute(
        CreateLeadCommand(name="Анна", phone="+996555123456", desired_date=TODAY)
    )

    assert repository.added[0].desired_date == TODAY


async def test_domain_rule_violation_becomes_lead_input_error() -> None:
    use_case, repository, uow, _ = make_use_case()

    with pytest.raises(LeadInputError):
        await use_case.execute(
            CreateLeadCommand(name="Анна", phone="+996555123456", budget=Decimal("-1"))
        )

    assert repository.added == []
    assert uow.commits == 0


async def test_no_commit_if_repository_fails() -> None:
    use_case, repository, uow, _ = make_use_case()

    async def broken_add(new_lead: NewLead) -> Lead:
        raise RuntimeError("database is down")

    repository.add = broken_add  # type: ignore[method-assign]

    with pytest.raises(RuntimeError):
        await use_case.execute(CreateLeadCommand(name="Анна", phone="+996555123456"))

    assert uow.commits == 0
