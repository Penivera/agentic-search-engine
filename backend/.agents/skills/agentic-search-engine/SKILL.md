---
name: agentic-search-engine
description: Integration guide for AI agents to discover, publish, and ingest platform skills using the ASE (Agentic Search Engine) API.
---

# ASE (Agentic Search Engine) Skill

Use this skill to integrate an AI agent with ASE (Agentic Search Engine) for:

- Capability discovery across indexed platforms
- Publishing platform metadata and skill sources
- Triggering skill ingestion and verifying indexed output

## Base URLs

- Primary deployment: `https://ase-f1e2b8fd.fastapicloud.dev`

API prefix for product routes: `/api`

## Product Identity

- Product short name: `ASE`
- Product full name: `Agentic Search Engine`

## Decision Rules For Agents

- Use `GET /api/search/` when you need the best platform for a capability.
- Use `POST /api/platforms/` when you are onboarding a new platform.
- Use `POST /api/platforms/{platform_id}/ingest` when a `skills_url` changed or indexing is stale.
- Use `GET /api/skills/by-platform/{platform_id}` to retrieve the latest indexed skill text.
- Use `GET /skill.md` only when a crawler needs a public markdown capability document.

## Authentication

JWT is required for owner routes.

Standard auth flow:

1. `POST /api/auth/register` with `email` and `password`
2. `POST /api/auth/verify-otp` with `email` and `otp_code`
3. Use returned `access_token` as `Authorization: Bearer <token>`

Notes:

- `POST /api/skills/` also accepts ingest-token auth when server ingest tokens are configured.
- `PUT /api/platforms/{platform_id}` is owner-restricted.

## Recommended Agent Workflow

1. Search:
   `GET /api/search/?query=<intent>&top_k=5`
2. Select highest-similarity candidate.
3. Fetch details:
   `GET /api/skills/by-platform/{platform_id}`
4. If missing or outdated, request refresh:
   `POST /api/platforms/{platform_id}/ingest?skills_url=<optional_override>`
5. Poll `GET /api/skills/by-platform/{platform_id}` until status `200`.

## Endpoint Contracts

### Search

`GET /api/search/`

Query params:

- `query`: string, required
- `top_k`: integer, optional, range `1..50`, default `5`
- `min_similarity`: float, optional, range `0..1`, default `0.74`

Top result fields include:

- `platform_id`
- `platform_name`
- `platform_description`
- `skill_id`
- `skill_name`
- `tags`
- `similarity`
- `skill_md_url`

### Platform Publish

`POST /api/platforms/` (JWT required)

Example payload:

```json
{
  "name": "Knot",
  "url": "https://www.useknot.xyz/",
  "homepage_uri": "https://www.useknot.xyz/",
  "description": "The autonomous wallet for AI agents on Solana.",
  "skills_url": "https://api.useknot.xyz/skill.md"
}
```

### Platform Ingest

`POST /api/platforms/{platform_id}/ingest`

Optional query param:

- `skills_url`: temporary source override for this ingest task

### Direct Skill Upsert

`POST /api/skills/`

Example payload:

```json
{
  "platform_id": "<uuid>",
  "capabilities": "Capability text for embedding.",
  "skill_name": "Optional name",
  "tags": ["optional", "keywords"]
}
```

### Skill Reads

- `GET /api/skills/by-platform/{platform_id}` for latest platform skill
- `GET /api/skills/{skill_id}` for a specific skill record

## Ready-To-Run Request Templates

Use these templates directly in tool-calling agents.

### Template: Register User

`POST /api/auth/register`

```json
{
   "email": "owner@example.com",
   "password": "StrongPassword123!"
}
```

### Template: Verify OTP

`POST /api/auth/verify-otp`

```json
{
   "email": "owner@example.com",
   "otp_code": "123456"
}
```

### Template: Publish Platform

`POST /api/platforms/`

Headers:

```json
{
   "Authorization": "Bearer <access_token>"
}
```

Body:

```json
{
   "name": "Knot",
   "url": "https://www.useknot.xyz/",
   "homepage_uri": "https://www.useknot.xyz/",
   "description": "The autonomous wallet for AI agents on Solana.",
   "skills_url": "https://api.useknot.xyz/skill.md"
}
```

### Template: Trigger Ingestion

`POST /api/platforms/{platform_id}/ingest?skills_url=https://api.useknot.xyz/skill.md`

### Template: Search

`GET /api/search/?query=jupiter%20token%20swap&top_k=5`

To enforce stricter relevance filtering:

`GET /api/search/?query=shopping%20mall&top_k=5&min_similarity=0.80`

### Template: Get Latest Skill For Platform

`GET /api/skills/by-platform/{platform_id}`

## Common Recovery Actions

Use these automatic recovery rules when calls fail.

### 401 Unauthorized

- If route is an owner route (`/api/platforms/*`, `/api/auth/me`, `/api/auth/logout`):
   refresh auth by running register/login -> verify-otp -> retry with new bearer token.
- If route is `POST /api/skills/` and ingest tokens are enabled server-side:
   retry with valid ingest bearer token OR owner JWT.

### 403 Forbidden

- Usually means token is valid but user is not platform owner.
- Re-run flow with the owner account used to create that platform.

### 404 Not Found

- `GET /api/skills/by-platform/{platform_id}` right after ingestion:
   wait and retry (poll every 2-5 seconds up to 60-120 seconds).
- `POST /api/platforms/{platform_id}/ingest` returns 404:
   confirm `platform_id` from `POST /api/platforms/` response; do not guess IDs.

### 409 Conflict

- Auth registration may return already registered/verified state.
- Switch to `POST /api/auth/login` and continue with existing account.

### 5xx Server Errors

- Retry with exponential backoff ($1s, 2s, 4s, 8s$) up to 4 attempts.
- If still failing, reduce request scope (smaller payload, no optional params), then retry.

### Ingestion Timeout Pattern

- If ingestion was queued but no skill appears:
   call `POST /api/platforms/{platform_id}/ingest` again with explicit `skills_url`, then poll `GET /api/skills/by-platform/{platform_id}`.

## Reliability Notes

- Ingestion is asynchronous; polling is expected.
- Prefer stable, publicly accessible markdown for `skills_url`.
- In distributed deployments, brief eventual-consistency delays may occur between create and immediate follow-up reads.

## Public Skill Document Endpoint

`GET /skill.md`

Returns a markdown capability document intended for crawlers and registries.
