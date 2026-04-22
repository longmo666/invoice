from fastapi import APIRouter
from app.api.v1.routers import auth, users, cleaning, admin_cleaning, recognition, admin_recognition, ai_config

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(cleaning.router)
api_router.include_router(admin_cleaning.router)
api_router.include_router(recognition.router)
api_router.include_router(admin_recognition.router)
api_router.include_router(ai_config.router)
