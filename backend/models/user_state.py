from typing import Optional
from sqlalchemy import Boolean, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.db_helper import Base

class UserState(Base):
    __tablename__ = "user_states"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"))
    external_user_id: Mapped[int] = mapped_column(BigInteger)
    trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[Optional[datetime]] = mapped_column()
    valid_messages: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="user_states")
