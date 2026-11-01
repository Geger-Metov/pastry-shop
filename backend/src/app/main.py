from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.infrastructure.database.session import get_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    yield
    await get_engine().dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Фабрика приложения. Запуск: `uvicorn app.main:create_app --factory`.

    Настройки можно передать явно (тесты), иначе читаются из окружения.
    """
    settings = settings or get_settings()

    app = FastAPI(title="Pastry shop API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app
