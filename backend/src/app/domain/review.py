from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Review:
    """Отзыв на магазин (product_id is None) или на товар. Показывается после модерации."""

    id: int
    customer_id: int | None
    order_id: int | None
    product_id: int | None
    author_name: str
    rating: int
    body: str
    is_published: bool
    created_at: datetime

    def __post_init__(self) -> None:
        if not 1 <= self.rating <= 5:
            raise ValueError("rating должен быть от 1 до 5")
