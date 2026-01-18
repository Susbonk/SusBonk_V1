from sqlalchemy import Column, String, Boolean, Integer, Float, BigInteger, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.helper import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50))
    email = Column(String(100))
    password_hash = Column(String(255))
    telegram_user_id = Column(BigInteger, unique=True)
    discord_user_id = Column(BigInteger, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    custom_prompts = relationship("CustomPrompt", back_populates="user", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(16), nullable=False)
    platform_chat_id = Column(BigInteger, nullable=False)
    title = Column(String(255))
    chat_link = Column(String(512))
    
    # AI configuration
    enable_ai_check = Column(Boolean, default=False)
    prompts_threshold = Column(Float, default=0.35)
    custom_prompt_threshold = Column(Float, default=0.35)
    
    # Cleanup settings - aligned with Senior backend
    cleanup_mentions = Column(Boolean, default=False)
    allowed_mentions = Column(JSONB, default=list)  # Added - was missing
    
    cleanup_emojis = Column(Boolean, default=False)
    max_emoji_count = Column(Integer, default=0)  # Added - was missing
    
    cleanup_links = Column(Boolean, default=False)
    allowed_link_domains = Column(JSONB, default=list)  # JSONB stores as list
    
    cleanup_emails = Column(Boolean, default=False)  # Added - was missing
    
    # Statistics (Junior-specific, kept for backward compatibility)
    processed_messages = Column(Integer, default=0)
    spam_detected = Column(Integer, default=0)
    messages_deleted = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    user_states = relationship("UserState", back_populates="chat", cascade="all, delete-orphan")

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    prompt_text = Column(Text, nullable=False)  # Required like Senior
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class CustomPrompt(Base):
    __tablename__ = "custom_prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100))
    prompt_text = Column(Text, nullable=False)  # Required like Senior
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="custom_prompts")

class UserState(Base):
    __tablename__ = "user_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    external_user_id = Column(BigInteger, nullable=False)
    trusted = Column(Boolean, default=False)
    joined_at = Column(TIMESTAMP)
    valid_messages = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="user_states")
