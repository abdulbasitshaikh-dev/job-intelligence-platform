from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.exceptions import DuplicateResourceException, NotFoundException, PermissionDeniedException
from app.database import get_db
from app.models.application import JobApplication
from app.models.job import Job
from app.models.user import User
from app.schemas.application import JobApplicationCreate, JobApplicationResponse, JobApplicationUpdate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/applications", tags=["Application Tracking"])


@router.get("", response_model=List[JobApplicationResponse])
async def list_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tracked job applications for current user."""
    stmt = (
        select(JobApplication)
        .options(selectinload(JobApplication.job))
        .where(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.updated_at.desc())
    )
    apps = (await db.execute(stmt)).scalars().all()
    return apps


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_in: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Track application status for a job."""
    job = await db.get(Job, app_in.job_id)
    if not job:
        raise NotFoundException(detail="Job not found")

    stmt = select(JobApplication).where(
        (JobApplication.user_id == current_user.id) & (JobApplication.job_id == app_in.job_id)
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise DuplicateResourceException(detail="Application record already exists for this job")

    application = JobApplication(
        user_id=current_user.id,
        job_id=app_in.job_id,
        status=app_in.status,
        notes=app_in.notes,
        applied_at=app_in.applied_at,
    )
    db.add(application)
    await db.commit()

    # Reload with job relationship
    stmt = (
        select(JobApplication)
        .options(selectinload(JobApplication.job))
        .where(JobApplication.id == application.id)
    )
    return (await db.execute(stmt)).scalars().first()


@router.patch("/{app_id}", response_model=JobApplicationResponse)
async def update_application(
    app_id: int,
    app_in: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update status or notes for tracked job application."""
    stmt = (
        select(JobApplication)
        .options(selectinload(JobApplication.job))
        .where(JobApplication.id == app_id)
    )
    application = (await db.execute(stmt)).scalars().first()
    if not application:
        raise NotFoundException(detail="Application record not found")

    if application.user_id != current_user.id:
        raise PermissionDeniedException(detail="Cannot update application belonging to another user")

    update_data = app_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(application, field, val)

    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{app_id}", response_model=MessageResponse)
async def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove application tracking record."""
    application = await db.get(JobApplication, app_id)
    if not application:
        raise NotFoundException(detail="Application record not found")

    if application.user_id != current_user.id:
        raise PermissionDeniedException(detail="Cannot delete application belonging to another user")

    await db.delete(application)
    await db.commit()
    return MessageResponse(message="Application record deleted")
