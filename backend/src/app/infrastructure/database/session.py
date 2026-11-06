from collections.abc import AsyncIterator
from functools import lru_cache

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def create_engine(database_url: str) -> AsyncEngine:
    """Engine для заданного URL. Соединение открывается лениво, при первом запросе."""
    return create_async_engine(database_url, pool_pre_ping=True)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


# Для скриптов (seed) и всего, что работает вне FastAPI. Приложение этим не пользуется:
# его engine создаётся в lifespan из переданных в create_app настроек.
@lru_cache
def get_engine() -> AsyncEngine:
    # Создаётся лениво, чтобы импорт модуля не требовал DATABASE_URL (тесты, Alembic)
    return create_engine(get_settings().database_url)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return create_sessionmaker(get_engine())


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI-зависимость: одна сессия на один запрос."""
    sessionmaker: async_sessionmaker[AsyncSession] = request.app.state.sessionmaker
    async with sessionmaker() as session:
        yield session
