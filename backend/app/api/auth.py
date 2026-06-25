from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_session
from ..models.user import User
from ..security import (
    verify_password, create_access_token, create_refresh_token,
    decode_token, JWTError,
)
from ..schemas.auth import TokenPair, RefreshIn, UserOut, LoginIn
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

BAD_CREDS = "البريد الإلكتروني أو كلمة المرور غير صحيحة"
BAD_REFRESH = "رمز التحديث غير صالح"

async def _authenticate(session: AsyncSession, email: str, password: str) -> User:
    res = await session.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail=BAD_CREDS)
    return user

@router.post("/login", response_model=TokenPair)
async def login(form: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session)):
    user = await _authenticate(session, form.username, form.password)
    role = user.role.value
    return TokenPair(
        access_token=create_access_token(str(user.id), role),
        refresh_token=create_refresh_token(str(user.id), role),
    )

@router.post("/login-json", response_model=TokenPair)
async def login_json(body: LoginIn, session: AsyncSession = Depends(get_session)):
    user = await _authenticate(session, body.email, body.password)
    role = user.role.value
    return TokenPair(
        access_token=create_access_token(str(user.id), role),
        refresh_token=create_refresh_token(str(user.id), role),
    )

@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, session: AsyncSession = Depends(get_session)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise JWTError("wrong token type")
        user_id = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail=BAD_REFRESH)
    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail=BAD_REFRESH)
    role = user.role.value
    return TokenPair(
        access_token=create_access_token(str(user.id), role),
        refresh_token=create_refresh_token(str(user.id), role),
    )

@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user