import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi_pagination import Page, Params

from app.auth.schemas import AuthUserSchema
from app.auth.utils import get_current_user, parse_token
from app.chat.schemas import ChatMessageSchema, ChatSessionSchema, ChatSessionSchemaWithMessages
from app.chat.services import ChatService, get_chat_service
from app.managers.connections import ConnectionManager, get_ws_manager

router = APIRouter(prefix="/chat", tags=["Chats"])


@router.get("/", response_model=List[ChatSessionSchemaWithMessages])
async def get_user_chats(
        user: Annotated[AuthUserSchema, Depends(get_current_user)],
        chat_serv: Annotated[ChatService, Depends(get_chat_service)],
):
    chats = await chat_serv.chat_repo.get_list(
        user_id=user.id,
        joined=["messages"],
        schema_cls=ChatSessionSchemaWithMessages,
    )
    return chats


@router.post("/", response_model=ChatSessionSchema)
async def create_user_chat(
        user: Annotated[AuthUserSchema, Depends(get_current_user)],
        chat_serv: Annotated[ChatService, Depends(get_chat_service)],
):
    chat = await chat_serv.chat_repo.add(user_id=user.id)
    return chat


@router.get("/{chat_id}/messages", response_model=Page[ChatMessageSchema])
async def get_chat_messages(
        chat_id: uuid.UUID,
        params: Annotated[Params, Depends()],
        chat_serv: Annotated[ChatService, Depends(get_chat_service)],
):
    limit = params.size
    offset = (params.page - 1) * params.size

    messages = await chat_serv.message_repo.get_list(
        limit=limit,
        offset=offset,
        order_by="created_at desc",
        chat_id=chat_id,
    )
    total = await chat_serv.message_repo.get_total_count(
        chat_id=chat_id,
    )

    return Page.create(
        items=messages,
        total=total,
        params=params
    )


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        chat_serv: Annotated[ChatService, Depends(get_chat_service)],
        ws_manager: Annotated[ConnectionManager, Depends(get_ws_manager)],
        token: str = Query(...)
):
    try:
        user_data = parse_token(token)
        user_id = uuid.UUID(user_data["sub"])
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if not (message := data["message"]) or data["type"] != "message":
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                raise

            model = data.get("model")
            chat_id = uuid.UUID(message.get("chat_id"))
            user_content = message.get("content")
            await chat_serv.process_user_message(
                model=model,
                chat_id=chat_id,
                user_content=user_content,
                websocket=websocket,
            )

    except (WebSocketDisconnect, RuntimeError):
        await ws_manager.disconnect(user_id, websocket)
