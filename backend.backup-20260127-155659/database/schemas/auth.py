from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    
    telegram_user_id: Optional[int] = None
    discord_user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class TelegramConnectResponse(BaseModel):
    status: str  # "pending" or "already_connected"
    message: str
    bot_link: Optional[str] = None
