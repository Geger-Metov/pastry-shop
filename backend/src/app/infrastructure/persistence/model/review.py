from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BigInt, BigIntPk, CreatedAt


class ReviewModel(Base):
    """Отзыв на магазин (product_id IS NULL) или на товар. Публикуется после модерации."""

    __tablename__ = "review"

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="rating_range"),
        Index(
            "ix_review_product_id_published",
            "product_id",
            postgresql_where=text("is_published"),
        ),
    )

    id: Mapped[BigIntPk]
    customer_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), index=True
    )
    order_id: Mapped[BigInt | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), index=True
    )
    product_id: Mapped[BigInt | None] = mapped_column(ForeignKey("product.id", ondelete="SET NULL"))
    author_name: Mapped[str] = mapped_column(String(100))
    rating: Mapped[int] = mapped_column(SmallInteger)
    body: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(server_default=text("false"))
    created_at: Mapped[CreatedAt]
