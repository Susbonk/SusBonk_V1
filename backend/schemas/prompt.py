from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Prompt schemas
class PromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    title: Optional[str] = Field(default=None, validation_alias="name")
    text: str = Field(..., min_length=1, validation_alias="prompt_text")

class PromptList(BaseModel):
    prompts: List[PromptResponse]

# Custom Prompt schemas
class CustomPromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    user_id: Optional[UUID] = None
    title: Optional[str] = Field(default=None, validation_alias="name")
    text: str = Field(..., min_length=1, validation_alias="prompt_text")

class CustomPromptList(BaseModel):
    prompts: List[CustomPromptResponse]

class CustomPromptCreate(BaseModel):
    title: Optional[str] = None
    text: str = Field(..., min_length=1)
    is_active: bool = True

class CustomPromptUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = Field(default=None, min_length=1)
    is_active: Optional[bool] = None
