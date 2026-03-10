# Agentic Search Engine

This platform indexes and searches `Skills.md` files from AI-first ecosystems to match capabilities with external agent requests.

## Core Features
- **Ingestion**: Extract and store capabilities from submitted `Skills.md` files.
- **Semantic Search**: Find AI platforms based on their skills and schema capabilities.
- **RESTful API**: Exposes endpoints to query platforms and register new ones.

## Getting Started

### Installation
```bash
# Clone the repo
cd agentic-search-engine
pip install -r requirements.txt
```

### Development Server
```bash
uvicorn main:app --reload
```