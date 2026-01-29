from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

# Chat schemas
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
    allowed_mentions: Optional[List[Any]] = None
    cleanup_emojis: bool
    max_emoji_count: int = 0
    cleanup_links: bool
    allowed_link_domains: Optional[List[Any]] = None
    cleanup_emails: bool = False

class ChatUpdate(BaseModel):
    enable_ai_check: Optional[bool] = None
    prompts_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    custom_prompt_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    cleanup_mentions: Optional[bool] = None
    allowed_mentions: Optional[List[Any]] = None
    cleanup_emojis: Optional[bool] = None
    max_emoji_count: Optional[int] = None
    cleanup_links: Optional[bool] = None
    allowed_link_domains: Optional[List[Any]] = None
    cleanup_emails: Optional[bool] = None

class ChatList(BaseModel):
    chats: List[ChatResponse]
