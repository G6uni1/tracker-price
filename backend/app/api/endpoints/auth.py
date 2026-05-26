from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from ...core import security
from ...core.database import get_db
from ...schemas.user import UserCreate, Token
from ...models.user import User
from ...models.notification_settings import NotificationSettings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verifica se email já existe
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    await db.flush()
    # Cria configuração padrão de notificações
    notif = NotificationSettings(user_id=user.id)
    db.add(notif)
    await db.commit()
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)

@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = security.create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)