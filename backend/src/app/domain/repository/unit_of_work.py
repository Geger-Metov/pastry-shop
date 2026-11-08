from typing import Protocol


class UnitOfWork(Protocol):
    """Граница транзакции. Репозитории не коммитят: когда действие завершено, это решает
    сценарий (use case) и вызывает commit() ровно один раз.

    Явного rollback нет: если до commit() случилась ошибка, сессия закрывается без коммита,
    и всё несохранённое откатывается само.
    """

    async def commit(self) -> None: ...
