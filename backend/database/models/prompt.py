from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Users
    from .chat import ChatPrompts, ChatCustomPrompts


class Prompts(Base):
    __tablename__ = "prompts"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prompts_pkey"),
        Index("prompts_is_active_9a1a4767", "is_active"),
    )

    name: Mapped[Optional[str]] = mapped_column(String(100))
    prompt_text: Mapped[Optional[str]] = mapped_column(Text)

    chat_prompts: Mapped[list["ChatPrompts"]] = relationship(
        "ChatPrompts", back_populates="prompt"
    )


class CustomPrompts(Base):
    __tablename__ = "custom_prompts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            deferrable=True,
            initially="DEFERRED",
            name="custom_prompts_user_id_2a2ed8b5_fk_users_id",
        ),
        PrimaryKeyConstraint("id", name="custom_prompts_pkey"),
        Index("custom_prompts_is_active_61d93681", "is_active"),
        Index("custom_prompts_user_id_2a2ed8b5", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    prompt_text: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="custom_prompts",
    )
    chat_custom_prompts: Mapped[list["ChatCustomPrompts"]] = relationship(
        "ChatCustomPrompts", back_populates="custom_prompt"
    )
