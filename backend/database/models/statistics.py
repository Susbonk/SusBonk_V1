from sqlalchemy import (
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# TODO: Think if it's needed for backend or just keep it for admin only
class RuntimeStatistics(Base):
    __tablename__ = "runtime_statistics"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="runtime_statistics_pkey"),
        UniqueConstraint("name", name="runtime_statistics_name_key"),
        Index("runtime_statistics_is_active_cb249a2e", "is_active"),
        Index("runtime_statistics_name_44aec854_like", "name"),
    )

    messages_checked: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_requests_made: Mapped[int] = mapped_column(Integer, nullable=False)
    messages_deleted: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
