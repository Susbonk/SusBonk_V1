from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import get_current_user
from api.security import create_access_token, hash_password, verify_password
from database import db_helper
from database.models import Users
from database.schemas.users import (
    TelegramConnectResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from settings import settings
from logger import get_logger


log = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
get_session = db_helper.session_getter


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserRegister,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    log.info(f"Processing registration request for user: {payload.email}")
    stmt = select(Users).where(Users.email == payload.email)
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        log.warning(f"Registration failed: Email already registered: {payload.email}")  # noqa: E501
        raise HTTPException(status_code=409, detail="Email already registered")

    user = Users(
        is_active=True,
        email=str(payload.email),
        username=payload.username,
        password_hash=hash_password(payload.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    log.info(f"Successfully registered user: {user.id}")

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    log.info(f"Processing login request for user: {payload.email}")
    stmt = select(Users).where(Users.email == str(payload.email))
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not user.password_hash:
        log.warning(f"Login failed: Invalid credentials for user: {payload.email}")  # noqa: E501
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        log.warning(f"Login failed: Invalid password for user: {payload.email}")  # noqa: E501
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        log.warning(f"Login failed: User account inactive: {payload.email}")
        raise HTTPException(status_code=403, detail="User inactive")

    token = create_access_token(
        sub=user.id,
        ttl_minutes=settings.JWT_ACCESS_TTL_MIN,
    )

    log.info(f"Successfully logged in user: {user.id}")

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Users = Depends(get_current_user),
) -> UserResponse:
    log.debug(f"Retrieving user profile for user: {current_user.id}")
    return UserResponse.model_validate(current_user)


@router.get("/me/connect_telegram", response_model=TelegramConnectResponse)
async def connect_telegram(
    current_user: Users = Depends(get_current_user),
) -> TelegramConnectResponse:
    log.debug(f"Processing Telegram connection for user: {current_user.id}")

    if current_user.telegram_user_id is not None:
        return TelegramConnectResponse(
            status="already_connected",
            message="You are already connected to a Telegram account",
        )
    bot_username = settings.BOT_USERNAME
    bot_link = f"Sent `/start {current_user.id}` to https://t.me/{bot_username}"  # noqa: E501

    return TelegramConnectResponse(
        status="pending",
        message="Click the link to connect your Telegram account",
        bot_link=bot_link,
    )
