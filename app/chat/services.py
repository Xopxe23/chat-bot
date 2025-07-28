import asyncio
import json
import uuid
from enum import Enum
from typing import Annotated, Any, AsyncGenerator, Dict, List

import httpx
from fastapi import Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.chat.models import RoleEnum
from app.chat.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    get_chat_repository,
    get_message_repository,
)
from app.database.redis_client import RedisChatCache, get_redis_cache
from app.managers.client import get_http_client


class ChatService:
    def __init__(
            self,
            chat_repo: ChatSessionRepository,
            message_repo: ChatMessageRepository,
            cache_repo: RedisChatCache,
            client: httpx.AsyncClient,
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.cache_repo = cache_repo
        self.client = client

    async def process_user_message(
            self,
            model: str,
            chat_id: uuid.UUID,
            user_content: List[Dict[str, Any]],
            websocket: WebSocket,
    ):
        last_messages = await self._get_last_messages_from_cache(chat_id)
        await self.message_repo.add(
            chat_id=chat_id,
            role=RoleEnum.user,
            content=user_content,
        )
        user_message = {
            "role": "user",
            "content": user_content,
        }
        await self.cache_repo.append_message(chat_id, user_message)
        assistant_content = await self._handle_model_response(
            model,
            last_messages,
            user_message,
            websocket,
        )
        await self.message_repo.add(
            chat_id=chat_id,
            role=RoleEnum.assistant,
            content=assistant_content,
        )
        await self.message_repo.session.commit()
        assistant_message = {
            "role": "assistant",
            "content": assistant_content,
        }
        await self.cache_repo.append_message(chat_id, assistant_message)
        try:
            await websocket.send_json({"type": "end"})
        except (WebSocketDisconnect, RuntimeError) as e:
            if isinstance(e, RuntimeError) and 'close message' not in str(e):
                raise

    async def _handle_model_response(
            self,
            model: str,
            last_messages: List[Dict[str, Any]],
            user_message: Dict[str, Any],
            websocket: WebSocket,
    ) -> List[Dict[str, Any]]:
        match model:
            case "gpt-4":
                full_answer = ""
                openai_messages = last_messages + [user_message]
                try:
                    async for token in self._stream_chat_completion(model, openai_messages):
                        full_answer += token
                        await self._safe_send(websocket, {"type": "token", "content": token})
                    return [{"type": "text", "text": full_answer}]
                except Exception:
                    # логирование ошибки
                    raise
            case _:
                raise ValueError(f"Unsupported model: {model}")

    async def _stream_chat_completion(
            self,
            model: str,
            messages: List,
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": model,
            "stream": True,
            "messages": messages,
        }
        try:
            async with self.client.stream("POST", "chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[len("data: "):].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError):
                            # log
                            continue
        except (httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError) as e:
            # log
            raise RuntimeError(f"OpenAI API error: {e}") from e

    async def _get_last_messages_from_cache(
            self,
            chat_id: uuid.UUID,
    ) -> List[Dict[str, Any]]:
        messages_context = await self.cache_repo.get_last_messages(chat_id, limit=15)
        if not messages_context:
            last_messages = await self.message_repo.get_list(
                limit=15,
                offset=0,
                order_by="created_at desc",
                chat_id=chat_id,
            )
            messages_context = [{
                "role": msg.role.value if isinstance(msg.role, Enum) else msg.role,
                "content": [part.model_dump() for part in msg.content],
            } for msg in reversed(last_messages)]
            await self.cache_repo.set_messages(chat_id, messages_context)
        return messages_context

    @staticmethod
    async def _safe_send(websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except (WebSocketDisconnect, RuntimeError) as e:
            if isinstance(e, RuntimeError) and 'close message' not in str(e):
                raise

    async def close_client(self):
        await self.client.aclose()


def get_chat_service(
        chat_repo: Annotated[ChatSessionRepository, Depends(get_chat_repository)],
        message_repo: Annotated[ChatMessageRepository, Depends(get_message_repository)],
        redis_cache: Annotated[RedisChatCache, Depends(get_redis_cache)],
        client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> ChatService:
    return ChatService(chat_repo, message_repo, redis_cache, client)
