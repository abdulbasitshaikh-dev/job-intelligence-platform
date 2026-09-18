from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User, JobPreference
from app.schemas.preference import JobPreferenceCreate, JobPreferenceResponse, JobPreferenceUpdate

router = APIRouter(prefix="/preferences", tags=["Job Preferences"])


@router.get("", response_model=JobPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve job preferences for current user."""
    stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
    pref = (await db.execute(stmt)).scalars().first()

    if not pref:
        # Create default preference if none exists
        pref = JobPreference(user_id=current_user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    return pref


@router.put("", response_model=JobPreferenceResponse)
async def update_preferences(
    pref_in: JobPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update job preferences for current user."""
    stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
    pref = (await db.execute(stmt)).scalars().first()

    if not pref:
        pref = JobPreference(user_id=current_user.id)
        db.add(pref)

    update_data = pref_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(pref, field, value)

    await db.commit()
    await db.refresh(pref)
    return pref
