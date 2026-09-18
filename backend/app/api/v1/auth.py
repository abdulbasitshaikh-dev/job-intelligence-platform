from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import CredentialsException, DuplicateResourceException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.database import get_db
from app.models.user import User, JobPreference
from app.models.notification import NotificationConfig
from app.schemas.common import MessageResponse
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    stmt = select(User).where(User.email == user_in.email)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise DuplicateResourceException(detail="A user with this email already exists")

    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()

    # Create default empty preference & notification config
    pref = JobPreference(
        user_id=user.id,
        keywords=["Python", "FastAPI", "Backend"],
        locations=["Remote", "Pakistan"],
        employment_types=["Full-time"],
        work_modes=["Remote"],
    )
    notif = NotificationConfig(user_id=user.id, email_notifications=True, min_match_score=60)
    db.add(pref)
    db.add(notif)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access + refresh tokens."""
    stmt = select(User).where(User.email == credentials.email)
    user = (await db.execute(stmt)).scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise CredentialsException(detail="Invalid email or password")

    if not user.is_active:
        raise CredentialsException(detail="User account is inactive")

    access_token = create_access_token(subject=user.id, is_superuser=user.is_superuser)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange valid refresh token for a new access token pair."""
    payload = decode_token(req.refresh_token, expected_type="refresh")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise CredentialsException()

    user = await db.get(User, int(user_id_str))
    if not user or not user.is_active:
        raise CredentialsException(detail="User not found or inactive")

    new_access_token = create_access_token(subject=user.id, is_superuser=user.is_superuser)
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user (client clears local token cache)."""
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of currently logged-in user."""
    return current_user
