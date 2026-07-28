"""
Sentinel AI — Async SQLAlchemy engine, session factory, and declarative base.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.services.shared.config import settings

# ── Engine ──────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# ── Session factory ─────────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative base ───────────────────────────────────────────
class Base(DeclarativeBase):
    """Shared declarative base for all ORM models across services."""
    pass


# ── Dependency for FastAPI routes ───────────────────────────────
async def get_db() -> AsyncSession:
    """Yield an async DB session; auto-closes on request teardown."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
