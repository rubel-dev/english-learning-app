from fastapi import APIRouter
from app.modules.admin.routers.listening import router as admin_listening_router

api_router = APIRouter()
api_router.include_router(admin_listening_router)
