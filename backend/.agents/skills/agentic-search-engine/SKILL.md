---
name: agentic-search-engine
description: AI Agent Search Engine skills. Use when you need to index your own platform or find wallets and other skills for AI agents.
---

# Agentic Search Engine

Official skill file for interacting with the AI Agent Search Engine.
This service indexes AI agent platforms and supports semantic retrieval over their capabilities.

## Sync Rule

Keep this file in sync with live API contracts.
Whenever request payloads, query params, or response fields change for agent-facing routes, update this file in the same change.

## Base URL

**Production**: `https://api.ase.penivera.me`
**Development**: `http://localhost:8000`
**Local**: `http://localhost:8000`

All API routes are prefixed with `/api`.

## Agent Flow

1. Create a user account via `/api/auth/register`.
2. Verify the user with OTP via `/api/auth/verify-otp` to receive a JWT.
3. Publish a platform on behalf of that verified user via `/api/platforms/` with `Authorization: Bearer <jwt>`.
4. Add capabilities directly via `/api/skills/` using the same JWT, or queue ingestion via `/api/platforms/{platform_id}/ingest`.
5. Search with `/api/search/` and use returned `platform_id` and `skill_md_url`.
6. Call `/api/skills/{platform_id}` to fetch full capability text for a chosen result.

## Endpoints

### 1. Register User (Start OTP Flow)

Create a user account and trigger OTP delivery.

**Endpoint**: `POST /api/auth/register`
**Payload**:

```json
{
  "email": "owner@example.com",
  "password": "strong-password-123"
}
```

**Success Response (200)**:

```json
{
  "message": "Verification code sent",
  "verification_required": true,
  "email": "owner@example.com",
  "otp_expires_in_seconds": 600,
  "dev_otp": "123456"
}
```

`dev_otp` appears only when backend debug OTP exposure is enabled.

### 2. Verify OTP (Get JWT)

Verify the user and get an access token.

**Endpoint**: `POST /api/auth/verify-otp`
**Payload**:

```json
{
  "email": "owner@example.com",
  "otp_code": "123456"
}
```

**Success Response (200)**:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_at": "2026-04-01T12:00:00+00:00",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "owner@example.com"
  }
}
```

### 3. Register a New Platform

Use this endpoint to register a new platform or agent application into the index.

**Endpoint**: `POST /api/platforms/`
**Auth Header**: `Authorization: Bearer <jwt>`
**Payload**:

```json
{
  "name": "My Agent App",
  "url": "https://my-agent.example.com",
  "homepage_uri": "https://my-agent.example.com/home",
  "description": "Optional description of what this platform does.",
  "skills_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md"
}
```

`skills_url` is optional, but recommended. If provided, search results return this exact value in `skill_md_url`.

**Success Response (200)**:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Agent App",
  "skills_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md",
  "message": "Platform created successfully. Crawler dispatched to discover skills and analyze the webpage."
}
```

### 4. Queue Skill Ingestion

Use this endpoint to trigger crawling/ingestion for a registered platform.

**Endpoint**: `POST /api/platforms/{platform_id}/ingest`

**Query Params**:

- `skills_url` (optional string): Temporary override for this ingest run. If omitted, the service uses the platform's stored `skills_url`.

**Success Response (200)**:

```json
{
  "message": "Ingestion task queued.",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses**:

- `400` invalid `platform_id` format
- `404` platform not found

### 5. Register a Skill

Use this endpoint to add capability text directly to a registered platform. Embeddings are generated automatically.

**Endpoint**: `POST /api/skills/`
**Auth Header**: `Authorization: Bearer <jwt>` (or ingest token when configured)
**Payload**:

```json
{
  "platform_id": "<UUID of the registered platform>",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto."
}
```

**Success Response (200)**:

```json
{
  "id": "5f3cc2f2-2d2c-4f0d-a0d7-3f3f5f888111",
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto.",
  "message": "Skill ingested successfully"
}
```

### 6. Search for Skills

Use this endpoint to semantically search for platforms matching the capability you need.

**Endpoint**: `GET /api/search/`
**Query Parameters**:

- `query` (string): The description of the skill you are looking for.
- `top_k` (integer, optional): Number of results to return. Range `1..50`, default `5`.

**Example Request**:
`GET /api/search/?query=wallets%20for%20ai%20agents&top_k=3`

**Example Response**:

```json
[
  {
    "platform_name": "My Agent App",
    "platform_description": "Optional description of what this platform does.",
    "platform_id": "123e4567-e89b-12d3-a456-426614174000",
    "skill": "Supports managing wallets for AI agents...",
    "similarity": 0.85,
    "skill_md_url": "https://my-agent.example.com/.agents/skills/agentic-search-engine/SKILL.md"
  }
]
```

`skill_md_url` comes from the platform's registered `skills_url` and may be `null` if it was not provided.

### 7. Get Full Skill Details for a Platform

Use this endpoint after search to retrieve full capabilities text for a selected platform.

**Endpoint**: `GET /api/skills/{platform_id}`

**Success Response (200, found)**:

```json
{
  "platform_id": "123e4567-e89b-12d3-a456-426614174000",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto.",
  "created_at": "2026-03-25T11:10:00.000000"
}
```

**Success Response (200, not found in index yet)**:

```json
{
  "status": "not_found",
  "message": "We do not have a skill file for this platform yet. You can request it to be indexed via the /platforms endpoint."
}
```

## Ownership Notes

- `POST /api/platforms/` always creates the platform under the authenticated user.
- `PUT /api/platforms/{platform_id}` is restricted to that platform owner.
- If login fails with `Email not verified. Verify OTP first.`, complete `/api/auth/verify-otp` before publishing.
