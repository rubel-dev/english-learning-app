from fastapi import FastAPI
from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.assessment_service import router as assessment_router
from app.api.routes.admin_reading import router as admin_reading_router
from app.api.routes.reading import router as reading_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.vocabulary import router as vocabulary_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(assessment_router)
app.include_router(admin_reading_router)
app.include_router(reading_router)
app.include_router(vocabulary_router)
@app.get('/health')
def health_check():
    return {
        "status":"ok",
        "app":settings.app_name
    }