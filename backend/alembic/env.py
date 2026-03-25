from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
import sys

sys.path.append(".")
from app.models.database import Base
from app.core.config import settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _to_sync_database_url(database_url: str) -> str:
    """Alembic uses a synchronous SQLAlchemy engine for migrations."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://", 1
        )
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return database_url


def run_migrations_online():
    # Use DATABASE_URL from environment or default from config
    database_url = _to_sync_database_url(settings.DATABASE_URL)
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool if "sqlite" in database_url else pool.QueuePool,
    )

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
