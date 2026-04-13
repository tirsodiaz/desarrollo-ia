from collections.abc import Callable

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.models import Base


def build_engine(database_url: str) -> Engine:
    return create_engine(database_url, echo=False)


def build_session_factory(database_url: str) -> Callable[[], Session]:
    engine = build_engine(database_url)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return factory


def create_all_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)
