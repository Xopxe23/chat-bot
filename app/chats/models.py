import datetime
import enum
import uuid

from sqlalchemy import JSON, TIMESTAMP, UUID, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.common.models import BaseModelMixin
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


class ChatSession(Base, BaseModelMixin):
    __tablename__ = "chats"

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    summaries: Mapped[list["ChatSummary"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class ChatMessage(Base, BaseModelMixin):
    __tablename__ = "messages"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))

    chat: Mapped["ChatSession"] = relationship(back_populates="messages")
    contents: Mapped[list["ChatMessageContent"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="ChatMessageContent.id"
    )


class ChatMessageContent(Base, BaseModelMixin):
    __tablename__ = "chat_message_content"

    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_message.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[ContentTypeEnum] = mapped_column(Enum(ContentTypeEnum), nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSON)

    message: Mapped["ChatMessage"] = relationship(back_populates="contents")


class ChatSummary(Base, BaseModelMixin):
    __tablename__ = "chat_summary"

    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    anchor_index: Mapped[int | None] = mapped_column(Integer)

    chat: Mapped["ChatSession"] = relationship(back_populates="summaries")
