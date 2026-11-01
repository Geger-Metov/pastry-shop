from fastapi import APIRouter

from app.api.dependencies import CategoryRepositoryDep, LocaleDep
from app.api.schemas import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
async def list_categories(
    repository: CategoryRepositoryDep, locale: LocaleDep
) -> list[CategoryOut]:
    items = await repository.list_active(locale)
    return [CategoryOut.from_domain(item) for item in items]
