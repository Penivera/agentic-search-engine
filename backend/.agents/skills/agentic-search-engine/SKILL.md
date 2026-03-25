---
name: agentic-search-engine
description: Discover and publish AI-agent capabilities via semantic search, platform indexing, and skill ingestion APIs.
---

# Agentic Search Engine Integration Skill

Use this skill when an AI agent needs to:

- Discover platforms by capability (semantic search)
- Publish a platform and its skill document
- Ingest/update skill content for indexing

## Service Endpoints

- Production: `https://api.ase.penivera.me`
- FastAPI Cloud deployment: `https://ase-f1e2b8fd.fastapicloud.dev`
- Local: `http://localhost:8000`

API prefix: `/api`

## Authentication Model

Two auth modes are used:

- User JWT (`Authorization: Bearer <jwt>`) for platform ownership routes.
- Optional ingest token list for skill ingest routes when enabled by server config.

Primary JWT flow:

1. `POST /api/auth/register`
2. `POST /api/auth/verify-otp`
3. Use returned `access_token`

## Core Operations

### 1) Publish Platform

`POST /api/platforms/` (JWT required)

Request:

```json
{
  "name": "Knot",
  "url": "https://www.useknot.xyz/",
  "homepage_uri": "https://www.useknot.xyz/",
  "description": "The autonomous wallet for AI agents on Solana. TEE-secured keys, Jupiter trading, policy controls. No private keys exposed.",
  "skills_url": "https://api.useknot.xyz/skill.md"
}
```

### 2) Trigger/Re-trigger Ingestion

`POST /api/platforms/{platform_id}/ingest`

Optional query param:

- `skills_url` (string): one-time override source for skill content.

### 3) Register Skill Directly

`POST /api/skills/`

Request:

```json
{
  "platform_id": "<uuid>",
  "capabilities": "Capability text for embedding and retrieval.",
  "skill_name": "Optional display name",
  "tags": ["optional", "tags"]
}
```

### 4) Discover Platforms by Capability

`GET /api/search/?query=<text>&top_k=<1..50>`

Key response fields:

- `platform_id`
- `platform_name`
- `skill_id`
- `similarity`
- `skill_md_url`

### 5) Retrieve Indexed Skill Content

- `GET /api/skills/by-platform/{platform_id}` (latest skill for platform)
- `GET /api/skills/{skill_id}` (specific skill document)

## Agent Usage Pattern (Recommended)

1. Search first with `GET /api/search/`.
2. Pick high-similarity results.
3. Resolve details via `GET /api/skills/by-platform/{platform_id}`.
4. If missing/outdated, request ingestion for that platform.

## Operational Notes

- `skills_url` should point to a stable markdown capability document.
- Ingestion is asynchronous; polling may be required before skill content appears.
- `PUT /api/platforms/{platform_id}` is owner-restricted.

## Public Capability Document

- `GET /skill.md`

This endpoint returns a markdown skill document for agent crawlers and registries.
