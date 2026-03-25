import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, func, JSON, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2083), nullable=False)
    homepage_uri: Mapped[str] = mapped_column(String(2083), nullable=False)
    skills_url: Mapped[str | None] = mapped_column(String(2083), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class SkillEmbedding(Base):
    __tablename__ = "skills_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    platform_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False
    )

    # Store dimension as JSON string for general compatibility,
    # instead of conditionally trying to return an ARRAY column at runtime.
    dimension: Mapped[str] = mapped_column(JSON, nullable=False)

    skill_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    skill_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    capabilities: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
