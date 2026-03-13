import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, func, Float, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from app.db.session import Base 

class Platform(Base):
    __tablename__ = 'platforms'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2083), nullable=False)
    homepage_uri: Mapped[str] = mapped_column(String(2083), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

class SkillEmbedding(Base):
    __tablename__ = 'skills_embeddings'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    platform_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('platforms.id', ondelete='CASCADE'), nullable=False)
    
    # Store dimension as JSON string for general compatibility, 
    # instead of conditionally trying to return an ARRAY column at runtime.
    dimension: Mapped[str] = mapped_column(JSON, nullable=False)
    
    capabilities: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)