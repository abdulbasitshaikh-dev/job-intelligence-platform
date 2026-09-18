from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
optional_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    """Validate access token and return current authenticated User."""
    payload = decode_token(token, expected_type="access")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise CredentialsException()

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise CredentialsException()

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not user.is_active:
        raise CredentialsException(detail="User inactive or not found")
    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(optional_oauth2),
) -> Optional[User]:
    """Return the current user if authenticated, or None for unauthenticated requests."""
    if not token:
        return None
    try:
        payload = decode_token(token, expected_type="access")
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_id = int(user_id_str)
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        return user if user and user.is_active else None
    except Exception:
        return None


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Enforce admin / superuser authorization boundary."""
    if not current_user.is_superuser:
        raise PermissionDeniedException(detail="Superuser privileges required")
    return current_user
