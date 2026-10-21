from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BigInt, BigIntPk, IsActive, SortOrder


class CategoryModel(Base):
    __tablename__ = "category"

    __table_args__ = (
        CheckConstraint("parent_id is null or parent_id <> id", name="not_own_parent"),
    )

    id: Mapped[BigIntPk]
    parent_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("category.id", ondelete="RESTRICT"), index=True
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    sort_order: Mapped[SortOrder]
    is_active: Mapped[IsActive]


class CategoryTranslationModel(Base):
    __tablename__ = "category_translation"

    category_id: Mapped[BigInt] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(5), ForeignKey("locale.code"), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
