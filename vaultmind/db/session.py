"""Database session management for VaultMind.

Supports PostgreSQL (recommended) and SQLite (fallback for edge devices).

Connection string format:
  PostgreSQL: postgresql://user:password@localhost:5432/vaultmind
  SQLite:     sqlite:///data/vaultmind.db
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from vaultmind.db.models import Base

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = os.environ.get(
    "VAULTMIND_DATABASE_URL",
    "sqlite:///data/vaultmind.db",
)

_engine = None
_SessionLocal = None


def get_engine(database_url: str | None = None):
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        url = database_url or DEFAULT_DATABASE_URL
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        _engine = create_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        logger.info("Database engine created: %s", url.split("@")[-1] if "@" in url else url)
    return _engine


def get_session_factory(database_url: str | None = None) -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine(database_url)
        _SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return _SessionLocal


def init_db(database_url: str | None = None):
    """Create all tables. Safe to call multiple times (uses CREATE IF NOT EXISTS)."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    logger.info("Database tables created/verified")


@contextmanager
def get_db(database_url: str | None = None):
    """Context manager for database sessions with automatic rollback on error."""
    factory = get_session_factory(database_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_connection(database_url: str | None = None) -> bool:
    """Test database connectivity."""
    try:
        engine = get_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database connection check failed")
        return False


def reset_engine():
    """Reset the engine and session factory (for testing)."""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
