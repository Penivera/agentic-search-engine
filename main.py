from fastapi import FastAPI

# Initialize the application
app = FastAPI()

@app.get('/')
async def root():
    return {"message": "API running with integrated FastAPI skill"}

# Add future routes from `api/routes.py`
from api.routes import router

# Register API routes
app.include_router(router, prefix="/api")