from fastapi import APIRouter

from app.routers import search, platforms, skills, owners, auth

api_router = APIRouter(prefix="/api")
api_router.include_router(search.router)
api_router.include_router(platforms.router)
api_router.include_router(skills.router)
api_router.include_router(owners.router)
api_router.include_router(auth.router)
