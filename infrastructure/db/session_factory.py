"""
infrastructure/db/session_factory.py
------------------------------------
Creates a SQLAlchemy Engine + sessionmaker that other modules (UoW,
migrations, tests) can import as a single callable `session_factory()`.

Usage
-----
from infrastructure.db.session_factory import session_factory
with session_factory() as session:
    ...

Environment variables (defaults shown):

    PG_HOST=localhost
    PG_PORT=5432
    PG_DB=messenger
    PG_USER=messenger
    PG_PASSWORD=messenger
    PG_POOL_SIZE=10
    PG_MAX_OVERFLOW=20
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


# -------------------------------------------------------------------------
#  helpers
# -------------------------------------------------------------------------
def _build_dsn() -> str:
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5432")
    db   = os.getenv("PG_DB",   "messenger")
    user = os.getenv("PG_USER", "messenger")
    pwd  = os.getenv("PG_PASSWORD", "messenger")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


@lru_cache(maxsize=1)
def _build_engine() -> Engine:
    """Singleton Engine; lru_cache(1) makes it module‑level global."""
    pool_size = int(os.getenv("PG_POOL_SIZE", "10"))
    overflow  = int(os.getenv("PG_MAX_OVERFLOW", "20"))
    engine = create_engine(
        _build_dsn(),
        pool_size=pool_size,
        max_overflow=overflow,
        pool_pre_ping=True,
        future=True,               # SQLAlchemy 2.x style
    )
    return engine


# -------------------------------------------------------------------------
#  public factory
# -------------------------------------------------------------------------
def session_factory() -> Session:
    """
    Returns a *new* Session bound to the singleton Engine.
    Call in a `with` statement or remember to session.close().
    """
    engine = _build_engine()
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
