"""SQLAlchemy engine and session helpers."""
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import get_settings


class Base(DeclarativeBase):
    """Base class for all NWIS ORM models."""


engine = create_engine(get_settings().database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session and close it when finished."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_all() -> None:
    """Create ORM tables directly; production deployments should prefer Alembic."""
    from .models import import_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
