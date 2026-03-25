from typing import Annotated, Any
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
import json
import numpy as np
import time
import logging

from app.core.deps import SessionDep, VectorizerDep
from app.models.database import QueryLog, SkillEmbedding
from app.services.search_cache import search_cache

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.get("/")
async def search_skills(
    session: SessionDep,
    vectorizer: VectorizerDep,
    query: Annotated[str, Query(description="Search query describing the skill")],
    top_k: Annotated[
        int, Query(ge=1, le=50, description="Number of top matching skills to return")
    ] = 5,
    min_similarity: Annotated[
        float,
        Query(
            ge=0.0,
            le=1.0,
            description="Minimum cosine similarity required for a result to be returned",
        ),
    ] = 0.74,
) -> list[dict[str, Any]]:
    """
    Search for skills based on a query, using embeddings for semantic similarity.
    """
    started_at = time.perf_counter()
    cache_key = f"{query.strip().lower()}::{top_k}::{min_similarity:.3f}"
    cached = search_cache.get(cache_key)
    if cached is not None:
        latency_ms = (time.perf_counter() - started_at) * 1000
        session.add(
            QueryLog(
                query=query,
                top_k=top_k,
                result_count=len(cached),
                latency_ms=latency_ms,
            )
        )
        await session.commit()
        return cached

    try:
        query_embedding = vectorizer.generate_embeddings([query])[0]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate query embedding: {e}"
        )

    from app.models.database import Platform

    result = await session.execute(
        select(SkillEmbedding, Platform).join(
            Platform, SkillEmbedding.platform_id == Platform.id
        )
    )
    results = result.all()

    if not results:
        return []

    matches = []
    query_dim = len(query_embedding)
    repaired_embeddings = 0
    for skill, platform in results:
        text_for_match = "\n".join(
            x
            for x in [
                skill.skill_name or "",
                " ".join(skill.tags or []),
                skill.capabilities,
            ]
            if x
        )
        # SQLite storage uses JSON, Postgres array.
        try:
            if isinstance(skill.dimension, str):
                raw_dimension = json.loads(skill.dimension)
            else:
                raw_dimension = skill.dimension
            skill_vector = np.array(raw_dimension, dtype=float)
        except Exception:
            logger.warning(
                "Skipping skill %s due to invalid embedding payload", skill.id
            )
            continue

        # Repair legacy/invalid vectors on-the-fly so search does not fail.
        if skill_vector.ndim != 1 or len(skill_vector) != query_dim:
            if text_for_match.strip():
                try:
                    repaired_vector = vectorizer.generate_embeddings([text_for_match])[
                        0
                    ]
                    skill.dimension = repaired_vector
                    skill_vector = np.array(repaired_vector, dtype=float)
                    repaired_embeddings += 1
                except Exception:
                    logger.warning(
                        "Skipping skill %s due to unrecoverable embedding dimension mismatch",
                        skill.id,
                    )
                    continue
            else:
                continue

        query_norm = np.linalg.norm(query_embedding)
        skill_norm = np.linalg.norm(skill_vector)
        if query_norm == 0 or skill_norm == 0:
            similarity = 0.0
        else:
            similarity = float(
                np.dot(query_embedding, skill_vector) / (query_norm * skill_norm)
            )

        matches.append(
            {
                "platform_name": platform.name,
                "platform_description": platform.description,
                "platform_id": str(platform.id),
                "skill_id": str(skill.id),
                "skill_name": skill.skill_name,
                "tags": skill.tags or [],
                "skill": skill.capabilities,
                "similarity": similarity,
                "skill_md_url": platform.skills_url,
                "match_text_preview": text_for_match[:220],
            }
        )

    matches = [m for m in matches if m["similarity"] >= min_similarity]
    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:top_k]
    search_cache.set(cache_key, matches)

    if repaired_embeddings:
        await session.commit()

    latency_ms = (time.perf_counter() - started_at) * 1000
    session.add(
        QueryLog(
            query=query,
            top_k=top_k,
            result_count=len(matches),
            latency_ms=latency_ms,
        )
    )
    await session.commit()

    return matches
