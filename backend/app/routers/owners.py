from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from app.core.deps import SessionDep
from app.models.database import Platform
from app.services.crawler import CrawlerService
import uuid

router = APIRouter(prefix="/owners", tags=["owners"])

class ClaimRequest(BaseModel):
    platform_id: str
    owner_id: str

class VerifyRequest(BaseModel):
    platform_id: str

@router.post("/claim")
async def initiate_claim(
    request: ClaimRequest,
    session: SessionDep
) -> dict[str, Any]:
    """
    Initiates a claim for a platform. Returns a unique token the user must 
    place in their website's <meta name="agentic-site-verification"> tag.
    """
    try:
        platform_uuid = uuid.UUID(request.platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(select(Platform).filter(Platform.id == platform_uuid))
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
        
    if platform.owner_id:
        raise HTTPException(status_code=400, detail="Platform is already claimed")

    # In a real app we would store this challenge token mapped to the user/session
    # For this demo, we make the token a deterministic hash of the owner string + id
    import hashlib
    token = f"{platform_uuid}-{hashlib.md5(request.owner_id.encode()).hexdigest()}"

    return {
        "message": "Please add the following meta tag to your website's <head> to verify ownership.",
        "html_tag": f'<meta name="agentic-site-verification" content="{token}" />',
        "token": token
    }

@router.post("/verify")
async def verify_claim(
    request: VerifyRequest,
    session: SessionDep
) -> dict[str, Any]:
    """
    Instructs the server to crawl the platform's homepage and check for 
    the presence of the verification token.
    """
    try:
        platform_uuid = uuid.UUID(request.platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(select(Platform).filter(Platform.id == platform_uuid))
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    if platform.owner_id:
        raise HTTPException(status_code=400, detail="Platform is already claimed")

    crawler = CrawlerService()
    try:
        meta_data = await crawler.extract_meta_tags(platform.homepage_uri)
    finally:
        await crawler.close()

    token = meta_data.get("verification_token")
    if not token or not token.startswith(str(platform_uuid)):
        raise HTTPException(
            status_code=403, 
            detail="Verification failed. Meta tag 'agentic-site-verification' was not found or invalid."
        )

    # Validate the token string (extract owner hash)
    # E.g. token format: {uuid}-{md5_hash}
    # For a real implementation, we'd lookup the database for `owner_id` by the token challenge
    platform.owner_id = "verified_owner_session"
    await session.commit()

    return {
        "message": "Domain ownership successfully verified.",
        "platform_id": str(platform.id)
    }
