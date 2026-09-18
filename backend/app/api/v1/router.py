from fastapi import APIRouter

from app.api.v1 import admin, applications, auth, jobs, preferences, sources, webhooks
from app.schemas.common import PlatformStatsResponse

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(preferences.router)
api_v1_router.include_router(sources.router)
api_v1_router.include_router(jobs.router)
api_v1_router.include_router(applications.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(webhooks.router)

# Top-level platform statistics endpoint
api_v1_router.add_api_route(
    "/stats",
    jobs.get_platform_stats,
    methods=["GET"],
    response_model=PlatformStatsResponse,
    tags=["Platform Stats"],
    summary="Get public high-level platform statistics",
)

