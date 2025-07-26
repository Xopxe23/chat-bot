from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatMessage, ChatSession
from app.chat.schemas import ChatMessageSchema, ChatSessionSchema
from app.common.repositories import BaseRepository
from app.database.pg_client import get_db


class ChatSessionRepository(BaseRepository[ChatSession, ChatSessionSchema]):
    model = ChatSession
    schema = ChatSessionSchema


def get_chat_repository(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> ChatSessionRepository:
    return ChatSessionRepository(session)


class ChatMessageRepository(BaseRepository[ChatMessage, ChatMessageSchema]):
    model = ChatMessage
    schema = ChatMessageSchema


def get_message_repository(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> ChatMessageRepository:
    return ChatMessageRepository(session)
