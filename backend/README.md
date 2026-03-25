# ASE Backend (Agentic Search Engine)

FastAPI backend for ingestion and semantic discovery of `SKILL.md` and `Skills.md` files.

## MVP Capabilities

- Skill ingestion with normalization and duplicate handling.
- Semantic search over stored skill embeddings.
- REST API for platform and skill registration/discovery.
- Basic bearer-token auth for skill registration.
- Query log persistence and hot-query cache.
- OpenAPI docs via FastAPI Swagger UI.

## Run Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional (real transformer embeddings instead of deterministic fallback):

```bash
pip install sentence-transformers==2.7.0
```

Open docs at `/docs`.

## Environment Variables

- `DATABASE_URL` (default: `sqlite:///dev.db`)
- `INGEST_API_TOKENS` (comma-separated bearer tokens, optional)
- `SEARCH_CACHE_TTL_SECONDS` (default: `60`)

If `INGEST_API_TOKENS` is unset, skill registration is open for local development.

## Skills API Contract

Base prefix: `/api/skills`

### `POST /api/skills`
Register a new skill (or ignore duplicates).

Auth:
- `Authorization: Bearer <token>` required only when `INGEST_API_TOKENS` is configured.

Request body:
```json
{
  "platform_id": "uuid",
  "skill_name": "Email Automation",
  "tags": ["email", "notifications"],
  "capabilities": "Can send transactional emails and trigger workflows."
}
```

Response:
```json
{
  "id": "uuid",
  "platform_id": "uuid",
  "skill_name": "Email Automation",
  "tags": ["email", "notifications"],
  "capabilities": "...",
  "created_at": "2026-03-25T12:34:56.000000",
  "message": "Skill ingested successfully"
}
```

### `GET /api/skills`
List skills with pagination.

Query params:
- `limit` (1-100, default 20)
- `offset` (>=0, default 0)

Response shape:
```json
{
  "count": 1,
  "items": [
    {
      "id": "uuid",
      "platform_id": "uuid",
      "skill_name": "Email Automation",
      "tags": ["email"],
      "capabilities": "...",
      "created_at": "2026-03-25T12:34:56.000000"
    }
  ]
}
```

### `GET /api/skills/{skill_id}`
Fetch a single skill by id.

### `GET /api/skills/by-platform/{platform_id}`
Compatibility endpoint to fetch latest skill for a platform.

## Search API

### `GET /api/search?query=...&top_k=5`
Returns semantically matched skills including platform metadata.

Search results include:
- `skill_id`
- `skill_name`
- `tags`
- `platform_name`
- `similarity`

Each search is also persisted in `query_logs` with latency and result count.

## Ingestion Pipeline

### Automatic platform ingestion
- `POST /api/platforms` creates a platform and triggers background crawl.
- `POST /api/platforms/{platform_id}/ingest` retriggers ingestion.

### Directory ingestion helper
`app/ingestion/skills_ingester.py` scans directories for both `SKILL.md` and `Skills.md`.

## Testing

```bash
cd backend
pytest -q
```

## Benchmarking

Use the provided benchmark helper:

```bash
cd backend
python scripts/benchmark_search.py --base-url http://127.0.0.1:8000 --query "email automation" --runs 20
```

Target for scaled MVP: keep p95 search latency under 500ms with representative data.

## Render Deployment Notes

`render.yaml` is configured for Python `3.12.0` and installs dependencies from `backend/requirements.txt`.

If a previous deployment failed due to Rust/maturin build steps (`datalayer-pycrdt`), remove stale dependency references and redeploy with this requirements file.
