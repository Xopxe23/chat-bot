import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.auth.schemas import AuthUserSchema
from app.auth.utils import get_current_user
from app.chat.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    get_chat_repository,
    get_message_repository,
)
from app.chat.schemas import ChatMessageSchema, ChatSessionSchema, ChatSessionSchemaWithMessages

router = APIRouter(prefix="/chat", tags=["Chats"])


@router.get("/", response_model=List[ChatSessionSchemaWithMessages])
async def get_user_chats(
        user: Annotated[AuthUserSchema, Depends(get_current_user)],
        chat_repo: Annotated[ChatSessionRepository, Depends(get_chat_repository)],
):
    chats = await chat_repo.get_list(
        user_id=user.id,
        joined=["messages"],
        schema_cls=ChatSessionSchemaWithMessages,
    )
    return chats


@router.post("/", response_model=ChatSessionSchema)
async def create_user_chat(
        user: Annotated[AuthUserSchema, Depends(get_current_user)],
        chat_repo: Annotated[ChatSessionRepository, Depends(get_chat_repository)],
):
    chat = await chat_repo.add(user_id=user.id)
    return chat


@router.get("/{chat_id}/messages", response_model=Page[ChatMessageSchema])
async def get_chat_messages(
        chat_id: uuid.UUID,
        params: Annotated[Params, Depends()],
        message_repo: Annotated[ChatMessageRepository, Depends(get_message_repository)],
):
    limit = params.size
    offset = (params.page - 1) * params.size

    messages = await message_repo.get_list(
        limit=limit,
        offset=offset,
        order_by="created_at decs",
        chat_id=chat_id,
    )
    total = await message_repo.get_total_count(
        chat_id=chat_id,
    )

    return Page.create(
        items=messages,
        total=total,
        params=params
    )
