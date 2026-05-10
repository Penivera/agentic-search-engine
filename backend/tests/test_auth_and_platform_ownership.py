import asyncio
import uuid
import base58
from nacl.signing import SigningKey

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


@pytest.fixture(autouse=True)
def patch_redis_client(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(auth_tokens, "get_redis_client", lambda: fake_redis)
    return fake_redis


def _generate_wallet():
    # generate a random signing key
    signing_key = SigningKey.generate()
    pubkey = signing_key.verify_key
    wallet_address = base58.b58encode(pubkey.encode()).decode("utf-8")
    return signing_key, wallet_address


def _sign_in_wallet(client: TestClient, signing_key: SigningKey, wallet_address: str) -> dict:
    # 1. Get nonce
    nonce_resp = client.get(f"/api/auth/nonce?wallet_address={wallet_address}")
    assert nonce_resp.status_code == 200
    nonce = nonce_resp.json()["nonce"]
    
    # 2. Sign message
    message = f"Sign this message to authenticate with ASE. Nonce: {nonce}".encode("utf-8")
    signed = signing_key.sign(message)
    signature = base58.b58encode(signed.signature).decode("utf-8")
    
    # 3. Verify
    verify_resp = client.post(
        "/api/auth/verify",
        json={
            "wallet_address": wallet_address,
            "signature": signature,
            "nonce": nonce
        }
    )
    assert verify_resp.status_code == 200
    return verify_resp.json()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_auth_verify_me_and_logout_revokes_token():
    asyncio.run(init_db())

    with TestClient(app) as client:
        signing_key, wallet_address = _generate_wallet()
        auth = _sign_in_wallet(client, signing_key, wallet_address)
        token = auth["access_token"]

        me_before_logout = client.get("/api/auth/me", headers=_auth_headers(token))
        assert me_before_logout.status_code == 200
        assert me_before_logout.json()["wallet_address"] == wallet_address

        logout = client.post("/api/auth/logout", headers=_auth_headers(token))
        assert logout.status_code == 200

        me_after_logout = client.get("/api/auth/me", headers=_auth_headers(token))
        assert me_after_logout.status_code == 401


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

        signing_key, wallet_address = _generate_wallet()
        auth = _sign_in_wallet(client, signing_key, wallet_address)

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
        owner_key, owner_wallet = _generate_wallet()
        other_key, other_wallet = _generate_wallet()
        
        owner_auth = _sign_in_wallet(client, owner_key, owner_wallet)
        other_auth = _sign_in_wallet(client, other_key, other_wallet)

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
