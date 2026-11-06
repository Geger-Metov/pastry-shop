from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import SessionDep

# Не входит в OpenAPI: это для Docker/балансировщика, а не часть контракта для фронтенда
router = APIRouter(include_in_schema=False)


@router.get("/health")
async def health(session: SessionDep) -> dict[str, str]:
    """200, если приложение живо и БД отвечает; иначе 503."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok"}
