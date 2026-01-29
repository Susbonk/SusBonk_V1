from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Chat-Prompt Link schemas
class ChatPromptLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    chat_id: UUID
    prompt_id: UUID
    priority: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

class ChatPromptLinkCreate(BaseModel):
    prompt_id: UUID
    priority: Optional[int] = None

class ChatPromptLinksList(BaseModel):
    items: List[ChatPromptLinkResponse]
    limit: int
    offset: int
    total: int

# Chat-Custom-Prompt Link schemas
class ChatCustomPromptLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    chat_id: UUID
    custom_prompt_id: UUID
    priority: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

class ChatCustomPromptLinkCreate(BaseModel):
    custom_prompt_id: UUID
    priority: Optional[int] = None

class ChatCustomPromptLinksList(BaseModel):
    items: List[ChatCustomPromptLinkResponse]
    limit: int
    offset: int
    total: int
