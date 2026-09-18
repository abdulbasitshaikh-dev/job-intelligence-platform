from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import is_safe_webhook_url
from app.database import get_db
from app.models.notification import NotificationConfig
from app.models.user import JobPreference, User
from app.schemas.notification import NotificationConfigResponse, NotificationConfigUpdate
from app.schemas.preference import JobPreferenceResponse, JobPreferenceUpdate

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


@router.get("/notifications", response_model=NotificationConfigResponse)
async def get_notification_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve notification configuration for current user."""
    stmt = select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    config = (await db.execute(stmt)).scalars().first()

    if not config:
        config = NotificationConfig(
            user_id=current_user.id,
            email_notifications=True,
            min_match_score=60,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return config


@router.put("/notifications", response_model=NotificationConfigResponse)
async def update_notification_config(
    config_in: NotificationConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notification configuration for current user (email, webhook, threshold)."""
    if config_in.webhook_url and not is_safe_webhook_url(config_in.webhook_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or forbidden webhook URL. Internal or non-HTTP(S) addresses are not permitted.",
        )

    stmt = select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    config = (await db.execute(stmt)).scalars().first()

    if not config:
        config = NotificationConfig(user_id=current_user.id)
        db.add(config)

    update_data = config_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config

