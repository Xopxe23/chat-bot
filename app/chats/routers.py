import uuid
from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.chats.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    get_chats_repository,
    get_messages_repository,
)
from app.chats.schemas import ChatMessageSchema, ChatSessionSchema

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("/", response_model=List[ChatSessionSchema])
async def get_user_chats(
    user_id: uuid.UUID,
    chats_repo: ChatSessionRepository = Depends(get_chats_repository)
):
    chats = await chats_repo.get_user_chats(user_id)
    return chats


@router.get("/{chat_id}/messages", response_model=Page[ChatMessageSchema])
async def get_chat_messages(
    chat_id: uuid.UUID,
    params: Params = Depends(),
    messages_repo: ChatMessageRepository = Depends(get_messages_repository),
):
    limit = params.size
    offset = (params.page - 1) * params.size

    messages, total = await messages_repo.get_messages_with_pagination(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )

    return Page.create(
        items=messages,
        total=total,
        params=params
    )
