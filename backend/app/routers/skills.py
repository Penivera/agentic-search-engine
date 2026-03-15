from typing import Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import json
import uuid

from app.core.deps import SessionDep, VectorizerDep
from app.models.database import SkillEmbedding, Platform
from app.schemas.requests import SkillCreate
from app.core.config import settings

router = APIRouter(prefix="/skills", tags=["skills"])

@router.post("/")
async def create_skill(
    skill_in: SkillCreate,
    session: SessionDep,
    vectorizer: VectorizerDep
) -> dict[str, Any]:
    """
    Submit a new skill for a platform, generating vector embeddings automatically.
    """
    # Verify platform exists
    try:
        platform_uuid = uuid.UUID(skill_in.platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(select(Platform).filter(Platform.id == platform_uuid))
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    try:
        embedding = vectorizer.generate_embeddings([skill_in.capabilities])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")

    # The SQLAlchemy JSON type natively handles lists
    db_skill = SkillEmbedding(
        platform_id=platform_uuid,
        dimension=embedding,
        capabilities=skill_in.capabilities
    )
    session.add(db_skill)
    await session.commit()
    await session.refresh(db_skill)

    return {
        "id": str(db_skill.id),
        "platform_id": str(db_skill.platform_id),
        "capabilities": db_skill.capabilities,
        "message": "Skill ingested successfully"
    }


@router.get("/{platform_id}")
async def get_skill(
    platform_id: str,
    session: SessionDep
) -> dict[str, Any]:
    """
    Retrieve the full skill capabilities for a specific platform.
    Used by agents to 'go deeper' after a discovery search.
    """
    try:
        platform_uuid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(SkillEmbedding).filter(SkillEmbedding.platform_id == platform_uuid)
    )
    skill = result.scalars().first()
    
    if not skill:
        return {
            "status": "not_found",
            "message": "We do not have a skill file for this platform yet. You can request it to be indexed via the /platforms endpoint."
        }

    return {
        "platform_id": str(skill.platform_id),
        "capabilities": skill.capabilities,
        "created_at": skill.created_at.isoformat()
    }
