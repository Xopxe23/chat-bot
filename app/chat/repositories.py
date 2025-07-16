from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.chat.models import ChatMessage, ChatSession
from app.chat.schemas import ChatMessageSchema, ChatSessionSchema
from app.common.repositories import BaseRepository
from app.database import get_db


class ChatSessionRepository(BaseRepository[ChatSession, ChatSessionSchema]):
    model = ChatSession
    schema = ChatSessionSchema


async def get_chat_repository(
    session: AsyncSession = Depends(get_db)
) -> ChatSessionRepository:
    return ChatSessionRepository(session)


class ChatMessageRepository(BaseRepository[ChatMessage, ChatMessageSchema]):
    model = ChatMessage
    schema = ChatMessageSchema



async def get_message_repository(
    session: AsyncSession = Depends(get_db)
) -> ChatMessageRepository:
    return ChatMessageRepository(session)
