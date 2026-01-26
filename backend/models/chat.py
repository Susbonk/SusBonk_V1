from typing import Optional, List, Any
from sqlalchemy import String, Boolean, Integer, Float, BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from core.db_helper import Base

class Chat(Base):
    __tablename__ = "chats"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(16))
    platform_chat_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    chat_link: Mapped[Optional[str]] = mapped_column(String(512))
    
    # AI configuration
    enable_ai_check: Mapped[bool] = mapped_column(Boolean, default=False)
    prompts_threshold: Mapped[float] = mapped_column(Float, default=0.35)
    custom_prompt_threshold: Mapped[float] = mapped_column(Float, default=0.35)
    
    # Cleanup settings
    cleanup_mentions: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_mentions: Mapped[Optional[List[Any]]] = mapped_column(JSONB, default=list)
    cleanup_emojis: Mapped[bool] = mapped_column(Boolean, default=False)
    max_emoji_count: Mapped[int] = mapped_column(Integer, default=0)
    cleanup_links: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_link_domains: Mapped[Optional[List[Any]]] = mapped_column(JSONB, default=list)
    cleanup_emails: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Statistics counters
    processed_messages: Mapped[int] = mapped_column(Integer, default=0)
    spam_detected: Mapped[int] = mapped_column(Integer, default=0)
    messages_deleted: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chats")
    user_states: Mapped[List["UserState"]] = relationship("UserState", back_populates="chat", cascade="all, delete-orphan")
    chat_prompts: Mapped[List["ChatPrompts"]] = relationship("ChatPrompts", back_populates="chat", cascade="all, delete-orphan")
    chat_custom_prompts: Mapped[List["ChatCustomPrompts"]] = relationship("ChatCustomPrompts", back_populates="chat", cascade="all, delete-orphan")
