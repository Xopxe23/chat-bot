import json
import uuid
from typing import Dict, List

import redis.asyncio as redis

from app.config.main import settings


class RedisChatCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @staticmethod
    def _get_key(chat_id: uuid.UUID) -> str:
        return f"chat:{chat_id}:messages"

    async def set_messages(self, chat_id: uuid.UUID, messages: List[Dict]):
        key = self._get_key(chat_id)
        await self.redis.delete(key)
        if not messages:
            return
        messages_json = [json.dumps(msg, ensure_ascii=False) for msg in messages]
        await self.redis.rpush(key, *messages_json)

    async def append_message(self, chat_id: uuid.UUID, message: Dict):
        key = self._get_key(chat_id)
        message_json = json.dumps(message, ensure_ascii=False)
        await self.redis.rpush(key, message_json)

    async def get_last_messages(self, chat_id: uuid.UUID, limit: int = 15) -> List[Dict]:
        key = self._get_key(chat_id)
        length = await self.redis.llen(key)
        if length == 0:
            return []
        start = max(0, length - limit)
        end = length - 1
        messages_json = await self.redis.lrange(key, start, end)
        return [json.loads(msg) for msg in messages_json]

    async def close(self):
        await self.redis.close()


_redis_client = redis.from_url(settings.database.REDIS_URL, decode_responses=True)


async def get_redis_cache() -> RedisChatCache:
    return RedisChatCache(_redis_client)
