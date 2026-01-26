from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

# Deleted Messages schemas
class DeletedMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    message_id: str
    chat_id: str
    platform_user_id: str
    content: Optional[str] = None
    timestamp: datetime
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DeletedMessagesList(BaseModel):
    items: List[DeletedMessageResponse]
    limit: int
    offset: int
    total: int
