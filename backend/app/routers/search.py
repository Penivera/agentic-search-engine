from typing import Annotated, Any, Literal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
import json
import numpy as np
import time
import logging
import re

from app.core.deps import SessionDep, VectorizerDep
from app.models.database import QueryLog, SkillEmbedding
from app.services.search_cache import search_cache

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)

_TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9]+")
_TOKEN_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "near",
    "find",
    "platform",
    "agent",
    "agents",
    "agentic",
}


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in _TOKEN_SPLIT_RE.split(text.lower())
        if len(token) >= 3 and token not in _TOKEN_STOPWORDS
    }


def _tailoring_sequence(mode: str, auto_relax: bool, relax_steps: int) -> list[str]:
    sequence_order = {
        "strict": ["strict", "balanced", "broad"],
        "balanced": ["balanced", "broad"],
        "broad": ["broad"],
    }
    sequence = sequence_order[mode]
    if not auto_relax:
        return sequence[:1]
    return sequence[: min(len(sequence), relax_steps + 1)]


def _tailoring_profile(mode: str, min_similarity: float) -> tuple[float, float, bool]:
    # Returns (effective_min_similarity, high_confidence_similarity, require_lexical_grounding).
    if mode == "strict":
        effective_min = max(min_similarity, 0.82)
        return effective_min, max(effective_min, 0.90), True
    if mode == "broad":
        effective_min = max(min_similarity, 0.62)
        return effective_min, max(effective_min, 0.85), False

    effective_min = max(min_similarity, 0.74)
    return effective_min, max(effective_min, 0.82), True


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
    tailoring: Annotated[
        Literal["strict", "balanced", "broad"],
        Query(
            description=(
                "How tailored the result set should be: strict (most precise), "
                "balanced (default), broad (more exploratory)"
            )
        ),
    ] = "balanced",
    auto_relax: Annotated[
        bool,
        Query(
            description=(
                "If true, automatically relaxes tailoring toward broader matching "
                "when no results are found"
            )
        ),
    ] = False,
    relax_steps: Annotated[
        int,
        Query(
            ge=0,
            le=2,
            description="How many fallback levels to try when auto_relax=true",
        ),
    ] = 1,
) -> list[dict[str, Any]]:
    """
    Search for skills based on a query, using embeddings for semantic similarity.
    """
    started_at = time.perf_counter()
    if not query.strip():
        return []

    cache_key = (
        f"{query.strip().lower()}::{top_k}::{min_similarity:.3f}::"
        f"{tailoring}::{int(auto_relax)}::{relax_steps}"
    )
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
    query_tokens = _tokenize(query)
    repaired_embeddings = 0
    base_items: list[dict[str, Any]] = []
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

        match_text = "\n".join(
            x
            for x in [
                text_for_match,
                platform.name or "",
                platform.description or "",
            ]
            if x
        )
        keyword_overlap_count = len(query_tokens.intersection(_tokenize(match_text)))
        base_items.append(
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
                "keyword_overlap_count": keyword_overlap_count,
            }
        )

    for current_mode in _tailoring_sequence(tailoring, auto_relax, relax_steps):
        effective_min, high_confidence_similarity, require_lexical = _tailoring_profile(
            current_mode, min_similarity
        )
        candidate_matches = []
        for item in base_items:
            if item["similarity"] < effective_min:
                continue

            if (
                require_lexical
                and query_tokens
                and item["keyword_overlap_count"] == 0
                and item["similarity"] < high_confidence_similarity
            ):
                continue

            response_item = dict(item)
            response_item.pop("keyword_overlap_count", None)
            response_item["applied_tailoring"] = current_mode
            candidate_matches.append(response_item)

        if candidate_matches:
            matches = sorted(
                candidate_matches,
                key=lambda x: x["similarity"],
                reverse=True,
            )[:top_k]
            break
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
