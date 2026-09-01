from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)
app.include_router(
    api_router,
    prefix = "/api/v1"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/health')
def health_check():
    return {
        "status":"ok",
        "app":settings.app_name
    }