from typing import Annotated, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from sqlalchemy import select
from app.core.deps import CurrentUserDep, SessionDep
from app.models.database import Platform, SkillEmbedding
from app.schemas.requests import PlatformCreate, PlatformUpdate
from app.services.crawler import CrawlerService
from app.services.vectorizer import Vectorizer
from app.ingestion.skills_parser import SkillParser
from app.core.config import settings
import logging
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/platforms", tags=["platforms"])


async def background_crawl_task(
    platform_id: str, url: str, skills_url: Optional[str] = None
):
    """
    Crawls the platform, generating a fallback description and scanning for skills.
    If a skill is found or provided directly, it automatically gets indexed.
    """
    crawler = CrawlerService()
    try:
        # We need a new session context for background tasks
        from app.db.session import SessionLocal
        import uuid

        async with SessionLocal() as session:
            platform_uuid = uuid.UUID(platform_id)
            result = await session.execute(
                select(Platform).filter(Platform.id == platform_uuid)
            )
            platform = result.scalars().first()
            if not platform:
                return

            if skills_url:
                # Fetch directly if we have a specific URL
                import httpx

                async with httpx.AsyncClient() as client:
                    resp = await client.get(skills_url, follow_redirects=True)
                    skill_content = resp.text if resp.status_code == 200 else None
                crawl_result = {
                    "skill_content": skill_content,
                    "description": platform.description,
                }
            else:
                crawl_result = await crawler.crawl_platform(url)

            # Auto-update description if not explicitly provided
            if not platform.description and crawl_result.get("description"):
                platform.description = crawl_result["description"]

            if crawl_result.get("skill_content"):
                # Initialize the Vectorizer and auto-ingest the discovered skill
                logger.info(f"Indexing skill for platform {url}")
                vectorizer = Vectorizer()
                parsed = SkillParser.parse_skill_content(crawl_result["skill_content"])
                capabilities = parsed["normalized_text"]
                skill_hash = hashlib.sha256(capabilities.encode("utf-8")).hexdigest()
                embedding = vectorizer.generate_embeddings([capabilities])[0]

                existing_result = await session.execute(
                    select(SkillEmbedding).filter(
                        SkillEmbedding.platform_id == platform.id
                    )
                )
                existing_skill = existing_result.scalars().first()
                if existing_skill:
                    existing_skill.dimension = embedding
                    existing_skill.capabilities = capabilities
                    existing_skill.skill_name = parsed.get("skill_name")
                    existing_skill.tags = parsed.get("tags")
                    existing_skill.skill_hash = skill_hash
                else:
                    db_skill = SkillEmbedding(
                        platform_id=platform.id,
                        dimension=embedding,
                        capabilities=capabilities,
                        skill_name=parsed.get("skill_name"),
                        tags=parsed.get("tags"),
                        skill_hash=skill_hash,
                    )
                    session.add(db_skill)

            await session.commit()
    except Exception as e:
        logger.error(f"Error during background crawl of {url}: {e}")
    finally:
        await crawler.close()


@router.post("/")
async def create_platform(
    platform_in: PlatformCreate,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    """
    Submit a new platform to the index. Kicks off an asynchronous background
    task to generate descriptions and discover AI skills.
    """
    db_platform = Platform(
        name=platform_in.name,
        url=str(platform_in.url),
        homepage_uri=str(platform_in.homepage_uri),
        skills_url=str(platform_in.skills_url),
        description=platform_in.description,
        owner_id=str(current_user.id),
    )
    session.add(db_platform)
    await session.commit()
    await session.refresh(db_platform)

    # Queue the background crawl task
    background_tasks.add_task(
        background_crawl_task,
        str(db_platform.id),
        str(db_platform.url),
        str(platform_in.skills_url),
    )

    return {
        "id": str(db_platform.id),
        "name": db_platform.name,
        "skills_url": db_platform.skills_url,
        "message": "Platform created successfully. Crawler dispatched to discover skills and analyze the webpage.",
    }


@router.post("/{platform_id}/ingest")
async def ingest_platform_skills(
    platform_id: str,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    skills_url: Annotated[
        Optional[str], Query(description="Optional URL to fetch skill content from")
    ] = None,
) -> dict[str, Any]:
    import uuid

    try:
        platform_uuid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(Platform).filter(Platform.id == platform_uuid)
    )
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    effective_skills_url = skills_url or platform.skills_url

    background_tasks.add_task(
        background_crawl_task, str(platform.id), str(platform.url), effective_skills_url
    )

    return {"message": "Ingestion task queued.", "platform_id": str(platform.id)}


@router.get("")
@router.get("/")
async def list_platforms(session: SessionDep) -> list[dict[str, Any]]:
    result = await session.execute(
        select(Platform).order_by(Platform.created_at.desc())
    )
    platforms = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "url": p.url,
            "homepage_uri": p.homepage_uri,
            "skills_url": p.skills_url,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in platforms
    ]


@router.get("/{platform_id}")
async def get_platform(platform_id: str, session: SessionDep) -> dict[str, Any]:
    import uuid

    try:
        platform_uuid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(Platform).filter(Platform.id == platform_uuid)
    )
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    return {
        "id": str(platform.id),
        "name": platform.name,
        "url": platform.url,
        "homepage_uri": platform.homepage_uri,
        "skills_url": platform.skills_url,
        "description": platform.description,
        "created_at": platform.created_at.isoformat() if platform.created_at else None,
    }


@router.put("/{platform_id}")
async def update_platform(
    platform_id: str,
    payload: PlatformUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    import uuid

    try:
        platform_uuid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform_id format")

    result = await session.execute(
        select(Platform).filter(Platform.id == platform_uuid)
    )
    platform = result.scalars().first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    if platform.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="Only the platform owner can edit this platform"
        )

    if payload.name is not None:
        platform.name = payload.name
    if payload.url is not None:
        platform.url = str(payload.url)
    if payload.homepage_uri is not None:
        platform.homepage_uri = str(payload.homepage_uri)
    if payload.description is not None:
        platform.description = payload.description
    if payload.skills_url is not None:
        platform.skills_url = str(payload.skills_url)

    await session.commit()
    await session.refresh(platform)

    return {
        "id": str(platform.id),
        "name": platform.name,
        "url": platform.url,
        "homepage_uri": platform.homepage_uri,
        "skills_url": platform.skills_url,
        "description": platform.description,
        "owner_id": platform.owner_id,
        "created_at": platform.created_at.isoformat() if platform.created_at else None,
        "message": "Platform updated successfully",
    }
