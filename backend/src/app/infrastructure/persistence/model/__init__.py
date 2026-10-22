"""Импорт всех моделей нужен, чтобы они попали в Base.metadata (Alembic autogenerate)."""

from app.infrastructure.persistence.model.allergen import AllergenModel
from app.infrastructure.persistence.model.category import CategoryModel, CategoryTranslationModel
from app.infrastructure.persistence.model.customer import CustomerModel
from app.infrastructure.persistence.model.delivery import DeliveryModel
from app.infrastructure.persistence.model.lead import LeadAttachmentModel, LeadModel
from app.infrastructure.persistence.model.locale import LocaleModel
from app.infrastructure.persistence.model.order import (
    OrderItemModel,
    OrderModel,
    OrderStatusHistoryModel,
)
from app.infrastructure.persistence.model.payment import PaymentModel
from app.infrastructure.persistence.model.portfolio import (
    PortfolioItemModel,
    PortfolioItemTranslationModel,
)
from app.infrastructure.persistence.model.product import (
    ProductAllergenModel,
    ProductImageModel,
    ProductModel,
    ProductTranslationModel,
    ProductVariantModel,
)
from app.infrastructure.persistence.model.review import ReviewModel
from app.infrastructure.persistence.model.staff import StaffUserModel

__all__ = [
    "AllergenModel",
    "CategoryModel",
    "CategoryTranslationModel",
    "CustomerModel",
    "DeliveryModel",
    "LeadAttachmentModel",
    "LeadModel",
    "LocaleModel",
    "OrderItemModel",
    "OrderModel",
    "OrderStatusHistoryModel",
    "PaymentModel",
    "PortfolioItemModel",
    "PortfolioItemTranslationModel",
    "ProductAllergenModel",
    "ProductImageModel",
    "ProductModel",
    "ProductTranslationModel",
    "ProductVariantModel",
    "ReviewModel",
    "StaffUserModel",
]
