from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Chat schemas - aligned with Senior backend (ChatSettingsResponse)
class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    type: str
    platform_chat_id: int
    
    title: Optional[str] = None
    chat_link: Optional[str] = None
    
    user_id: UUID
    
    enable_ai_check: bool
    prompts_threshold: float
    custom_prompt_threshold: float
    
    cleanup_mentions: bool
    allowed_mentions: Optional[list] = None  # Added - was missing
    
    cleanup_emojis: bool
    max_emoji_count: int = 0  # Added - was missing (default 0)
    
    cleanup_links: bool
    allowed_link_domains: Optional[list] = None  # Fixed - was dict, now list
    
    cleanup_emails: bool = False  # Added - was missing (default False)

class ChatUpdate(BaseModel):
    enable_ai_check: Optional[bool] = None
    
    prompts_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    custom_prompt_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    
    cleanup_mentions: Optional[bool] = None
    allowed_mentions: Optional[list] = None
    
    cleanup_emojis: Optional[bool] = None
    max_emoji_count: Optional[int] = None
    
    cleanup_links: Optional[bool] = None
    allowed_link_domains: Optional[list] = None
    
    cleanup_emails: Optional[bool] = None

class ChatList(BaseModel):
    chats: List[ChatResponse]

# User State schemas - aligned with Senior backend
class UserStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    chat_id: UUID
    external_user_id: int
    
    trusted: bool
    joined_at: Optional[datetime]
    valid_messages: int
    
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserStateUpdate(BaseModel):
    trusted: Optional[bool] = None

class UserStatesList(BaseModel):
    items: List[UserStateResponse]
    limit: int  # Added - was missing
    offset: int  # Added - was missing
    total: int  # Added - was missing
