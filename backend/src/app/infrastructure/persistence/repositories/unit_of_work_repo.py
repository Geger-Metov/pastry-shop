from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


class SqlUnitOfWork:
    async def commit(self, session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
