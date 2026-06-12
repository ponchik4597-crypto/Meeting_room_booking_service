from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, password_hash
from app.db.session import get_db
from app.user.models import User
from app.user.schemas import Token, UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_db)):
    """Эндпоинт для регистрации нового пользователя"""
    stmt = select(User).where(func.lower(User.login) == user_in.login.lower())
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с логином '{user_in.login}' уже существует",
        )

    new_user = User(
        login=user_in.login,
        hashed_password=password_hash.hash(user_in.password),
        role=user_in.role,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """Эндпоинт для аутентификации пользователя и получения JWT-токена"""
    statement = select(User).where(func.lower(User.login) == form_data.username.lower())
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user or not password_hash.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": user.login, "role": user.role}
    access_token = create_access_token(data=token_data)
    return Token(access_token=access_token, token_type="bearer")
