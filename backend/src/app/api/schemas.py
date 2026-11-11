"""Схемы ответов API. Отдельно от domain: контракт API не должен меняться вместе с моделью."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.domain.allergen import Allergen
from app.domain.category import LocalizedCategory
from app.domain.email import is_valid_email
from app.domain.locale import Locale
from app.domain.product import LocalizedProduct, ProductImage, ProductVariant


class CategoryOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    parent_id: int | None
    slug: str
    name: str
    description: str | None
    # язык, на котором РЕАЛЬНО пришли name и description (может отличаться от запрошенного)
    locale: Locale

    @classmethod
    def from_domain(cls, item: LocalizedCategory) -> Self:
        return cls(
            id=item.category.id,
            parent_id=item.category.parent_id,
            slug=item.category.slug,
            name=item.name,
            description=item.description,
            locale=item.locale,
        )


class VariantOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    weight_g: int | None
    pieces: int | None
    # Decimal в JSON превращается в строку ("1300.50"), а не во float: деньги не теряют точность
    price: Decimal

    @classmethod
    def from_domain(cls, variant: ProductVariant) -> Self:
        return cls(
            id=variant.id,
            weight_g=variant.weight_g,
            pieces=variant.pieces,
            price=variant.price,
        )


class ImageOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    path: str

    @classmethod
    def from_domain(cls, image: ProductImage) -> Self:
        return cls(id=image.id, path=image.path)


class AllergenOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    code: str

    @classmethod
    def from_domain(cls, allergen: Allergen) -> Self:
        return cls(id=allergen.id, code=allergen.code)


class ProductOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    category_id: int
    slug: str
    name: str
    description: str | None
    locale: Locale
    variants: list[VariantOut]
    images: list[ImageOut]
    allergens: list[AllergenOut]

    @classmethod
    def from_domain(cls, item: LocalizedProduct) -> Self:
        return cls(
            id=item.product.id,
            category_id=item.product.category_id,
            slug=item.product.slug,
            name=item.name,
            description=item.description,
            locale=item.locale,
            variants=[VariantOut.from_domain(v) for v in item.variants],
            images=[ImageOut.from_domain(i) for i in item.images],
            allergens=[AllergenOut.from_domain(a) for a in item.allergens],
        )


# strip_whitespace срабатывает ДО проверки длины: "   " не пройдёт min_length
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
# Только "разумный размер": нормализация в E.164 - в сценарии CreateLead (ей нужна
# настройка phone_default_country_code)
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32)]


class LeadIn(BaseModel):
    """Форма заявки. Статус, id и даты клиент не передаёт: их задаёт сервер."""

    model_config = ConfigDict(frozen=True)

    name: Name
    phone: Phone
    email: str | None = Field(default=None, max_length=255)
    comment: str | None = Field(default=None, max_length=2000)
    desired_date: date | None = None
    servings: int | None = Field(default=None, gt=0, le=1000)
    # numeric(10, 2) в БД: больше цифр - ошибка БД, поэтому ограничиваем здесь
    budget: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    decor: str | None = Field(default=None, max_length=200)
    design_description: str | None = Field(default=None, max_length=5000)

    @field_validator("email", "comment", "decor", "design_description", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        """Пробелы по краям убираем, пустая строка означает "не заполнено"."""
        if isinstance(value, str):
            value = value.strip() or None
        return value

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str | None) -> str | None:
        if value is not None and not is_valid_email(value):
            raise ValueError("Некорректный email")
        return value


class LeadCreated(BaseModel):
    id: int


class ShopOut(BaseModel):
    model_config = ConfigDict(frozen=True)
    currency: str
