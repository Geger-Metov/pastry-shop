"""Фикстуры для тестов с настоящей PostgreSQL.

Нужна ОТДЕЛЬНАЯ база, имя которой заканчивается на `_test`:

    CREATE DATABASE pastry_test;
    TEST_DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/pastry_test uv run pytest

Без TEST_DATABASE_URL интеграционные тесты пропускаются. Таблицы создаются заново в начале
сессии (drop_all + create_all), а каждый тест идёт в транзакции, которая откатывается.
"""

import os
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import insert, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

import app.infrastructure.persistence.model  # noqa: F401  (регистрирует модели)
from app.core.config import Settings
from app.domain.locale import SUPPORTED_LOCALES
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_session
from app.infrastructure.persistence.model.locale import LocaleModel
from app.main import create_app

ORIGIN = "http://localhost:3000"


def _test_database_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL", "")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set: integration tests need a real PostgreSQL")
    database = make_url(url).database or ""
    if not database.endswith("_test"):
        # drop_all стирает ВСЕ таблицы: защищаемся от запуска на рабочей базе
        pytest.exit(f"Refusing to run: database {database!r} must end with '_test'", returncode=2)
    return url


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(_test_database_url())
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        # справочник locale в проде заполняет миграция, здесь - вручную
        await connection.execute(
            insert(LocaleModel), [{"code": code} for code in SUPPORTED_LOCALES]
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Сессия внутри внешней транзакции: всё, что сделал тест, откатывается."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        ) as session:
            yield session
        await transaction.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    """HTTP-клиент к приложению; сессия БД - та же, что видит тест."""
    settings = Settings(
        database_url="postgresql+asyncpg://unused/unused_test",
        shop_currency="RUB",
        phone_default_country_code="996",
        cors_origins=[ORIGIN],
    )
    app = create_app(settings)

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session  # данные теста доступны приложению, а commit() - это commit savepoint

    app.dependency_overrides[get_session] = override_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
