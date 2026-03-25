import asyncio

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.deps import get_vectorizer
from app.db.session import SessionLocal, init_db
from app.main import app
from app.models.database import Platform


class FakeVectorizer:
    def generate_embeddings(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


async def _create_platform() -> str:
    async with SessionLocal() as session:
        platform = Platform(
            name="ASE Test Platform",
            url="https://example.org",
            homepage_uri="https://example.org",
            description="platform for tests",
        )
        session.add(platform)
        await session.commit()
        await session.refresh(platform)
        return str(platform.id)


def test_skills_api_contract_end_to_end():
    asyncio.run(init_db())
    settings.INGEST_API_TOKENS = "test-token"

    app.dependency_overrides[get_vectorizer] = lambda: FakeVectorizer()

    with TestClient(app) as client:
        platform_id = asyncio.run(_create_platform())

        missing_auth = client.post(
            "/api/skills",
            json={
                "platform_id": platform_id,
                "skill_name": "email sender",
                "tags": ["email", "notification"],
                "capabilities": "Can send transactional email.",
            },
        )
        assert missing_auth.status_code == 401

        created = client.post(
            "/api/skills",
            headers={"Authorization": "Bearer test-token"},
            json={
                "platform_id": platform_id,
                "skill_name": "email sender",
                "tags": ["email", "notification"],
                "capabilities": "Can send transactional email.",
            },
        )
        assert created.status_code == 200
        skill_id = created.json()["id"]

        listed = client.get("/api/skills")
        assert listed.status_code == 200
        assert listed.json()["count"] >= 1

        fetched = client.get(f"/api/skills/{skill_id}")
        assert fetched.status_code == 200
        assert fetched.json()["id"] == skill_id

    app.dependency_overrides = {}


def test_public_skill_md_endpoint_returns_markdown():
    asyncio.run(init_db())

    with TestClient(app) as client:
        response = client.get("/skill.md")

    assert response.status_code == 200
    assert "text/markdown" in response.headers.get("content-type", "")
    assert response.text.strip().startswith("#")
