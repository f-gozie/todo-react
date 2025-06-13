from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.redis_client import redis_client
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin, Token, TokenRefresh, UserRead

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
user_repo = UserRepository()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, session: AsyncSession = Depends(get_db_session)):
    existing = await user_repo.get_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(payload.password)
    user = await user_repo.create(session, {"email": payload.email, "hashed_password": hashed})
    await session.commit()
    return UserRead.model_validate(user)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_db_session)):
    user = await user_repo.get_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: TokenRefresh):
    try:
        payload_data = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Check blacklist
    is_blacklisted = await redis_client.get(f"bl:{payload.refresh_token}")
    if is_blacklisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    user_id = int(payload_data["sub"])
    # Revoke old refresh token
    exp_ts = payload_data["exp"]
    ttl = exp_ts - int(datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await redis_client.setex(f"bl:{payload.refresh_token}", ttl, "revoked")

    # Issue new tokens
    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    return Token(access_token=new_access, refresh_token=new_refresh)


# ---------------------------------------------------------------------------
# Utility dependency
# ---------------------------------------------------------------------------


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db_session)):
    try:
        payload = decode_token(token, expected_type="access")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(payload["sub"])
    from app.repositories.user import UserRepository

    user = await user_repo.get(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user 