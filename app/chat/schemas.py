import datetime
import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.chat.models import ContentTypeEnum, RoleEnum
from app.common.schemas import OrmModel


class ImageUrlSchema(BaseModel):
    url: str


class ContentItemSchema(BaseModel):
    type: ContentTypeEnum
    text: Optional[str] = None
    image_url: Optional[ImageUrlSchema] = None
    meta: Optional[Dict[str, Any]] = None


class ChatMessageSchema(OrmModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: RoleEnum
    content: Union[ContentItemSchema, List[ContentItemSchema]]
    created_at: datetime.datetime


class ChatSessionSchema(OrmModel):
    user_id: Optional[uuid.UUID]
    title: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ChatSessionSchemaWithMessages(ChatSessionSchema):
    messages: List[ChatMessageSchema] = Field(default_factory=list)
