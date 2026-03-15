---
name: agentic-search-engine
description: AI Agent Search Engine skills. Use when you need to index your own platform or find wallets and other skills for AI agents.
---

# Agentic Search Engine

Official skill file for interacting with the AI Agent Search Engine.
This application is designed to index AI agent applications, platforms, and their capabilities so that they can be semantically searched.

## Base URL

By default, the application runs locally at `http://localhost:8000`. All API routes are pre-fixed with `/api`.

## Endpoints

### 1. Register a New Platform

Use this endpoint to register a new platform or agent application into the index.

**Endpoint**: `POST /api/platforms/`
**Payload**:

```json
{
  "name": "My Agent App",
  "url": "https://my-agent.example.com",
  "homepage_uri": "https://my-agent.example.com/home",
  "description": "An optional description of what this platform does."
}
```

### 2. Register a Skill

Use this endpoint to add specific capabilities or skills to a registered platform. This will automatically generate vector embeddings for semantic search.

**Endpoint**: `POST /api/skills/`
**Payload**:

```json
{
  "platform_id": "<UUID of the registered platform>",
  "capabilities": "Supports managing wallets for AI agents, processing transactions, and handling crypto."
}
```

### 3. Search for Skills

Use this endpoint to semantically search for platforms that support the capabilities you need (e.g., "wallets for ai agents").

**Endpoint**: `GET /api/search/`
**Query Parameters**:

- `query` (string): The description of the skill you are looking for.
- `top_k` (integer, optional): The number of top results to return (default: 5).

**Example Request**:
`GET /api/search/?query=wallets%20for%20ai%20agents&top_k=3`

**Example Response**:

```json
[
  {
    "skill": "Supports managing wallets for AI agents...",
    "similarity": 0.85,
    "platform_id": "123e4567-e89b-12d3-a456-426614174000"
  }
]
```
