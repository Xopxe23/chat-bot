import enum
import uuid
from typing import Optional

from sqlalchemy import JSON, UUID, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.common.models import BaseModelMixin, CreatedAtMixin, UpdatedAtMixin
from app.database import Base


class RoleEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ContentTypeEnum(str, enum.Enum):
    text = "text"
    image_url = "image_url"
    audio = "audio"
    file = "file"


class ChatSession(Base, BaseModelMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "chat_session"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_user.id"),
        nullable=True
    )
    title: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    summaries: Mapped[list["ChatSummary"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class ChatMessage(Base, BaseModelMixin, CreatedAtMixin):
    __tablename__ = "chat_message"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)

    chat: Mapped["ChatSession"] = relationship(back_populates="messages")


class ChatSummary(Base, BaseModelMixin, CreatedAtMixin):
    __tablename__ = "chat_summary"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id", ondelete="CASCADE"))
    summary: Mapped[str] = mapped_column(Text)
    anchor_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    chat: Mapped["ChatSession"] = relationship(back_populates="summaries")
