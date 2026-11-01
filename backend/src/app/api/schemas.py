"""Схемы ответов API. Отдельно от domain: контракт API не должен меняться вместе с моделью."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict

from app.domain.allergen import Allergen
from app.domain.category import LocalizedCategory
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
