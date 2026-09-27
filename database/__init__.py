"""NWIS persistent storage package.

Database engine objects are imported lazily so schema-only consumers and tests do not
need a live PostgreSQL driver at import time.
"""

__all__ = ["Base", "SessionLocal", "engine", "get_session"]


def __getattr__(name):
    if name in __all__:
        from . import db
        return getattr(db, name)
    raise AttributeError(name)
