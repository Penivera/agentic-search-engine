from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from app import SessionLocal
from app.embeddings.vectorizer import Vectorizer
from api.schemas.database import SkillEmbedding
import json
import numpy as np

router = APIRouter()

@router.get("/search")
async def search_skills(
    query: str = Query(..., description="Search query describing the skill"),
    top_k: int = Query(5, description="Number of top matching skills to return")
):
    """
    Search for skills based on a query, using embeddings for semantic similarity.

    Args:
        query (str): Search query describing skill capabilities.
        top_k (int): Number of top matches to return.

    Returns:
        List[dict]: Matched skills with similarity scores.
    """
    session: Session = SessionLocal()
    vectorizer = Vectorizer()

    # Generate embedding for the search query
    try:
        query_embedding = vectorizer.generate_embeddings([query])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate query embedding: {e}")

    # Retrieve all skills from the database
    skills = session.query(SkillEmbedding).all()
    if not skills:
        raise HTTPException(status_code=404, detail="No skills found in the database.")

    matches = []
    for skill in skills:
        skill_vector = np.array(json.loads(skill.dimension))
        similarity = np.dot(query_embedding, skill_vector) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(skill_vector)
        )
        matches.append({
            "skill": skill.capabilities,
            "similarity": similarity,
        })

    # Sort matches by similarity and return the top_k results
    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:top_k]
    return matches