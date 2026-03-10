from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, func, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(2083), nullable=False)
    homepage_uri = Column(String(2083), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class SkillEmbedding(Base):
    __tablename__ = 'skills_embeddings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey('platforms.id', ondelete='CASCADE'), nullable=False)
    dimension = Column(Text, nullable=False)  # JSON-serialized vector
    capabilities = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)