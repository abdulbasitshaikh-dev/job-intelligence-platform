from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.config import settings
from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic health check")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@router.get("/health/live", summary="Liveness probe")
async def liveness_probe():
    return {"status": "alive"}


@router.get("/health/ready", summary="Readiness probe (PostgreSQL & Redis)")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    db_healthy = False
    redis_healthy = False

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        redis_healthy = True
    except Exception:
        redis_healthy = False

    if db_healthy and redis_healthy:
        return {
            "status": "ready",
            "services": {
                "database": "connected",
                "redis": "connected",
            },
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "services": {
                    "database": "connected" if db_healthy else "disconnected",
                    "redis": "connected" if redis_healthy else "disconnected",
                },
            },
        )
