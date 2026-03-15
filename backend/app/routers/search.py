from typing import Annotated, Any
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
import json
import numpy as np

from app.core.deps import SessionDep, VectorizerDep
from app.models.database import SkillEmbedding

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def search_skills(
    session: SessionDep,
    vectorizer: VectorizerDep,
    query: Annotated[str, Query(description="Search query describing the skill")],
    top_k: Annotated[int, Query(description="Number of top matching skills to return")] = 5
) -> list[dict[str, Any]]:
    """
    Search for skills based on a query, using embeddings for semantic similarity.
    """
    try:
        query_embedding = vectorizer.generate_embeddings([query])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate query embedding: {e}")

    from app.models.database import Platform
    
    result = await session.execute(
        select(SkillEmbedding, Platform)
        .join(Platform, SkillEmbedding.platform_id == Platform.id)
    )
    results = result.all()
    
    if not results:
        return []

    matches = []
    for skill, platform in results:
        # SQLite storage uses JSON, Postgres array
        if isinstance(skill.dimension, str):
            skill_vector = np.array(json.loads(skill.dimension))
        else:
            skill_vector = np.array(skill.dimension)
            
        similarity = np.dot(query_embedding, skill_vector) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(skill_vector)
        )
        matches.append({
            "platform_name": platform.name,
            "platform_description": platform.description,
            "platform_id": str(platform.id),
            "skill": skill.capabilities,
            "similarity": float(similarity)
        })

    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:top_k]
    return matches
