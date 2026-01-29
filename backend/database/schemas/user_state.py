from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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


class UserStatesList(BaseModel):
    items: list[UserStateResponse]
    limit: int
    offset: int
    total: int


class UserStateUpdate(BaseModel):
    trusted: Optional[bool] = None
