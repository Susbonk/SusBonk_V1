from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatSettingsUpdate(BaseModel):
    enable_ai_check: Optional[bool] = None

    cleanup_mentions: Optional[bool] = None
    allowed_mentions: Optional[list] = None

    cleanup_emojis: Optional[bool] = None
    max_emoji_count: Optional[int] = None

    cleanup_links: Optional[bool] = None
    allowed_link_domains: Optional[list] = None

    cleanup_emails: Optional[bool] = None

    min_messages_required: Optional[int] = Field(default=None, ge=0)
    min_observation_minutes: Optional[int] = Field(default=None, ge=0)


class ChatSettingsResponse(BaseModel):
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

    cleanup_mentions: bool
    allowed_mentions: Optional[list] = None

    cleanup_emojis: bool
    max_emoji_count: int

    cleanup_links: bool
    allowed_link_domains: Optional[list] = None

    cleanup_emails: bool

    min_messages_required: Optional[int] = Field(default=None, ge=0)
    min_observation_minutes: Optional[int] = Field(default=None, ge=0)


class ChatsList(BaseModel):
    chats: list[ChatSettingsResponse]
