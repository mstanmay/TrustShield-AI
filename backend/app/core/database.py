"""
Async SQLAlchemy engine and session factory for PostgreSQL (and SQLite fallback).
Production-safe connection management with automatic driver normalization and credential masking.
"""

from __future__ import annotations

import logging
import re
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

logger = logging.getLogger(__name__)


def normalize_async_database_url(raw_url: str | None) -> str:
    """Safely convert any database URL into an async-compatible URL for SQLAlchemy AsyncEngine.

    Handles:
    - postgres:// -> postgresql+asyncpg://
    - postgresql:// -> postgresql+asyncpg://
    - postgresql+psycopg2:// -> postgresql+asyncpg://
    - postgresql+psycopg:// -> postgresql+asyncpg://
    - sqlite:// -> sqlite+aiosqlite://
    - sqlite+aiosqlite:// -> preserved
    - postgresql+asyncpg:// -> preserved
    """
    if not raw_url or not str(raw_url).strip():
        raise ValueError(
            "DATABASE_URL is not set or is empty. "
            "Please configure the DATABASE_URL environment variable."
        )

    url = str(raw_url).strip()

    # Normalize PostgreSQL schemes for asyncpg
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    # Normalize SQLite schemes for aiosqlite
    if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


def normalize_sync_database_url(raw_url: str | None) -> str:
    """Safely convert any database URL into a sync-compatible URL for Celery/migrations."""
    if not raw_url or not str(raw_url).strip():
        raw_url = getattr(settings, "DATABASE_URL", "sqlite+aiosqlite:///./sebi_fraud.db")

    url = str(raw_url).strip()

    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)

    return url


def mask_database_url(url: str) -> str:
    """Mask credentials (passwords) in database URL for safe logging."""
    if not url:
        return "<empty>"
    try:
        u = make_url(url)
        return u.render_as_string(hide_password=True)
    except Exception:
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", str(url))


def create_async_engine_instance(url: str) -> AsyncEngine:
    """Build a configured AsyncEngine based on URL dialect."""
    async_url = normalize_async_database_url(url)
    engine_kwargs: dict = {
        "echo": settings.DEBUG,
        "pool_pre_ping": True,
    }

    if async_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        pool_size = getattr(settings, "DB_POOL_SIZE", 20)
        max_overflow = getattr(settings, "DB_MAX_OVERFLOW", 10)
        engine_kwargs.update({
            "pool_size": pool_size,
            "max_overflow": max_overflow,
        })

    return create_async_engine(async_url, **engine_kwargs)


# ── Primary Async Engine & Session Maker ─────────────────────────────────────
ASYNC_DATABASE_URL = normalize_async_database_url(settings.DATABASE_URL)
async_engine: AsyncEngine = create_async_engine_instance(ASYNC_DATABASE_URL)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ── Primary Sync Engine (for Celery / Migrations) ─────────────────────────────
SYNC_DATABASE_URL = normalize_sync_database_url(settings.DATABASE_SYNC_URL or settings.DATABASE_URL)
_sync_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}
if not SYNC_DATABASE_URL.startswith("sqlite"):
    _sync_engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 5,
    })
sync_engine = create_engine(SYNC_DATABASE_URL, **_sync_engine_kwargs)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
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
    """Create all tables with automatic fallback if primary DB is unreachable."""
    global async_engine, AsyncSessionLocal
    from app.models.database import Base

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Connected to database at %s", mask_database_url(ASYNC_DATABASE_URL))
    except Exception as e:
        logger.warning(
            "Primary database connection failed (%s). Falling back to local SQLite database (sebi_fraud.db)...",
            e,
        )
        sqlite_url = "sqlite+aiosqlite:///./sebi_fraud.db"
        async_engine = create_async_engine(
            sqlite_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Initialized local SQLite fallback database successfully at %s", mask_database_url(sqlite_url))


async def close_db() -> None:
    """Dispose of the engine connection pool."""
    global async_engine
    if async_engine:
        await async_engine.dispose()

