from __future__ import annotations

import hashlib
import uuid
from typing import Any, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.config import settings
from app.core.deps import (
    BearerCredentialsDep,
    OptionalUserDep,
    SessionDep,
    VectorizerDep,
)
from app.models.database import Platform, SkillEmbedding
from app.schemas.requests import SkillCreate

router = APIRouter(prefix="/skills", tags=["skills"])


def _skill_payload(skill: SkillEmbedding) -> dict[str, Any]:
    return {
        "id": str(skill.id),
        "platform_id": str(skill.platform_id),
        "skill_name": skill.skill_name,
        "tags": skill.tags or [],
        "capabilities": skill.capabilities,
        "created_at": skill.created_at.isoformat() if skill.created_at else None,
    }


@router.post("")
@router.post("/")
async def create_skill(
    skill_in: SkillCreate,
    session: SessionDep,
    vectorizer: VectorizerDep,
    credentials: BearerCredentialsDep,
    current_user: OptionalUserDep,
) -> dict[str, Any]:
    """
    Register or update a skill. Requires bearer token when INGEST_API_TOKENS is configured.
    """
    try:
        platform_uuid = uuid.UUID(skill_in.platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(Platform).filter(Platform.id == platform_uuid)
    )
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    # Authorized if bearer token is in INGEST_API_TOKENS OR user owns the platform.
    if settings.ingest_tokens:
        bearer_token = credentials.credentials if credentials else None
        is_ingest_token = bool(bearer_token and bearer_token in settings.ingest_tokens)
        is_owner = bool(current_user and str(current_user.id) == platform.owner_id)

        if not is_ingest_token and not is_owner:
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid bearer token",
            )

    embedding_text = "\n".join(
        x
        for x in [
            skill_in.skill_name or "",
            " ".join(skill_in.tags or []),
            skill_in.capabilities,
        ]
        if x
    )

    try:
        embedding = vectorizer.generate_embeddings([embedding_text])[0]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate embedding: {e}"
        )

    skill_hash = hashlib.sha256(skill_in.capabilities.encode("utf-8")).hexdigest()

    existing = await session.execute(
        select(SkillEmbedding).filter(
            SkillEmbedding.platform_id == platform_uuid,
            SkillEmbedding.skill_hash == skill_hash,
        )
    )
    existing_skill = existing.scalars().first()
    if existing_skill:
        return {
            **_skill_payload(existing_skill),
            "message": "Duplicate skill ignored",
        }

    db_skill = SkillEmbedding(
        platform_id=platform_uuid,
        dimension=embedding,
        capabilities=skill_in.capabilities,
        skill_name=skill_in.skill_name,
        tags=skill_in.tags,
        skill_hash=skill_hash,
    )
    session.add(db_skill)
    await session.commit()
    await session.refresh(db_skill)

    return {
        **_skill_payload(db_skill),
        "message": "Skill ingested successfully",
    }


@router.get("")
@router.get("/")
async def list_skills(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    result = await session.execute(
        select(SkillEmbedding)
        .order_by(SkillEmbedding.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    skills = result.scalars().all()
    return {
        "count": len(skills),
        "items": [_skill_payload(skill) for skill in skills],
    }


@router.get("/by-platform/{platform_id}")
async def get_skill_by_platform(
    platform_id: str,
    session: SessionDep,
) -> dict[str, Any]:
    """
    Compatibility endpoint for existing callers that resolve a skill by platform id.
    """
    try:
        platform_uuid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(SkillEmbedding)
        .filter(SkillEmbedding.platform_id == platform_uuid)
        .order_by(SkillEmbedding.created_at.desc())
    )
    skill = result.scalars().first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found for platform")

    return _skill_payload(skill)


@router.get("/{skill_id}")
async def get_skill(skill_id: str, session: SessionDep) -> dict[str, Any]:
    """
    Get a skill by skill id.
    """
    try:
        skill_uuid = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill_id format")

    result = await session.execute(
        select(SkillEmbedding).filter(SkillEmbedding.id == skill_uuid)
    )
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return _skill_payload(skill)
