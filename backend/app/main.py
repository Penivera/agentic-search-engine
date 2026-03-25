from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from app.db.session import init_db
from app.routers import api_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.database import Platform, SkillEmbedding


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


# Initialize the application
app = FastAPI(
    title="ASE API",
    description="Agentic Search Engine backend API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Agentic Search Engine API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "database": settings.db_type}


@app.get("/skill.md", include_in_schema=False)
async def skill_markdown() -> PlainTextResponse:
    """
    Public skill document endpoint expected by external agent indexers.
    Returns the latest indexed skill as markdown, with a safe fallback.
    """
    fallback = (
        "# Agentic Search Engine\n\n"
        "## Capabilities\n"
        "- Semantic search over indexed platform skills\n"
        "- Platform and skill registration APIs\n"
        "- JWT auth, ownership, and OTP-based verification\n"
    )

    try:
        async with SessionLocal() as session:
            result = await session.execute(
                select(SkillEmbedding, Platform)
                .join(Platform, SkillEmbedding.platform_id == Platform.id)
                .order_by(SkillEmbedding.created_at.desc())
                .limit(1)
            )
            row = result.first()
    except Exception:
        row = None

    if not row:
        return PlainTextResponse(content=fallback, media_type="text/markdown")

    skill, platform = row
    title = skill.skill_name or platform.name or "Agentic Search Engine"
    tags = skill.tags or []
    tag_line = f"\nTags: {', '.join(tags)}\n" if tags else ""
    markdown = (
        f"# {title}\n\n"
        f"Platform: {platform.name}\n"
        f"Platform URL: {platform.url}\n"
        f"Skill URL: {platform.skills_url or '/skill.md'}\n"
        f"{tag_line}\n"
        "## Capabilities\n"
        f"{skill.capabilities.strip()}\n"
    )
    return PlainTextResponse(content=markdown, media_type="text/markdown")


# Register API routes
app.include_router(api_router)
