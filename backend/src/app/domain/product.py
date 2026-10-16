from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    category_id: int
    name: str
    description: str
    weight: int
    price: float
    image_path: str
    is_active: bool
