from typing import Any, Protocol


class UnitOfWork(Protocol):
    def commit(self, session: Any) -> None: ...
