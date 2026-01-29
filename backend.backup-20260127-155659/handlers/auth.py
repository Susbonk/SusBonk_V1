from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db_helper import db_helper
from core.security import hash_password, verify_password, create_access_token, get_current_user
from models import User
from schemas.auth import UserRegister, UserLogin, Token, UserResponse, TelegramConnectResponse
import os

router = APIRouter(prefix="/auth", tags=["auth"])

# Get bot username from environment or use default
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "SusBonkBot")

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(db_helper.session_getter)):
    # Check if user exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create token
        access_token = create_access_token({"sub": str(user.id)})
        return Token(access_token=access_token)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(db_helper.session_getter)):
    result = await db.execute(select(User).filter(User.email == credentials.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/connect_telegram", response_model=TelegramConnectResponse)
async def connect_telegram(current_user: User = Depends(get_current_user)):
    """Generate a link for connecting the user's Telegram account."""
    if current_user.telegram_user_id is not None:
        return TelegramConnectResponse(
            status="already_connected",
            message="You are already connected to a Telegram account"
        )
    
    bot_link = f"Send `/start {current_user.id}` to https://t.me/{BOT_USERNAME}"
    
    return TelegramConnectResponse(
        status="pending",
        message="Click the link to connect your Telegram account",
        bot_link=bot_link
    )
