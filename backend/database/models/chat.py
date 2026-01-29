from typing import TYPE_CHECKING, Optional
import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Users
    from .prompt import CustomPrompts, Prompts


class Chats(Base):
    __tablename__ = "chats"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            deferrable=True,
            initially="DEFERRED",
            name="chats_user_id_7dbaf5bc_fk_users_id",
        ),
        PrimaryKeyConstraint("id", name="chats_pkey"),
        UniqueConstraint(
            "type", "platform_chat_id", name="uk_chats_type_platform_chat_id"
        ),
        Index("chats_is_active_fb349602", "is_active"),
        Index("chats_user_id_7dbaf5bc", "user_id"),
    )

    type: Mapped[str] = mapped_column(String(16), nullable=False)
    platform_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    enable_ai_check: Mapped[bool] = mapped_column(Boolean, nullable=False)

    cleanup_mentions: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cleanup_emojis: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cleanup_links: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    messages_deleted: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    spam_detected: Mapped[int] = mapped_column(Integer, nullable=False)
    cleanup_emails: Mapped[bool] = mapped_column(Boolean, nullable=False)
    max_emoji_count: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    chat_link: Mapped[Optional[str]] = mapped_column(String(512))
    allowed_link_domains: Mapped[Optional[list]] = mapped_column(JSONB)
    allowed_mentions: Mapped[Optional[list]] = mapped_column(JSONB)

    min_messages_required: Mapped[int] = mapped_column(Integer, nullable=False)
    min_observation_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="chats")
    chat_custom_prompts: Mapped[list["ChatCustomPrompts"]] = relationship(
        "ChatCustomPrompts", back_populates="chat"
    )
    chat_prompts: Mapped[list["ChatPrompts"]] = relationship(
        "ChatPrompts", back_populates="chat"
    )
    user_states: Mapped[list["UserStates"]] = relationship(
        "UserStates", back_populates="chat"
    )


class ChatCustomPrompts(Base):
    __tablename__ = "chat_custom_prompts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
            deferrable=True,
            initially="DEFERRED",
            name="chat_custom_prompts_chat_id_7b7450b1_fk_chats_id",
        ),
        ForeignKeyConstraint(
            ["custom_prompt_id"],
            ["custom_prompts.id"],
            deferrable=True,
            initially="DEFERRED",
            name="chat_custom_prompts_custom_prompt_id_c060c56e_fk_custom_pr",
        ),
        PrimaryKeyConstraint("id", name="chat_custom_prompts_pkey"),
        UniqueConstraint(
            "chat_id",
            "custom_prompt_id",
            name="uk_chat_custom_prompts_chat_id_custom_prompt_id",
        ),
        Index("chat_custom_prompts_chat_id_7b7450b1", "chat_id"),
        Index(
            "chat_custom_prompts_custom_prompt_id_c060c56e",
            "custom_prompt_id",
        ),
        Index("chat_custom_prompts_is_active_687bb51b", "is_active"),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    custom_prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    priority: Mapped[Optional[int]] = mapped_column(Integer)

    threshold: Mapped[Optional[float]] = mapped_column(Double)

    chat: Mapped["Chats"] = relationship(
        "Chats",
        back_populates="chat_custom_prompts",
    )
    custom_prompt: Mapped["CustomPrompts"] = relationship(
        "CustomPrompts", back_populates="chat_custom_prompts"
    )


class ChatPrompts(Base):
    __tablename__ = "chat_prompts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
            deferrable=True,
            initially="DEFERRED",
            name="chat_prompts_chat_id_58b01d9d_fk_chats_id",
        ),
        ForeignKeyConstraint(
            ["prompt_id"],
            ["prompts.id"],
            deferrable=True,
            initially="DEFERRED",
            name="chat_prompts_prompt_id_85355311_fk_prompts_id",
        ),
        PrimaryKeyConstraint("id", name="chat_prompts_pkey"),
        UniqueConstraint(
            "chat_id", "prompt_id", name="uk_chat_prompts_chat_id_prompt_id"
        ),
        Index("chat_prompts_chat_id_58b01d9d", "chat_id"),
        Index("chat_prompts_is_active_14f801d7", "is_active"),
        Index("chat_prompts_prompt_id_85355311", "prompt_id"),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    prompt_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    priority: Mapped[Optional[int]] = mapped_column(Integer)

    threshold: Mapped[Optional[float]] = mapped_column(Double)

    chat: Mapped["Chats"] = relationship(
        "Chats",
        back_populates="chat_prompts",
    )
    prompt: Mapped["Prompts"] = relationship(
        "Prompts",
        back_populates="chat_prompts",
    )


class UserStates(Base):
    __tablename__ = "user_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
            deferrable=True,
            initially="DEFERRED",
            name="user_states_chat_id_f167116e_fk_chats_id",
        ),
        PrimaryKeyConstraint("id", name="user_states_pkey"),
        Index("idx_user_states_chat_extuser", "chat_id", "external_user_id"),
        Index("user_states_chat_id_f167116e", "chat_id"),
        Index("user_states_is_active_5312b655", "is_active"),
    )

    external_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    trusted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    valid_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))  # noqa: E501

    chat: Mapped["Chats"] = relationship("Chats", back_populates="user_states")
