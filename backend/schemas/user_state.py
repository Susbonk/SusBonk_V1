from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# User State schemas
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
    limit: int
    offset: int
    total: int
