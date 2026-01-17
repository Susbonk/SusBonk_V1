from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Prompt schemas
class PromptResponse(BaseModel):
    id: UUID
    name: Optional[str]
    prompt_text: Optional[str]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class PromptList(BaseModel):
    items: List[PromptResponse]
    total: int
    page: int
    page_size: int

# Custom Prompt schemas
class CustomPromptCreate(BaseModel):
    name: str
    prompt_text: str

class CustomPromptUpdate(BaseModel):
    name: Optional[str] = None
    prompt_text: Optional[str] = None

class CustomPromptResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: Optional[str]
    prompt_text: Optional[str]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class CustomPromptList(BaseModel):
    items: List[CustomPromptResponse]
    total: int
    page: int
    page_size: int
