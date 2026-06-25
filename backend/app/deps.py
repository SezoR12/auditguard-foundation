from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import get_session, set_session_role
from .security import decode_token, JWTError
from .models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ARABIC_UNAUTH = "بيانات الاعتماد غير صالحة"
ARABIC_FORBIDDEN = "ليس لديك صلاحية الوصول إلى هذا المورد"

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("wrong token type")
        user_id = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail=ARABIC_UNAUTH)
    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail=ARABIC_UNAUTH)
    role = user.role.value if hasattr(user.role, "value") else str(user.role)
    await set_session_role(session, role)
    return user

def require_role(*allowed: str):
    async def _dep(user: User = Depends(get_current_user)) -> User:
        role = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role not in allowed:
            raise HTTPException(status_code=403, detail=ARABIC_FORBIDDEN)
        return user
    return _dep