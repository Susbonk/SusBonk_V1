from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatPromptLinkCreate(BaseModel):
    prompt_id: UUID
    priority: Optional[int] = None
    threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    is_active: bool = True


class ChatCustomPromptLinkCreate(BaseModel):
    custom_prompt_id: UUID
    priority: Optional[int] = None
    threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    is_active: bool = True


class ChatPromptLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    chat_id: UUID
    prompt_id: UUID

    priority: Optional[int] = None
    threshold: float


class ChatCustomPromptLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    chat_id: UUID
    custom_prompt_id: UUID

    priority: Optional[int] = None
    threshold: float


class ChatLinksResponse(BaseModel):
    prompts: list[ChatPromptLinkResponse]
    custom_prompts: list[ChatCustomPromptLinkResponse]
