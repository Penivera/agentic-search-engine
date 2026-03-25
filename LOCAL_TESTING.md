# Local Development Testing Guide

## Quick Start

Both servers are running and connected:

```bash
# Backend: running on http://localhost:8000
# Frontend: running on http://localhost:5173
```

## Testing the System

### 1. Open Frontend
Navigate to: **http://localhost:5173**

### 2. Test Dual Interface
- Click "I'm an Agent" → View SKILL.md with integration commands
- Click "I'm a Human" → Go to search interface

### 3. Test Search Functionality
1. Go to http://localhost:5173/home
2. Search for any skill (e.g., "search", "email", "wallet")
3. Results will be fetched from your local backend at http://localhost:8000/api/search

### 4. View API Documentation
Visit: **http://localhost:8000/docs**
- Interactive Swagger UI
- Test all endpoints directly
- See request/response formats

### 5. Health Check
```bash
# Check backend status
GET http://localhost:8000/health
# Response: {"status": "ok", "database": "sqlite"}
```

## API Endpoints Available

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health & database type |
| `/api/search` | GET | Search skills (query, top_k params) |
| `/api/skills` | POST | Register new skill |
| `/api/skills` | GET | List all skills |
| `/api/platforms` | POST | Register platform |
| `/api/platforms` | GET | List platforms |
| `/docs` | GET | Swagger API docs |

## Testing Search

Example search request:
```bash
http://localhost:8000/api/search?query=wallet&top_k=5
```

Response format:
```json
[
  {
    "platform_name": "Platform Name",
    "platform_description": "Description",
    "platform_id": "uuid",
    "skill": "Full skill description",
    "similarity": 0.85,
    "skill_md_url": "optional url"
  }
]
```

## Browser Console

Check browser console (F12) for:
- Frontend API calls to backend
- CORS headers validation
- Network requests and responses

## Hot Reload

- **Frontend**: Edit any `.tsx` or `.ts` file → Auto-refreshes
- **Backend**: Edit any Python file → Auto-reloads server

## Stop Servers

Press `Ctrl+C` in either terminal to stop that server.

## Environment Configuration

**Frontend** uses `VITE_API_URL`:
- Dev: `http://localhost:8000/api`
- Production: `https://api.ase.penivera.me/api`

**Backend** uses `DATABASE_URL`:
- Dev: `sqlite:///dev.db`
- Production: `postgresql://...`

---

**Status: ✅ Local Development Environment Ready**
