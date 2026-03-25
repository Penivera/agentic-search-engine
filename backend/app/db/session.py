from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import MetaData, inspect, text
from app.core.config import settings

_db_startup_error: str | None = None

# Modify the URL for async dialects dynamically if needed,
# assuming SQLite local by default and Postgres on prod
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
elif db_url.startswith("postgres"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )

engine = create_async_engine(db_url)
SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
metadata = MetaData()


class Base(DeclarativeBase):
    pass


async def init_db():
    global _db_startup_error

    from app.models.database import Base

    _db_startup_error = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_users_columns)
        await conn.run_sync(_ensure_platforms_columns)
        await conn.run_sync(_ensure_skills_embeddings_columns)


def record_db_startup_error(exc: Exception) -> None:
    global _db_startup_error
    _db_startup_error = f"{type(exc).__name__}: {exc}"


def get_db_startup_error() -> str | None:
    return _db_startup_error


def _ensure_users_columns(sync_conn) -> None:
    inspector = inspect(sync_conn)
    table_names = inspector.get_table_names()
    if "users" not in table_names:
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "is_verified" not in existing_columns:
        sync_conn.execute(
            text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL")
        )

    if "verified_at" not in existing_columns:
        sync_conn.execute(text("ALTER TABLE users ADD COLUMN verified_at TIMESTAMP"))


def _ensure_platforms_columns(sync_conn) -> None:
    inspector = inspect(sync_conn)
    table_names = inspector.get_table_names()
    if "platforms" not in table_names:
        return

    existing_columns = {col["name"] for col in inspector.get_columns("platforms")}
    if "skills_url" not in existing_columns:
        sync_conn.execute(
            text("ALTER TABLE platforms ADD COLUMN skills_url VARCHAR(2083)")
        )

    if "owner_id" not in existing_columns:
        sync_conn.execute(
            text("ALTER TABLE platforms ADD COLUMN owner_id VARCHAR(255)")
        )


def _ensure_skills_embeddings_columns(sync_conn) -> None:
    inspector = inspect(sync_conn)
    table_names = inspector.get_table_names()
    if "skills_embeddings" not in table_names:
        return

    existing_columns = {
        col["name"] for col in inspector.get_columns("skills_embeddings")
    }

    if "skill_name" not in existing_columns:
        sync_conn.execute(
            text("ALTER TABLE skills_embeddings ADD COLUMN skill_name VARCHAR(255)")
        )

    if "tags" not in existing_columns:
        if settings.db_type == "postgres":
            sync_conn.execute(
                text("ALTER TABLE skills_embeddings ADD COLUMN tags JSONB")
            )
        else:
            sync_conn.execute(
                text("ALTER TABLE skills_embeddings ADD COLUMN tags JSON")
            )

    if "skill_hash" not in existing_columns:
        sync_conn.execute(
            text("ALTER TABLE skills_embeddings ADD COLUMN skill_hash VARCHAR(64)")
        )
