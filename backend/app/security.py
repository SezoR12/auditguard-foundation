from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_ctx.verify(p, h)

def _encode(sub: str, role: str, minutes: int, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub, "role": role, "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_access_token(user_id: str, role: str) -> str:
    return _encode(user_id, role, settings.ACCESS_TOKEN_MINUTES, "access")

def create_refresh_token(user_id: str, role: str) -> str:
    return _encode(user_id, role, settings.REFRESH_TOKEN_DAYS * 24 * 60, "refresh")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])

__all__ = ["hash_password", "verify_password", "create_access_token",
           "create_refresh_token", "decode_token", "JWTError"]