from collections.abc import Callable
from typing import Self

from sqlalchemy.orm import Session

from app.infrastructure.persistence.repositories import SqlProcessingRecordRepository


class UnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self._session: Session | None = None
        self.records: SqlProcessingRecordRepository | None = None

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.records = SqlProcessingRecordRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session is None:
            return
        if exc_type:
            self._session.rollback()
        else:
            self._session.commit()
        self._session.close()

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork session has not been started")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork session has not been started")
        self._session.rollback()
