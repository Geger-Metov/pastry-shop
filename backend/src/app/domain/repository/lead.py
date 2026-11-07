from typing import Protocol

from app.domain.lead import Lead, NewLead


class LeadRepository(Protocol):
    async def add(self, new_lead: NewLead) -> Lead: ...
