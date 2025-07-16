import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from app.chats.models import ContentTypeEnum, RoleEnum


class ChatMessageContentSchema(BaseModel):
    id: uuid.UUID
    type: ContentTypeEnum
    text: Optional[str]
    url: Optional[str]
    meta: Optional[dict]

    class Config:
        from_attributes = True


class ChatMessageSchema(BaseModel):
    id: uuid.UUID
    role: RoleEnum
    created_at: datetime.datetime
    contents: List[ChatMessageContentSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    title: Optional[str]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List[ChatMessageSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True
