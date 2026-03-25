import asyncio
import uuid

from fastapi.testclient import TestClient
import pytest

from app.db.session import init_db
from app.main import app
from app.services import auth_tokens


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self.store[key] = value

    async def get(self, key: str):
        return self.store.get(key)

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)


async def _noop_background_crawl_task(
    platform_id: str, url: str, skills_url: str | None = None
) -> None:
    return None


async def _noop_send_verification_email(to_email: str, otp_code: str) -> None:
    return None


def _register_user(
    client: TestClient, email: str, password: str = "password123"
) -> dict:
    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data.get("verification_required") is True
    assert "dev_otp" in register_data

    verify_response = client.post(
        "/api/auth/verify-otp",
        json={"email": email, "otp_code": register_data["dev_otp"]},
    )
    assert verify_response.status_code == 200
    return verify_response.json()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def patch_redis_client(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(auth_tokens, "get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(
        "app.routers.auth.send_verification_otp_email",
        _noop_send_verification_email,
    )
    return fake_redis


def test_auth_register_me_and_logout_revokes_token():
    asyncio.run(init_db())

    with TestClient(app) as client:
        email = f"auth-{uuid.uuid4()}@example.com"
        auth = _register_user(client, email)
        token = auth["access_token"]

        me_before_logout = client.get("/api/auth/me", headers=_auth_headers(token))
        assert me_before_logout.status_code == 200
        assert me_before_logout.json()["email"] == email

        logout = client.post("/api/auth/logout", headers=_auth_headers(token))
        assert logout.status_code == 200

        me_after_logout = client.get("/api/auth/me", headers=_auth_headers(token))
        assert me_after_logout.status_code == 401


def test_login_requires_verified_user():
    asyncio.run(init_db())

    with TestClient(app) as client:
        email = f"pending-{uuid.uuid4()}@example.com"
        register_response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "password123"},
        )
        assert register_response.status_code == 200

        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "password123"},
        )
        assert login_response.status_code == 403


def test_platform_create_requires_auth(monkeypatch):
    asyncio.run(init_db())

    import app.routers.platforms as platforms_router

    monkeypatch.setattr(
        platforms_router,
        "background_crawl_task",
        _noop_background_crawl_task,
    )

    with TestClient(app) as client:
        anonymous = client.post(
            "/api/platforms/",
            json={
                "name": "No Auth Platform",
                "url": "https://no-auth.example.com",
                "homepage_uri": "https://no-auth.example.com",
                "skills_url": "https://no-auth.example.com/skills",
            },
        )
        assert anonymous.status_code == 401

        email = f"owner-{uuid.uuid4()}@example.com"
        auth = _register_user(client, email)

        created = client.post(
            "/api/platforms/",
            headers=_auth_headers(auth["access_token"]),
            json={
                "name": "Auth Platform",
                "url": "https://auth.example.com",
                "homepage_uri": "https://auth.example.com",
                "skills_url": "https://auth.example.com/skills",
            },
        )

        assert created.status_code == 200
        body = created.json()
        assert "id" in body
        assert body["name"] == "Auth Platform"


def test_platform_update_restricted_to_owner(monkeypatch):
    asyncio.run(init_db())

    import app.routers.platforms as platforms_router

    monkeypatch.setattr(
        platforms_router,
        "background_crawl_task",
        _noop_background_crawl_task,
    )

    with TestClient(app) as client:
        owner_auth = _register_user(client, f"owner-{uuid.uuid4()}@example.com")
        other_auth = _register_user(client, f"other-{uuid.uuid4()}@example.com")

        created = client.post(
            "/api/platforms/",
            headers=_auth_headers(owner_auth["access_token"]),
            json={
                "name": "Owner Platform",
                "url": "https://owner.example.com",
                "homepage_uri": "https://owner.example.com",
                "skills_url": "https://owner.example.com/skills",
            },
        )
        assert created.status_code == 200
        platform_id = created.json()["id"]

        non_owner_update = client.put(
            f"/api/platforms/{platform_id}",
            headers=_auth_headers(other_auth["access_token"]),
            json={"description": "I should not be able to edit this"},
        )
        assert non_owner_update.status_code == 403

        owner_update = client.put(
            f"/api/platforms/{platform_id}",
            headers=_auth_headers(owner_auth["access_token"]),
            json={"description": "Owner updated description"},
        )
        assert owner_update.status_code == 200
        assert owner_update.json()["description"] == "Owner updated description"
