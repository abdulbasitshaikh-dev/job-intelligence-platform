from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

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


def is_safe_webhook_url(url: Optional[str]) -> bool:
    """Validate webhook URL scheme and prevent SSRF to internal/private networks."""
    if url is None:
        return True
    if not isinstance(url, str) or not url.strip():
        return False

    import ipaddress
    import socket
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        lower_host = hostname.lower()
        if lower_host in ("localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "metadata.google.internal"):
            return False
        if lower_host.endswith((".local", ".internal", ".localhost", ".corp", ".lan", ".home")):
            return False

        try:
            ip = ipaddress.ip_address(lower_host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            # Hostname is a domain; verify resolved IP addresses if resolvable
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for item in addr_info:
                    resolved_ip = ipaddress.ip_address(item[4][0])
                    if resolved_ip.is_private or resolved_ip.is_loopback or resolved_ip.is_link_local or resolved_ip.is_reserved or resolved_ip.is_multicast:
                        return False
            except (socket.gaierror, socket.herror, socket.timeout):
                # If DNS resolution is unavailable (e.g. offline testing or mock host), allow valid domain structure
                if "." not in lower_host:
                    return False
        return True
    except Exception:
        return False

