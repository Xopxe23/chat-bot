import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.chat.models import ContentTypeEnum, RoleEnum
from app.common.schemas import OrmModel


class ContentItem(BaseModel):
    type: ContentTypeEnum
    text: Optional[str] = None
    url: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ChatMessageSchema(OrmModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: RoleEnum
    content: List[ContentItem]


class ChatSessionSchema(OrmModel):
    user_id: Optional[uuid.UUID]
    title: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ChatSessionSchemaWithMessages(ChatSessionSchema):
    messages: List[ChatMessageSchema] = Field(default_factory=list)
