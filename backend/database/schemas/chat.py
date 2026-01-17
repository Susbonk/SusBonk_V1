from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Chat schemas
class ChatResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    platform_chat_id: int
    title: Optional[str]
    chat_link: Optional[str]
    enable_ai_check: bool
    prompts_threshold: float
    custom_prompt_threshold: float
    cleanup_mentions: bool
    cleanup_emojis: bool
    cleanup_links: bool
    allowed_link_domains: Optional[dict]
    processed_messages: int
    spam_detected: int
    messages_deleted: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ChatUpdate(BaseModel):
    enable_ai_check: Optional[bool] = None
    prompts_threshold: Optional[float] = None
    custom_prompt_threshold: Optional[float] = None
    cleanup_mentions: Optional[bool] = None
    cleanup_emojis: Optional[bool] = None
    cleanup_links: Optional[bool] = None
    allowed_link_domains: Optional[dict] = None

class ChatList(BaseModel):
    items: List[ChatResponse]
    total: int
    page: int
    page_size: int

# User State schemas
class UserStateResponse(BaseModel):
    id: UUID
    chat_id: UUID
    external_user_id: int
    trusted: bool
    joined_at: Optional[datetime]
    valid_messages: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class UserStateUpdate(BaseModel):
    trusted: Optional[bool] = None

class UserStatesList(BaseModel):
    items: List[UserStateResponse]
    total: int
    page: int
    page_size: int
