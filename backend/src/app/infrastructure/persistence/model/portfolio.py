from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BigInt, BigIntPk, CreatedAt, IsActive, SortOrder


class PortfolioItemModel(Base):
    __tablename__ = "portfolio_item"

    id: Mapped[BigIntPk]
    category_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), index=True
    )
    image_path: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[SortOrder]
    is_published: Mapped[IsActive]
    created_at: Mapped[CreatedAt]


class PortfolioItemTranslationModel(Base):
    __tablename__ = "portfolio_item_translation"

    portfolio_item_id: Mapped[BigInt] = mapped_column(
        ForeignKey("portfolio_item.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(5), ForeignKey("locale.code"), primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
