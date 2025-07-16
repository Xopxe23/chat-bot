import uuid
from typing import List, Tuple

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.chats.models import ChatMessage, ChatSession
from app.chats.schemas import ChatMessageSchema, ChatSessionSchema
from app.common.repositories import BaseRepository
from app.database import get_async_session


class ChatSessionRepository(BaseRepository[ChatSession]):
    model = ChatSession

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_user_chats(self, user_id: uuid.UUID) -> List[ChatSessionSchema]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.updated_at.desc())
        )
        result = await self.get_all(query)
        return [ChatSessionSchema.model_validate(chat) for chat in result]


async def get_chats_repository(
    session: AsyncSession = Depends(get_async_session)
) -> ChatSessionRepository:
    return ChatSessionRepository(session)


class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    async def get_messages_with_pagination(
            self,
            chat_id: uuid.UUID,
            limit: int,
            offset: int
    ) -> Tuple[List[ChatMessageSchema], int]:
        query = (
            select(self.model)
            .where(self.model.chat_id == chat_id)
            .order_by(self.model.created_at)
            .limit(limit)
            .offset(offset)
            .options(selectinload(self.model.contents))
        )
        result = await self.get_all(query)
        messages = [ChatMessageSchema.model_validate(messages) for messages in result]
        count_query = select(func.count()).where(self.model.chat_id == chat_id)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return messages, total


async def get_messages_repository(
    session: AsyncSession = Depends(get_async_session)
) -> ChatMessageRepository:
    return ChatMessageRepository(session)
