from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    username: Optional[str] = None
    email: Optional[EmailStr] = None

    telegram_user_id: Optional[int] = None
    discord_user_id: Optional[int] = None


class UsersList(BaseModel):
    users: list[UserResponse]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    username: Optional[str] = Field(default=None, max_length=50)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TelegramConnectResponse(BaseModel):
    status: str
    message: str
    bot_link: Optional[str] = None
