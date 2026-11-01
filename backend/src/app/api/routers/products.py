from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import LocaleDep, ProductRepositoryDep
from app.api.schemas import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    repository: ProductRepositoryDep,
    locale: LocaleDep,
    category: Annotated[str | None, Query(description="slug категории")] = None,
) -> list[ProductOut]:
    if category is None:
        items = await repository.list_active(locale)
    else:
        items = await repository.list_active_by_category(category, locale)
    return [ProductOut.from_domain(item) for item in items]


@router.get("/{slug}")
async def get_product(slug: str, repository: ProductRepositoryDep, locale: LocaleDep) -> ProductOut:
    item = await repository.get_active_by_slug(slug, locale)
    if item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.from_domain(item)
