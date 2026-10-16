from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Allergen:
    id: int
    code: str
