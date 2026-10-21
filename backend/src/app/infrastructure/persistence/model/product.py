from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import (
    Base,
    BigInt,
    BigIntPk,
    CreatedAt,
    IsActive,
    SortOrder,
    UpdatedAt,
)


class ProductModel(Base):
    __tablename__ = "product"

    id: Mapped[BigIntPk]
    category_id: Mapped[BigInt] = mapped_column(
        ForeignKey("category.id", ondelete="RESTRICT"), index=True
    )
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    sort_order: Mapped[SortOrder]
    is_active: Mapped[IsActive]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


class ProductTranslationModel(Base):
    __tablename__ = "product_translation"

    product_id: Mapped[BigInt] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(5), ForeignKey("locale.code"), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)


class ProductVariantModel(Base):
    __tablename__ = "product_variant"

    __table_args__ = (
        CheckConstraint("weight_g > 0", name="weight_positive"),
        UniqueConstraint("product_id", "weight_g", "pieces", postgresql_nulls_not_distinct=True),
        CheckConstraint("price > 0", name="price_non_negative"),
        CheckConstraint("pieces > 0", name="pieces_non_negative"),
    )

    id: Mapped[BigIntPk]
    product_id: Mapped[BigInt] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), index=True
    )
    weight_g: Mapped[int | None] = mapped_column(Integer)
    pieces: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[SortOrder]
    is_active: Mapped[IsActive]


class ProductImageModel(Base):
    __tablename__ = "product_image"

    id: Mapped[BigIntPk]
    product_id: Mapped[BigInt] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), index=True
    )
    path: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[SortOrder]


class ProductAllergenModel(Base):
    __tablename__ = "product_allergen"

    product_id: Mapped[BigInt] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), primary_key=True
    )
    allergen_id: Mapped[BigInt] = mapped_column(
        ForeignKey("allergen.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
