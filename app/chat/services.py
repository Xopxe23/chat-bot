import asyncio
import json
from typing import Annotated, AsyncGenerator

import httpx
from fastapi import Depends

from app.chat.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    get_chat_repository,
    get_message_repository,
)
from app.config.main import settings


class ChatService:
    def __init__(
            self,
            chat_repo: ChatSessionRepository,
            message_repo: ChatMessageRepository,
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.client = httpx.AsyncClient(
            base_url=settings.security.OPENAI_URL,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {settings.security.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
        )

    async def stream_chat_completion(self, prompt: str) -> AsyncGenerator[str, None]:
        payload = {
            "model": "gpt-4",
            "stream": True,
            "messages": [
                {"role": "user", "content": prompt}
            ],
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

    async def close_client(self):
        await self.client.aclose()


def get_chat_service(
        chat_repo: Annotated[ChatSessionRepository, Depends(get_chat_repository)],
        message_repo: Annotated[ChatMessageRepository, Depends(get_message_repository)],
) -> ChatService:
    return ChatService(chat_repo, message_repo)
