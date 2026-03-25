from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.db.session import get_db_startup_error, init_db, record_db_startup_error
from app.routers import api_router
from app.core.config import settings


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.db_ready = False
    try:
        await init_db()
        app.state.db_ready = True
    except Exception as exc:
        record_db_startup_error(exc)
        logger.exception(
            "Database init failed during startup. Continuing in degraded mode."
        )
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
async def health() -> dict[str, str | bool | None]:
    db_error = get_db_startup_error()
    status = "ok" if app.state.db_ready else "degraded"
    return {
        "status": status,
        "database": settings.db_type,
        "database_ready": app.state.db_ready,
        "database_error": db_error,
    }


@app.get("/skill.md", include_in_schema=False)
async def skill_markdown() -> PlainTextResponse:
    """
    Public skill document endpoint expected by external agent indexers.
    Returns ASE's canonical skill file when available, with a safe fallback.
    """
    # Prefer serving the repository skill contract so crawler consumers get
    # stable product capabilities instead of transient indexed third-party skills.
    source_file_candidates = [
        Path(__file__).resolve().parents[1]
        / ".agents"
        / "skills"
        / "agentic-search-engine"
        / "SKILL.md",
        Path(__file__).resolve().parents[2]
        / ".agents"
        / "skills"
        / "agentic-search-engine"
        / "SKILL.md",
    ]
    for candidate in source_file_candidates:
        if candidate.exists():
            try:
                return PlainTextResponse(
                    content=candidate.read_text(encoding="utf-8"),
                    media_type="text/markdown",
                )
            except Exception:
                pass

    fallback = (
        "# ASE (Agentic Search Engine) Skill\n\n"
        "## Capabilities\n"
        "- Discover platforms by semantic capability search\n"
        "- Register platforms and ingest external skill documents\n"
        "- Retrieve latest indexed skill content per platform\n"
    )
    return PlainTextResponse(content=fallback, media_type="text/markdown")


# Register API routes
app.include_router(api_router)
