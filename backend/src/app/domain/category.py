from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    parent_id: int
    code: str
