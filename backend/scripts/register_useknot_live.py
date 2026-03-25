import time
import uuid

import requests


BASE_URL = "https://ase-f1e2b8fd.fastapicloud.dev"
USEKNOT_PAYLOAD = {
    "name": "Knot",
    "url": "https://www.useknot.xyz/",
    "homepage_uri": "https://www.useknot.xyz/",
    "description": "The autonomous wallet for AI agents on Solana. TEE-secured keys, Jupiter trading, policy controls. No private keys exposed.",
    "skills_url": "https://api.useknot.xyz/skill.md",
}


def _json_or_none(response: requests.Response):
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return None


def main() -> int:
    email = f"useknot-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"
    session = requests.Session()

    register = session.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": password},
        timeout=30,
    )
    print("EMAIL", email)
    print("REGISTER", register.status_code, register.text[:400])

    token = None
    register_json = _json_or_none(register)
    token = register_json.get("access_token") if register_json else None
    otp = register_json.get("dev_otp") if register_json else None
    if token:
        print("REGISTER_RETURNED_TOKEN", True)
    if otp:
        for attempt in range(1, 31):
            verify = session.post(
                f"{BASE_URL}/api/auth/verify-otp",
                json={"email": email, "otp_code": otp},
                timeout=30,
            )
            print(f"VERIFY_ATTEMPT_{attempt}", verify.status_code, verify.text[:400])
            verify_json = _json_or_none(verify)
            token = verify_json.get("access_token") if verify_json else None
            if token:
                break
            time.sleep(1)
    else:
        print("NO_DEV_OTP_IN_RESPONSE")

    print("TOKEN_PRESENT", bool(token))
    if not token:
        return 2

    headers = {"Authorization": f"Bearer {token}"}
    create = session.post(
        f"{BASE_URL}/api/platforms/",
        json=USEKNOT_PAYLOAD,
        headers=headers,
        timeout=30,
    )
    print("CREATE_PLATFORM", create.status_code, create.text[:600])
    create_json = _json_or_none(create)
    platform_id = create_json.get("id") if create_json else None
    if not platform_id:
        return 3

    ingest = session.post(
        f"{BASE_URL}/api/platforms/{platform_id}/ingest",
        params={"skills_url": USEKNOT_PAYLOAD["skills_url"]},
        timeout=30,
    )
    print("INGEST", ingest.status_code, ingest.text[:300])

    for i in range(20):
        time.sleep(2)
        skill = session.get(
            f"{BASE_URL}/api/skills/by-platform/{platform_id}",
            timeout=30,
        )
        print("POLL", i + 1, skill.status_code)
        if skill.status_code == 200:
            skill_json = _json_or_none(skill) or {}
            print("PLATFORM_ID", skill_json.get("platform_id"))
            print("SKILL_NAME", skill_json.get("skill_name"))
            print("TAGS", skill_json.get("tags"))
            preview = (skill_json.get("capabilities") or "")[:350].replace("\n", " ")
            print("CAPABILITIES_PREVIEW", preview)
            return 0

    return 4


if __name__ == "__main__":
    raise SystemExit(main())
