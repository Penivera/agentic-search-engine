from fastapi import APIRouter, FastAPI, Query
from typing import List
from app.embeddings.vectorizer import Vectorizer
from app.ingestion.skills_parser import SkillParser

router = APIRouter()

# Initialize vectorizer for embeddings
vectorizer = Vectorizer()

@router.get("/search")
async def search_skills(query: str = Query(..., description="Search query for skills")) -> List[dict]:
    """
    Search existing skills by capability.

    Args:
        query (str): The search query representing skill capability.

    Returns:
        List[dict]: Matched skills sorted by relevance.
    """
    # Placeholder: Generate embedding for the query and return sample response
    query_embedding = vectorizer.generate_embeddings([query])

    # Placeholder until database integration is finalized
    return [
        {"skill": "FastAPI Best Practices", "relevance": 0.95},
        {"skill": "Sample Skill", "relevance": 0.86},
    ]
