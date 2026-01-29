from typing import Optional
from pydantic import BaseModel


class DeletedMessageResponse(BaseModel):
    job_id: str
    chat_id: int
    chat_uuid: str
    platform_user_id: int
    user_state_id: Optional[str] = None
    nickname: Optional[str] = None
    message_text: str
    timestamp: int


class DeletedMessagesList(BaseModel):
    items: list[DeletedMessageResponse]
