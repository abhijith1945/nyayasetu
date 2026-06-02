"""
Authentication utilities: JWT token generation, password hashing, verification.
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error("Password hashing error: %s", str(e))
        raise


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception as e:
        logger.error("Password verification error: %s", str(e))
        return False


def create_jwt_token(user_id: str, role: str, email: str = "") -> str:
    """Create JWT token with user info."""
    try:
        payload = {
            "user_id": user_id,
            "role": role,
            "email": email,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error("JWT creation error: %s", str(e))
        raise


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("JWT token invalid: %s", str(e))
        return None
    except Exception as e:
        logger.error("JWT verification error: %s", str(e))
        return None


async def get_current_user(credentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to extract and verify JWT from Authorization header."""
    token = credentials.credentials
    
    # Demo mode: accept demo tokens
    if token.startswith('demo-officer-token-'):
        return {
            'user_id': 'demo-officer-user',
            'role': 'officer',
            'email': 'demo-officer@nyayasetu.local'
        }

    if token.startswith('demo-token-'):
        return {
            'user_id': 'demo-user',
            'role': 'citizen',
            'email': 'demo@nyayasetu.local'
        }
    
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_optional(credentials: Optional[Dict[str, Any]] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Optional dependency — returns payload or None if no token."""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload


def require_role(required_role: str):
    """Dependency factory to check user role."""
    async def check_role(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires role '{required_role}'",
            )
        return user
    
    return check_role


def require_roles(*allowed_roles: str):
    """Dependency factory to check if user has one of allowed roles."""
    async def check_roles(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            roles_str = ", ".join(allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of roles: {roles_str}",
            )
        return user
    
    return check_roles
