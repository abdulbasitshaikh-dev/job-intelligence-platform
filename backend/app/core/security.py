from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.config import settings
from app.core.exceptions import CredentialsException

ph = PasswordHasher()


def get_password_hash(password: str) -> str:
    """Hash password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    token_type: str = "access",
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT token."""
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": token_type,
    }
    if additional_claims:
        to_encode.update(additional_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Union[str, Any], is_superuser: bool = False) -> str:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(
        subject=subject,
        expires_delta=expires,
        token_type="access",
        additional_claims={"is_superuser": is_superuser},
    )


def create_refresh_token(subject: Union[str, Any]) -> str:
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(subject=subject, expires_delta=expires, token_type="refresh")


def decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Decode and validate JWT token claims."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            raise CredentialsException(detail=f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail="Token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsException(detail="Could not validate credentials")
