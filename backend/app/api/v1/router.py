from fastapi import APIRouter

from app.api.v1 import admin, applications, auth, jobs, preferences, sources, webhooks

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(preferences.router)
api_v1_router.include_router(sources.router)
api_v1_router.include_router(jobs.router)
api_v1_router.include_router(applications.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(webhooks.router)
