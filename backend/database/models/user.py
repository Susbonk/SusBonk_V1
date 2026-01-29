from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .chat import Chats
    from .prompt import CustomPrompts


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="users_pkey",
        ),
        UniqueConstraint(
            "discord_user_id",
            name="users_discord_user_id_key",
        ),
        UniqueConstraint(
            "telegram_user_id",
            name="users_telegram_user_id_key",
        ),
        Index(
            "users_is_active_1197087a",
            "is_active",
        ),
    )

    username: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    telegram_user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    discord_user_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    chats: Mapped[list["Chats"]] = relationship("Chats", back_populates="user")
    custom_prompts: Mapped[list["CustomPrompts"]] = relationship(
        "CustomPrompts", back_populates="user"
    )
