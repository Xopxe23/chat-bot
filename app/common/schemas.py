import uuid
from typing import Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.v1.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int


class OrmModel(BaseModel):
    id: uuid.UUID

    class Config:
        from_attributes = True
