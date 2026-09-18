from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.database import get_db
from app.models.source import Source
from app.models.user import User
from app.schemas.source import SourceResponse

router = APIRouter(prefix="/sources", tags=["Job Sources"])


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """List available and enabled job discovery sources (publicly accessible)."""
    stmt = select(Source).where(Source.enabled == True).order_by(Source.name)
    results = await db.execute(stmt)
    sources = results.scalars().all()
    return sources

