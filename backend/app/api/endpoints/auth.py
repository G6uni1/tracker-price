# backend/app/api/endpoints/auth.py — VERSÃO CORRIGIDA COMPLETA
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core import security
from ...core.database import get_db
from ...core.rate_limit import limiter
from ...models.notification_settings import NotificationSettings
from ...models.user import User
from ...schemas.user import Token, UserCreate

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.flush()

    notif = NotificationSettings(user_id=user.id)
    db.add(notif)
    await db.commit()

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not security.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)