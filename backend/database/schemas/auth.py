from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    username: Optional[str]
    email: Optional[str]
    telegram_user_id: Optional[int]
    discord_user_id: Optional[int]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
