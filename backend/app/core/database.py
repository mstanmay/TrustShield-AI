"""
Async SQLAlchemy engine and session factory for PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine

from app.config import settings

import logging

logger = logging.getLogger(__name__)

# Primary Async engine (PostgreSQL or configured DB)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for Celery / migrations
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)


async def get_db_session() -> AsyncSession:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (auto-fallbacks to SQLite if PostgreSQL is unavailable)."""
    global async_engine, AsyncSessionLocal
    from app.models.database import Base

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Connected to database at %s", settings.DATABASE_URL)
    except Exception as e:
        logger.warning(
            "PostgreSQL connection failed (%s). Falling back to local SQLite database (sebi_fraud.db)...",
            e,
        )
        sqlite_url = "sqlite+aiosqlite:///./sebi_fraud.db"
        async_engine = create_async_engine(sqlite_url, echo=settings.DEBUG)
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Initialized local SQLite database successfully")


async def close_db() -> None:
    """Dispose of the engine connection pool."""
    await async_engine.dispose()

