from dataclasses import dataclass
from datetime import datetime

from app.domain.allergen import Allergen
from app.domain.locale import Locale
from app.domain.money import Money


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    category_id: int
    slug: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProductTranslation:
    product_id: int
    locale: Locale
    name: str
    description: str | None


@dataclass(frozen=True, slots=True)
class ProductVariant:
    """Размер/набор товара. Цена хранится здесь, а не в Product."""

    id: int
    product_id: int
    weight_g: int | None
    pieces: int | None
    price: Money
    sort_order: int
    is_active: bool

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price не может быть отрицательной")
        if self.weight_g is not None and self.weight_g <= 0:
            raise ValueError("weight_g должен быть > 0")
        if self.pieces is not None and self.pieces <= 0:
            raise ValueError("pieces должен быть > 0")


@dataclass(frozen=True, slots=True)
class ProductImage:
    id: int
    product_id: int
    path: str
    sort_order: int


@dataclass(frozen=True, slots=True)
class LocalizedProduct:
    """Товар для витрины: название на одном языке + варианты, картинки и аллергены.

    `locale` - язык, на котором РЕАЛЬНО вернулись name и description (может быть языком по
    умолчанию, если перевода на запрошенный нет). Коллекции - tuple, потому что dataclass frozen.
    """

    product: Product
    locale: Locale
    name: str
    description: str | None
    variants: tuple[ProductVariant, ...]
    images: tuple[ProductImage, ...]
    allergens: tuple[Allergen, ...]
