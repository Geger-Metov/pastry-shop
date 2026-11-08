from sqlalchemy.ext.asyncio import AsyncSession


class SqlUnitOfWork:
    """Реализация UnitOfWork. Получает ТУ ЖЕ сессию, что и репозитории этого запроса."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()
